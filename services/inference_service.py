"""
推理服务
提供YOLOv11模型推理功能
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Union
import time
from ultralytics import YOLO
from .database import db_service
from utils import inference_logger
import config

class InferenceEngine:
    """推理引擎类"""
    
    def __init__(self):
        """初始化推理引擎"""
        self.model: Optional[YOLO] = None
        self.current_model_path: Optional[str] = None
        self.conf_threshold = config.YOLO_CONFIG['conf_threshold']
        self.iou_threshold = config.YOLO_CONFIG['iou_threshold']
        self.device = config.SYSTEM_CONFIG['device']
    
    def load_model(self, model_path: str) -> bool:
        """
        加载YOLO模型
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            bool: 是否加载成功
        """
        try:
            # 检查路径
            if not model_path:
                inference_logger.error("模型路径为空")
                return False
            
            model_path_obj = Path(model_path)
            if not model_path_obj.exists():
                inference_logger.error(f"模型文件不存在: {model_path}")
                return False
            
            # 检查文件扩展名
            if model_path_obj.suffix not in ['.pt', '.pth']:
                inference_logger.warning(f"模型文件扩展名不常见: {model_path_obj.suffix}")
            
            # 验证模型文件格式
            try:
                import torch
                ckpt = torch.load(model_path, map_location='cpu', weights_only=False)
                
                # 检查是否是有效的YOLO模型
                if not isinstance(ckpt, dict) or ('model' not in ckpt and 'ema' not in ckpt):
                    inference_logger.error(
                        f"无效的YOLO模型文件: {model_path}\n"
                        f"该文件不包含必需的 'model' 或 'ema' 键。\n"
                        f"实际包含的键: {list(ckpt.keys()) if isinstance(ckpt, dict) else 'Not a dict'}\n"
                        f"这可能不是一个YOLOv11训练的模型文件。"
                    )
                    return False
                    
            except Exception as e:
                inference_logger.error(f"模型文件格式验证失败: {str(e)}")
                return False
            
            inference_logger.info(f"开始加载模型: {model_path}")
            inference_logger.info(f"使用设备: {self.device}")
            
            # 加载模型
            self.model = YOLO(model_path)
            self.current_model_path = model_path
            
            inference_logger.info(f"模型加载成功: {model_path}")
            inference_logger.info(f"模型类型: {type(self.model)}")
            
            # 尝试获取模型信息
            try:
                if hasattr(self.model, 'names'):
                    inference_logger.info(f"模型类别: {self.model.names}")
            except:
                pass
            
            return True
            
        except Exception as e:
            inference_logger.error(f"模型加载失败: {str(e)}")
            inference_logger.exception("详细错误信息:")
            return False
    
    def set_parameters(self, conf_threshold: float = None, iou_threshold: float = None):
        """
        设置推理参数
        
        Args:
            conf_threshold: 置信度阈值
            iou_threshold: NMS阈值
        """
        if conf_threshold is not None:
            self.conf_threshold = conf_threshold
        if iou_threshold is not None:
            self.iou_threshold = iou_threshold
    
    def predict_image(self, image_path: str, save_path: str = None) -> Dict:
        """
        对单张图片进行推理
        
        Args:
            image_path: 图片路径
            save_path: 结果保存路径
            
        Returns:
            Dict: 推理结果
        """
        if not self.model:
            inference_logger.error("模型未加载")
            return {'success': False, 'error': '模型未加载'}
        
        try:
            start_time = time.time()
            
            # 执行推理
            results = self.model.predict(
                source=image_path,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                device=self.device,
                save=False
            )
            
            inference_time = time.time() - start_time
            
            # 解析结果
            detections = []
            img = cv2.imread(image_path)
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls = int(box.cls[0].cpu().numpy())
                    
                    detection = {
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': conf,
                        'class_id': cls,
                        'class_name': result.names[cls]
                    }
                    detections.append(detection)
                    
                    # 绘制检测框
                    if img is not None:
                        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        label = f"{result.names[cls]}: {conf:.2f}"
                        cv2.putText(img, label, (int(x1), int(y1)-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # 保存结果
            if save_path and img is not None:
                cv2.imwrite(save_path, img)
            
            inference_logger.info(f"图片推理完成: {image_path}, 检测数: {len(detections)}, 耗时: {inference_time:.3f}s")
            
            return {
                'success': True,
                'detections': detections,
                'inference_time': inference_time,
                'image': img
            }
        except Exception as e:
            inference_logger.error(f"图片推理失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def predict_video(self, video_path: str, save_path: str = None, callback=None) -> Dict:
        """
        对视频进行推理
        
        Args:
            video_path: 视频路径
            save_path: 结果保存路径
            callback: 进度回调函数 callback(frame, detections, fps)
            
        Returns:
            Dict: 推理结果统计
        """
        if not self.model:
            inference_logger.error("模型未加载")
            return {'success': False, 'error': '模型未加载'}
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {'success': False, 'error': '无法打开视频'}
            
            # 视频信息
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # 视频写入器
            writer = None
            if save_path:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(save_path, fourcc, fps, (width, height))
            
            frame_count = 0
            total_detections = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                start_time = time.time()
                
                # 推理
                results = self.model.predict(
                    source=frame,
                    conf=self.conf_threshold,
                    iou=self.iou_threshold,
                    device=self.device,
                    verbose=False
                )
                
                detections = []
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        cls = int(box.cls[0].cpu().numpy())
                        
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': conf,
                            'class_name': result.names[cls]
                        })
                        
                        # 绘制
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        label = f"{result.names[cls]}: {conf:.2f}"
                        cv2.putText(frame, label, (int(x1), int(y1)-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                current_fps = 1.0 / (time.time() - start_time)
                total_detections += len(detections)
                frame_count += 1
                
                # 写入视频
                if writer:
                    writer.write(frame)
                
                # 回调
                if callback:
                    callback(frame, detections, current_fps)
            
            cap.release()
            if writer:
                writer.release()
            
            inference_logger.info(f"视频推理完成: {video_path}, 总帧数: {frame_count}, 总检测数: {total_detections}")
            
            return {
                'success': True,
                'total_frames': frame_count,
                'total_detections': total_detections,
                'fps': fps
            }
        except Exception as e:
            inference_logger.error(f"视频推理失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def predict_camera(self, camera_id: int = 0, callback=None):
        """
        实时摄像头推理
        
        Args:
            camera_id: 摄像头ID
            callback: 帧回调函数 callback(frame, detections, fps)
        """
        if not self.model:
            inference_logger.error("模型未加载")
            return
        
        try:
            cap = cv2.VideoCapture(camera_id)
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                start_time = time.time()
                
                # 推理
                results = self.model.predict(
                    source=frame,
                    conf=self.conf_threshold,
                    iou=self.iou_threshold,
                    device=self.device,
                    verbose=False
                )
                
                detections = []
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        cls = int(box.cls[0].cpu().numpy())
                        
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': conf,
                            'class_name': result.names[cls]
                        })
                        
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        label = f"{result.names[cls]}: {conf:.2f}"
                        cv2.putText(frame, label, (int(x1), int(y1)-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                fps = 1.0 / (time.time() - start_time)
                
                if callback:
                    if not callback(frame, detections, fps):
                        break
            
            cap.release()
        except Exception as e:
            inference_logger.error(f"摄像头推理失败: {str(e)}")
    
    def log_inference(self, user_id: int, model_name: str, source_type: str, 
                     source_path: str, detections: int, inference_time: float):
        """
        记录推理日志到数据库
        
        Args:
            user_id: 用户ID
            model_name: 模型名称
            source_type: 数据源类型
            source_path: 数据源路径
            detections: 检测数量
            inference_time: 推理时间
        """
        try:
            db_service.execute_query(
                """INSERT INTO inference_logs 
                (user_id, model_name, source_type, source_path, detections, inference_time) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, model_name, source_type, source_path, detections, inference_time),
                fetch=False
            )
        except Exception as e:
            inference_logger.error(f"记录推理日志失败: {str(e)}")

# 全局推理引擎实例
inference_engine = InferenceEngine()
