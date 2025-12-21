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
    
    def prepare_training(self, base_model: str = None) -> bool:
        """
        准备训练模型
        
        Args:
            base_model: 基础模型路径或名称，如果为None则尝试使用默认模型
            
        Returns:
            bool: 是否准备成功
        """
        try:
            # 如果没有指定模型，尝试使用默认模型或第一个可用模型
            if not base_model:
                from .model_manager import model_manager
                models = model_manager.get_all_models()
                if models:
                    # 使用第一个可用模型
                    base_model = models[0]['file_path']
                    training_logger.info(f"未指定模型，使用可用模型: {base_model}")
                else:
                    # 尝试使用默认模型名称
                    base_model = 'yolov11n.pt'
                    training_logger.warning(f"无可用模型，尝试使用默认模型: {base_model}")
            
            # 如果传入的是文件路径，直接使用
            if Path(base_model).exists():
                model_path = base_model
            else:
                # 否则在models目录中查找
                model_path = config.MODELS_DIR / base_model
                if not model_path.exists():
                    # 尝试自动下载（仅适用于官方预训练模型）
                    training_logger.info(f"本地不存在模型，尝试下载: {base_model}")
                    model_path = base_model
            
            self.model = YOLO(str(model_path))
            training_logger.info(f"训练模型准备完成: {model_path}")
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
            train_path: 训练集路径（相对于dataset_path）
            val_path: 验证集路径（相对于dataset_path）
            
        Returns:
            str: YAML文件路径
        """
        # 确保 class_names是列表且不为空
        if not class_names or not isinstance(class_names, list):
            training_logger.warning("未提供类别名称，使用默认配置")
            class_names = config.YOLO_CONFIG['classes']
        
        # 转换为绝对路径
        dataset_path = Path(dataset_path).resolve()
        
        # 验证数据集目录结构
        train_images_dir = dataset_path / train_path
        val_images_dir = dataset_path / val_path
        
        if not train_images_dir.exists():
            training_logger.error(f"训练集图片目录不存在: {train_images_dir}")
            raise FileNotFoundError(f"训练集图片目录不存在: {train_images_dir}")
        
        if not val_images_dir.exists():
            training_logger.error(f"验证集图片目录不存在: {val_images_dir}")
            raise FileNotFoundError(f"验证集图片目录不存在: {val_images_dir}")
        
        # 清理标注文件中超出范围的类别索引
        self._clean_labels(str(dataset_path), len(class_names) - 1)
        
        # 使用绝对路径创建YAML配置
        yaml_content = {
            'path': str(dataset_path),  # 绝对路径
            'train': train_path,  # 相对路径
            'val': val_path,  # 相对路径
            'nc': len(class_names),
            'names': class_names
        }
        
        yaml_path = dataset_path / 'data.yaml'
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f, allow_unicode=True, default_flow_style=False)
        
        training_logger.info(f"数据集配置文件创建: {yaml_path}")
        training_logger.info(f"数据集路径: {dataset_path}")
        training_logger.info(f"训练集: {train_images_dir}")
        training_logger.info(f"验证集: {val_images_dir}")
        training_logger.info(f"类别数量: {len(class_names)}, 类别: {class_names}")
        return str(yaml_path)
    
    def _clean_labels(self, dataset_path: str, max_class_id: int):
        """
        清理标注文件中超出范围的类别索引
        
        Args:
            dataset_path: 数据集路径
            max_class_id: 最大允许的类别索引
        """
        labels_dir = Path(dataset_path) / 'labels'
        if not labels_dir.exists():
            training_logger.warning(f"标注目录不存在: {labels_dir}")
            return
        
        cleaned_count = 0
        removed_count = 0
        
        for label_file in labels_dir.rglob('*.txt'):
            try:
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) < 5:
                        continue
                    
                    try:
                        class_id = int(parts[0])
                        # 只保留合法范围内的标注
                        if 0 <= class_id <= max_class_id:
                            cleaned_lines.append(line)
                        else:
                            removed_count += 1
                            training_logger.debug(f"移除无效标注: {label_file.name} - class_id={class_id}")
                    except ValueError:
                        continue
                
                # 写回清理后的内容
                if len(cleaned_lines) != len([l for l in lines if l.strip()]):
                    with open(label_file, 'w') as f:
                        f.write('\n'.join(cleaned_lines))
                        if cleaned_lines:
                            f.write('\n')
                    cleaned_count += 1
                    
            except Exception as e:
                training_logger.warning(f"处理标注文件失败 {label_file}: {str(e)}")
        
        if cleaned_count > 0:
            training_logger.info(f"清理了 {cleaned_count} 个标注文件，移除了 {removed_count} 个无效标注")
        else:
            training_logger.info("所有标注文件均合法")
    
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
            
            # 执行训练，添加single_cls参数来处理类别索引问题
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
                verbose=True,
                # 添加以下参数来处理类别索引问题和稳定性
                exist_ok=True,  # 允许覆盖已存在的项目
                pretrained=True,  # 使用预训练权重
                optimizer='SGD',  # 使用SGD优化器（更稳定）
                close_mosaic=10,  # 最后10个epoch关闭mosaic增强
                amp=False  # 关闭自动混合精度（避免NoneType错误）
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
    
    def delete_training_log(self, log_id: int) -> bool:
        """
        删除单条训练日志
        
        Args:
            log_id: 日志ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            db_service.execute_query(
                "DELETE FROM training_logs WHERE id = %s",
                (log_id,),
                fetch=False
            )
            training_logger.info(f"已删除训练日志: {log_id}")
            return True
        except Exception as e:
            training_logger.error(f"删除训练日志失败: {str(e)}")
            return False
    
    def clear_all_training_logs(self, user_id: int) -> bool:
        """
        清空某用户的所有训练日志
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否清空成功
        """
        try:
            db_service.execute_query(
                "DELETE FROM training_logs WHERE user_id = %s",
                (user_id,),
                fetch=False
            )
            training_logger.info(f"已清空用户 {user_id} 的所有训练日志")
            return True
        except Exception as e:
            training_logger.error(f"清空训练日志失败: {str(e)}")
            return False
    
    def save_trained_model(self, weights_path: str, model_name: str, version: str = '1.0',
                          classes: list = None, description: str = None, author: str = None) -> bool:
        """
        保存训练好的模型到模型管理器
        
        Args:
            weights_path: 训练好的模型权重路径
            model_name: 模型名称
            version: 版本号
            classes: 类别列表
            description: 描述
            author: 作者
            
        Returns:
            bool: 是否保存成功
        """
        try:
            from .model_manager import model_manager
            
            # 检查模型文件是否存在
            if not Path(weights_path).exists():
                training_logger.error(f"模型文件不存在: {weights_path}")
                return False
            
            # 注册模型到模型管理器
            success = model_manager.add_model(
                name=model_name,
                version=version,
                file_path=weights_path,
                classes=classes,
                description=description,
                author=author
            )
            
            if success:
                training_logger.info(f"训练模型已保存到模型管理器: {model_name} v{version}")
            else:
                training_logger.error(f"保存模型到模型管理器失败")
            
            return success
            
        except Exception as e:
            training_logger.error(f"保存训练模型失败: {str(e)}")
            return False

# 全局训练服务实例
training_service = TrainingService()
