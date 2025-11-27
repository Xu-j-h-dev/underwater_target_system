"""
认证服务
提供用户注册、登录、密码管理等功能
"""
import hashlib
from datetime import datetime
from typing import Optional, Dict, List
from .database import db_service
from utils import auth_logger
import config

class AuthService:
    """认证服务类"""
    
    def __init__(self):
        """初始化认证服务"""
        self._init_default_users()
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """
        密码哈希
        
        Args:
            password: 明文密码
            
        Returns:
            str: 哈希后的密码
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _init_default_users(self):
        """初始化默认用户"""
        try:
            # 检查是否已存在用户
            users = db_service.execute_query("SELECT COUNT(*) as count FROM users")
            if users[0]['count'] == 0:
                # 创建默认用户
                for user_data in config.DEFAULT_USERS:
                    self.register(
                        username=user_data['username'],
                        password=user_data['password'],
                        email=user_data['email'],
                        role=user_data['role']
                    )
                auth_logger.info("默认用户创建完成")
        except Exception as e:
            auth_logger.error(f"初始化默认用户失败: {str(e)}")
    
    def register(self, username: str, password: str, email: str = None, role: str = 'user') -> bool:
        """
        用户注册
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            role: 角色（admin/user）
            
        Returns:
            bool: 注册是否成功
        """
        try:
            # 检查用户名是否已存在
            existing = db_service.execute_query(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )
            if existing:
                auth_logger.warning(f"用户名已存在: {username}")
                return False
            
            # 插入新用户
            hashed_pwd = self._hash_password(password)
            db_service.execute_query(
                "INSERT INTO users (username, password, email, role, status) VALUES (%s, %s, %s, %s, %s)",
                (username, hashed_pwd, email, role, 'active'),
                fetch=False
            )
            auth_logger.info(f"用户注册成功: {username}")
            return True
        except Exception as e:
            auth_logger.error(f"用户注册失败: {str(e)}")
            return False
    
    def login(self, username: str, password: str, ip_address: str = '127.0.0.1') -> Optional[Dict]:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            ip_address: IP地址
            
        Returns:
            Optional[Dict]: 用户信息（登录成功）或 None（登录失败）
        """
        try:
            hashed_pwd = self._hash_password(password)
            user = db_service.execute_query(
                "SELECT * FROM users WHERE username = %s AND password = %s AND status = 'active'",
                (username, hashed_pwd)
            )
            
            if user:
                user_info = user[0]
                # 记录登录日志
                db_service.execute_query(
                    "INSERT INTO login_logs (user_id, username, ip_address, status) VALUES (%s, %s, %s, %s)",
                    (user_info['id'], username, ip_address, 'success'),
                    fetch=False
                )
                auth_logger.info(f"用户登录成功: {username}")
                return user_info
            else:
                # 记录失败日志
                db_service.execute_query(
                    "INSERT INTO login_logs (username, ip_address, status) VALUES (%s, %s, %s)",
                    (username, ip_address, 'failed'),
                    fetch=False
                )
                auth_logger.warning(f"用户登录失败: {username}")
                return None
        except Exception as e:
            auth_logger.error(f"登录异常: {str(e)}")
            return None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            bool: 是否修改成功
        """
        try:
            old_hashed = self._hash_password(old_password)
            user = db_service.execute_query(
                "SELECT id FROM users WHERE id = %s AND password = %s",
                (user_id, old_hashed)
            )
            
            if not user:
                auth_logger.warning(f"旧密码错误: user_id={user_id}")
                return False
            
            new_hashed = self._hash_password(new_password)
            db_service.execute_query(
                "UPDATE users SET password = %s WHERE id = %s",
                (new_hashed, user_id),
                fetch=False
            )
            auth_logger.info(f"密码修改成功: user_id={user_id}")
            return True
        except Exception as e:
            auth_logger.error(f"修改密码失败: {str(e)}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """
        获取所有用户
        
        Returns:
            List[Dict]: 用户列表
        """
        try:
            users = db_service.execute_query("SELECT id, username, email, role, status, created_at FROM users")
            return users or []
        except Exception as e:
            auth_logger.error(f"获取用户列表失败: {str(e)}")
            return []
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段（email, role, status等）
            
        Returns:
            bool: 是否更新成功
        """
        try:
            allowed_fields = ['email', 'role', 'status']
            updates = []
            params = []
            
            for key, value in kwargs.items():
                if key in allowed_fields:
                    updates.append(f"{key} = %s")
                    params.append(value)
            
            if not updates:
                return False
            
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            db_service.execute_query(query, tuple(params), fetch=False)
            auth_logger.info(f"用户信息更新成功: user_id={user_id}")
            return True
        except Exception as e:
            auth_logger.error(f"更新用户信息失败: {str(e)}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            db_service.execute_query("DELETE FROM users WHERE id = %s", (user_id,), fetch=False)
            auth_logger.info(f"用户删除成功: user_id={user_id}")
            return True
        except Exception as e:
            auth_logger.error(f"删除用户失败: {str(e)}")
            return False
    
    def get_login_logs(self, limit: int = 100) -> List[Dict]:
        """
        获取登录日志
        
        Args:
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 登录日志列表
        """
        try:
            logs = db_service.execute_query(
                "SELECT * FROM login_logs ORDER BY login_time DESC LIMIT %s",
                (limit,)
            )
            return logs or []
        except Exception as e:
            auth_logger.error(f"获取登录日志失败: {str(e)}")
            return []

# 全局认证服务实例
auth_service = AuthService()
