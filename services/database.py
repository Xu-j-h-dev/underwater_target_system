"""
数据库服务
提供MySQL数据库连接和操作
"""
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
import config
from utils import system_logger

class DatabaseService:
    """数据库服务类"""
    
    def __init__(self):
        """初始化数据库服务"""
        self.config = config.DATABASE_CONFIG
        self._ensure_database_exists()
        self._create_tables()
    
    def _get_connection_without_db(self):
        """获取不指定数据库的连接（用于创建数据库）"""
        return pymysql.connect(
            host=self.config['host'],
            port=self.config['port'],
            user=self.config['user'],
            password=self.config['password'],
            charset=self.config['charset']
        )
    
    def _ensure_database_exists(self):
        """确保数据库存在，不存在则创建"""
        try:
            conn = self._get_connection_without_db()
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']} DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.commit()
            cursor.close()
            conn.close()
            system_logger.info(f"数据库 {self.config['database']} 准备完成")
        except Exception as e:
            system_logger.error(f"创建数据库失败: {str(e)}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        获取数据库连接（上下文管理器）
        
        Yields:
            pymysql.Connection: 数据库连接对象
        """
        conn = None
        try:
            conn = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                charset=self.config['charset'],
                cursorclass=DictCursor
            )
            yield conn
        except Exception as e:
            system_logger.error(f"数据库连接失败: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _create_tables(self):
        """创建数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100),
                    role VARCHAR(20) NOT NULL DEFAULT 'user',
                    status VARCHAR(20) NOT NULL DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_username (username),
                    INDEX idx_role (role)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # 模型表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS models (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    version VARCHAR(50) NOT NULL,
                    file_path VARCHAR(255) NOT NULL,
                    classes TEXT,
                    description TEXT,
                    author VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_name (name),
                    INDEX idx_version (version)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # 登录日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS login_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    username VARCHAR(50),
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(50),
                    status VARCHAR(20),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_username (username),
                    INDEX idx_login_time (login_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # 推理日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inference_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    model_name VARCHAR(100),
                    source_type VARCHAR(50),
                    source_path VARCHAR(255),
                    detections INT DEFAULT 0,
                    inference_time FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_user_id (user_id),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # 训练日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    model_name VARCHAR(100),
                    dataset_path VARCHAR(255),
                    epochs INT,
                    batch_size INT,
                    status VARCHAR(20),
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP NULL,
                    final_map FLOAT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_user_id (user_id),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # 系统日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    level VARCHAR(20),
                    module VARCHAR(50),
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_level (level),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            conn.commit()
            cursor.close()
            system_logger.info("数据库表创建完成")
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            fetch: 是否返回查询结果
            
        Returns:
            查询结果（如果fetch=True）
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                conn.commit()
                last_id = cursor.lastrowid
                cursor.close()
                return last_id
    
    def execute_many(self, query: str, params_list: list):
        """
        批量执行SQL语句
        
        Args:
            query: SQL语句
            params_list: 参数列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            cursor.close()

# 全局数据库实例
db_service = DatabaseService()
