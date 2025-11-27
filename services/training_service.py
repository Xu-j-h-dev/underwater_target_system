"""
训练服务
提供YOLOv11模型训练功能
"""
from pathlib import Path
from typing import Optional, Dict, Callable
import yaml
from ultralytics import YOLO
from .database import db_service
from utils import training_logger
import config

class TrainingService:
    """训练服务类"""
    
    def __init__(self):
        """初始化训练服务"""
        self.model: Optional[YOLO] = None
        self.is_training = False
        self.should_stop = False
    
    def prepare_training(self, base_model: str = 'yolov11n.pt') -> bool:
        """
        准备训练模型
        
        Args:
            base_model: 基础模型名称
            
        Returns:
            bool: 是否准备成功
        """
        try:
            model_path = config.MODELS_DIR / base_model
            if not model_path.exists():
                # 如果本地不存在，会自动下载
                training_logger.info(f"正在下载模型: {base_model}")
            
            self.model = YOLO(str(model_path))
            training_logger.info(f"训练模型准备完成: {base_model}")
            return True
        except Exception as e:
            training_logger.error(f"准备训练模型失败: {str(e)}")
            return False
    
    def create_dataset_yaml(self, dataset_path: str, class_names: list, 
                           train_path: str, val_path: str) -> str:
        """
        创建数据集配置文件
        
        Args:
            dataset_path: 数据集根路径
            class_names: 类别名称列表
            train_path: 训练集路径
            val_path: 验证集路径
            
        Returns:
            str: YAML文件路径
        """
        yaml_content = {
            'path': dataset_path,
            'train': train_path,
            'val': val_path,
            'names': {i: name for i, name in enumerate(class_names)}
        }
        
        yaml_path = Path(dataset_path) / 'data.yaml'
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f, allow_unicode=True)
        
        training_logger.info(f"数据集配置文件创建: {yaml_path}")
        return str(yaml_path)
    
    def start_training(self, 
                      data_yaml: str,
                      epochs: int = None,
                      batch_size: int = None,
                      img_size: int = None,
                      lr: float = None,
                      project_name: str = 'underwater_training',
                      user_id: int = None,
                      progress_callback: Callable = None) -> Dict:
        """
        开始训练
        
        Args:
            data_yaml: 数据集YAML配置文件路径
            epochs: 训练轮数
            batch_size: 批次大小
            img_size: 图像大小
            lr: 学习率
            project_name: 项目名称
            user_id: 用户ID
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 训练结果
        """
        if self.is_training:
            training_logger.warning("已有训练任务在进行")
            return {'success': False, 'error': '已有训练任务在进行'}
        
        if not self.model:
            training_logger.error("模型未准备")
            return {'success': False, 'error': '模型未准备'}
        
        # 使用配置或默认值
        epochs = epochs or config.TRAINING_CONFIG['epochs']
        batch_size = batch_size or config.TRAINING_CONFIG['batch_size']
        img_size = img_size or config.TRAINING_CONFIG['img_size']
        lr = lr or config.TRAINING_CONFIG['lr']
        
        try:
            self.is_training = True
            self.should_stop = False
            
            # 记录训练开始
            log_id = None
            if user_id:
                log_id = db_service.execute_query(
                    """INSERT INTO training_logs 
                    (user_id, model_name, dataset_path, epochs, batch_size, status) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (user_id, project_name, data_yaml, epochs, batch_size, 'running'),
                    fetch=False
                )
            
            training_logger.info(f"开始训练: {project_name}")
            
            # 执行训练
            results = self.model.train(
                data=data_yaml,
                epochs=epochs,
                batch=batch_size,
                imgsz=img_size,
                lr0=lr,
                project=str(config.MODELS_DIR / 'training'),
                name=project_name,
                device=config.SYSTEM_CONFIG['device'],
                workers=config.TRAINING_CONFIG['workers'],
                patience=config.TRAINING_CONFIG['patience'],
                verbose=True
            )
            
            self.is_training = False
            
            # 获取最终指标
            final_map = float(results.results_dict.get('metrics/mAP50-95(B)', 0))
            
            # 更新训练日志
            if log_id:
                db_service.execute_query(
                    """UPDATE training_logs 
                    SET status = %s, end_time = NOW(), final_map = %s 
                    WHERE id = %s""",
                    ('completed', final_map, log_id),
                    fetch=False
                )
            
            training_logger.info(f"训练完成: {project_name}, mAP: {final_map:.4f}")
            
            return {
                'success': True,
                'results': results,
                'final_map': final_map,
                'weights_path': str(results.save_dir / 'weights' / 'best.pt')
            }
            
        except Exception as e:
            self.is_training = False
            training_logger.error(f"训练失败: {str(e)}")
            
            # 更新失败状态
            if log_id:
                db_service.execute_query(
                    "UPDATE training_logs SET status = %s, end_time = NOW() WHERE id = %s",
                    ('failed', log_id),
                    fetch=False
                )
            
            return {'success': False, 'error': str(e)}
    
    def stop_training(self):
        """停止训练"""
        if self.is_training:
            self.should_stop = True
            training_logger.info("训练停止请求已发送")
    
    def validate_model(self, model_path: str, data_yaml: str) -> Dict:
        """
        验证模型
        
        Args:
            model_path: 模型路径
            data_yaml: 数据集配置
            
        Returns:
            Dict: 验证结果
        """
        try:
            model = YOLO(model_path)
            results = model.val(data=data_yaml)
            
            metrics = {
                'mAP50': float(results.results_dict.get('metrics/mAP50(B)', 0)),
                'mAP50-95': float(results.results_dict.get('metrics/mAP50-95(B)', 0)),
                'precision': float(results.results_dict.get('metrics/precision(B)', 0)),
                'recall': float(results.results_dict.get('metrics/recall(B)', 0))
            }
            
            training_logger.info(f"模型验证完成: {model_path}")
            return {'success': True, 'metrics': metrics}
            
        except Exception as e:
            training_logger.error(f"模型验证失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def export_model(self, model_path: str, format: str = 'onnx') -> Dict:
        """
        导出模型
        
        Args:
            model_path: 模型路径
            format: 导出格式 (onnx, torchscript, etc.)
            
        Returns:
            Dict: 导出结果
        """
        try:
            model = YOLO(model_path)
            export_path = model.export(format=format)
            training_logger.info(f"模型导出成功: {export_path}")
            return {'success': True, 'export_path': str(export_path)}
        except Exception as e:
            training_logger.error(f"模型导出失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_training_logs(self, user_id: int = None, limit: int = 100) -> list:
        """
        获取训练日志
        
        Args:
            user_id: 用户ID（可选）
            limit: 返回数量限制
            
        Returns:
            list: 训练日志列表
        """
        try:
            if user_id:
                logs = db_service.execute_query(
                    "SELECT * FROM training_logs WHERE user_id = %s ORDER BY start_time DESC LIMIT %s",
                    (user_id, limit)
                )
            else:
                logs = db_service.execute_query(
                    "SELECT * FROM training_logs ORDER BY start_time DESC LIMIT %s",
                    (limit,)
                )
            return logs or []
        except Exception as e:
            training_logger.error(f"获取训练日志失败: {str(e)}")
            return []

# 全局训练服务实例
training_service = TrainingService()
