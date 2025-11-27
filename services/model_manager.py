"""
模型管理服务
提供模型的增删改查、版本管理等功能
"""
from pathlib import Path
from typing import List, Dict, Optional
import shutil
import json
from datetime import datetime
from .database import db_service
from utils import system_logger
import config

class ModelManager:
    """模型管理器类"""
    
    def __init__(self):
        """初始化模型管理器"""
        self.models_dir = config.MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def add_model(self, 
                  name: str,
                  version: str,
                  file_path: str,
                  classes: List[str] = None,
                  description: str = None,
                  author: str = None) -> bool:
        """
        添加模型到仓库
        
        Args:
            name: 模型名称
            version: 版本号
            file_path: 模型文件路径
            classes: 类别列表
            description: 描述
            author: 作者
            
        Returns:
            bool: 是否添加成功
        """
        try:
            # 检查文件是否存在
            source_path = Path(file_path)
            if not source_path.exists():
                system_logger.error(f"模型文件不存在: {file_path}")
                return False
            
            # 复制到模型目录
            target_filename = f"{name}_v{version}.pt"
            target_path = self.models_dir / target_filename
            shutil.copy2(source_path, target_path)
            
            # 保存到数据库
            classes_str = json.dumps(classes, ensure_ascii=False) if classes else None
            db_service.execute_query(
                """INSERT INTO models (name, version, file_path, classes, description, author) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (name, version, str(target_path), classes_str, description, author),
                fetch=False
            )
            
            system_logger.info(f"模型添加成功: {name} v{version}")
            return True
            
        except Exception as e:
            system_logger.error(f"添加模型失败: {str(e)}")
            return False
    
    def get_all_models(self) -> List[Dict]:
        """
        获取所有模型
        
        Returns:
            List[Dict]: 模型列表
        """
        try:
            models = db_service.execute_query("SELECT * FROM models ORDER BY created_at DESC")
            
            # 解析classes字段
            for model in models:
                if model.get('classes'):
                    try:
                        model['classes'] = json.loads(model['classes'])
                    except:
                        model['classes'] = []
            
            return models or []
        except Exception as e:
            system_logger.error(f"获取模型列表失败: {str(e)}")
            return []
    
    def get_model_by_id(self, model_id: int) -> Optional[Dict]:
        """
        根据ID获取模型
        
        Args:
            model_id: 模型ID
            
        Returns:
            Optional[Dict]: 模型信息
        """
        try:
            models = db_service.execute_query("SELECT * FROM models WHERE id = %s", (model_id,))
            if models:
                model = models[0]
                if model.get('classes'):
                    try:
                        model['classes'] = json.loads(model['classes'])
                    except:
                        model['classes'] = []
                return model
            return None
        except Exception as e:
            system_logger.error(f"获取模型失败: {str(e)}")
            return None
    
    def get_model_by_name(self, name: str, version: str = None) -> Optional[Dict]:
        """
        根据名称获取模型
        
        Args:
            name: 模型名称
            version: 版本号（可选）
            
        Returns:
            Optional[Dict]: 模型信息
        """
        try:
            if version:
                models = db_service.execute_query(
                    "SELECT * FROM models WHERE name = %s AND version = %s",
                    (name, version)
                )
            else:
                models = db_service.execute_query(
                    "SELECT * FROM models WHERE name = %s ORDER BY created_at DESC LIMIT 1",
                    (name,)
                )
            
            if models:
                model = models[0]
                if model.get('classes'):
                    try:
                        model['classes'] = json.loads(model['classes'])
                    except:
                        model['classes'] = []
                return model
            return None
        except Exception as e:
            system_logger.error(f"获取模型失败: {str(e)}")
            return None
    
    def update_model(self, model_id: int, **kwargs) -> bool:
        """
        更新模型信息
        
        Args:
            model_id: 模型ID
            **kwargs: 要更新的字段
            
        Returns:
            bool: 是否更新成功
        """
        try:
            allowed_fields = ['description', 'author', 'classes']
            updates = []
            params = []
            
            for key, value in kwargs.items():
                if key in allowed_fields:
                    if key == 'classes' and isinstance(value, list):
                        value = json.dumps(value, ensure_ascii=False)
                    updates.append(f"{key} = %s")
                    params.append(value)
            
            if not updates:
                return False
            
            params.append(model_id)
            query = f"UPDATE models SET {', '.join(updates)} WHERE id = %s"
            db_service.execute_query(query, tuple(params), fetch=False)
            
            system_logger.info(f"模型信息更新成功: model_id={model_id}")
            return True
        except Exception as e:
            system_logger.error(f"更新模型信息失败: {str(e)}")
            return False
    
    def delete_model(self, model_id: int, delete_file: bool = True) -> bool:
        """
        删除模型
        
        Args:
            model_id: 模型ID
            delete_file: 是否同时删除文件
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 获取模型信息
            model = self.get_model_by_id(model_id)
            if not model:
                return False
            
            # 删除文件
            if delete_file and model.get('file_path'):
                file_path = Path(model['file_path'])
                if file_path.exists():
                    file_path.unlink()
            
            # 从数据库删除
            db_service.execute_query("DELETE FROM models WHERE id = %s", (model_id,), fetch=False)
            
            system_logger.info(f"模型删除成功: model_id={model_id}")
            return True
        except Exception as e:
            system_logger.error(f"删除模型失败: {str(e)}")
            return False
    
    def search_models(self, keyword: str) -> List[Dict]:
        """
        搜索模型
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            List[Dict]: 匹配的模型列表
        """
        try:
            models = db_service.execute_query(
                """SELECT * FROM models 
                WHERE name LIKE %s OR description LIKE %s OR author LIKE %s
                ORDER BY created_at DESC""",
                (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
            )
            
            for model in models:
                if model.get('classes'):
                    try:
                        model['classes'] = json.loads(model['classes'])
                    except:
                        model['classes'] = []
            
            return models or []
        except Exception as e:
            system_logger.error(f"搜索模型失败: {str(e)}")
            return []
    
    def export_model_info(self, model_id: int, export_path: str) -> bool:
        """
        导出模型信息为JSON
        
        Args:
            model_id: 模型ID
            export_path: 导出路径
            
        Returns:
            bool: 是否导出成功
        """
        try:
            model = self.get_model_by_id(model_id)
            if not model:
                return False
            
            # 转换datetime为字符串
            for key in ['created_at', 'updated_at']:
                if key in model and isinstance(model[key], datetime):
                    model[key] = model[key].strftime('%Y-%m-%d %H:%M:%S')
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(model, f, ensure_ascii=False, indent=2)
            
            system_logger.info(f"模型信息导出成功: {export_path}")
            return True
        except Exception as e:
            system_logger.error(f"导出模型信息失败: {str(e)}")
            return False

# 全局模型管理器实例
model_manager = ModelManager()
