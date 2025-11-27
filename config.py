"""
系统配置文件
包含数据库、模型、路径等全局配置
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据库配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '051128',  # 请修改为实际密码
    'database': 'underwater_detection',
    'charset': 'utf8mb4'
}

# 路径配置
DATA_DIR = BASE_DIR / 'data'
MODELS_DIR = BASE_DIR / 'models'
LOGS_DIR = BASE_DIR / 'logs'
UPLOADS_DIR = BASE_DIR / 'uploads'
RESULTS_DIR = BASE_DIR / 'results'

# 确保目录存在
for dir_path in [DATA_DIR, MODELS_DIR, LOGS_DIR, UPLOADS_DIR, RESULTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# YOLOv11 配置
YOLO_CONFIG = {
    'default_model': 'yolov11n.pt',
    'img_size': 640,
    'conf_threshold': 0.25,
    'iou_threshold': 0.45,
    'max_det': 1000,
    'classes': ['fish', 'coral', 'turtle', 'shark', 'jellyfish', 'dolphin', 'submarine', 'diver']
}

# 训练配置
TRAINING_CONFIG = {
    'epochs': 100,
    'batch_size': 16,
    'img_size': 640,
    'lr': 0.01,
    'workers': 4,
    'patience': 50
}

# 系统配置
SYSTEM_CONFIG = {
    'device': 'cuda',  # cuda / cpu
    'language': 'zh_CN',  # zh_CN / en_US
    'theme': 'light',  # light / dark
    'log_level': 'INFO'
}

# UI配置
UI_CONFIG = {
    'window_width': 1280,
    'window_height': 720,
    'min_width': 1024,
    'min_height': 600
}

# 默认用户（首次运行时创建）
DEFAULT_USERS = [
    {'username': 'admin', 'password': 'admin123', 'role': 'admin', 'email': 'admin@underwater.com'},
    {'username': 'user', 'password': 'user123', 'role': 'user', 'email': 'user@underwater.com'}
]

# 日志配置
LOG_CONFIG = {
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}
