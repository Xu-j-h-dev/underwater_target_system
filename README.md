# 水下目标识别系统

基于 **Python + PyQt6 + YOLOv11 + MySQL** 的桌面级水下目标识别系统，支持实时/离线检测、模型训练、用户管理等功能。

## 🌟 功能特性

### 1. 双角色登录系统
- 支持 **管理员** 和 **普通用户** 双角色
- 账号管理（创建、删除、修改密码、角色设置）
- 登录日志记录

**默认账号：**
- 管理员：`admin` / `admin123`
- 普通用户：`user` / `user123`

### 2. 管理员仪表盘
- **用户管理**：查看/编辑用户信息、角色、状态
- **模型管理**：上传/删除模型、版本记录、标签说明
- **日志管理**：登录日志、推理日志、训练日志、系统日志
- 支持分页、搜索、排序、导出

### 3. 主界面（推理界面）
- **模型加载**：从模型仓库选择 YOLOv11 权重
- **参数设置**：置信度阈值、NMS 阈值调节
- **数据源支持**：
  - 实时视频（USB 相机 / IP 摄像头）
  - 单张图片
  - 视频文件
- **可视化**：检测框、类别、置信度实时显示
- **输出**：保存检测结果为图片/视频，导出 JSON/TXT
- **性能显示**：FPS、推理耗时

### 4. 模型训练管理
- 数据集导入（YOLO 格式）
- 配置训练超参数（epochs、batch size、lr 等）
- 启动、暂停、中断训练任务
- 实时监控训练日志
- 训练完成后自动保存权重到模型仓库

### 5. 模型仓库
- 展示所有可用 YOLOv11 模型
- 模型版本管理
- 一键切换模型

### 6. 日志与告警中心
- 登录日志、推理日志、训练日志
- 系统错误和异常告警
- 支持导出与搜索

## 📁 项目结构

```
underwater_target_system/
├── data/                   # 示例数据集、配置
├── models/                 # YOLOv11 权重与模型定义
├── services/               # 业务逻辑层
│   ├── __init__.py
│   ├── database.py        # 数据库服务
│   ├── auth_service.py    # 认证服务
│   ├── inference_service.py  # 推理服务
│   ├── training_service.py   # 训练服务
│   └── model_manager.py   # 模型管理
├── ui/                     # PyQt6 UI 相关
│   ├── login/             # 登录界面
│   │   ├── login_window.py
│   │   └── register_dialog.py
│   ├── admin/             # 管理员仪表盘
│   │   └── admin_dashboard.py
│   ├── main/              # 主界面（推理）
│   │   └── main_window.py
│   ├── training/          # 训练管理
│   │   └── training_window.py
│   └── settings/          # 系统设置
├── utils/                  # 工具函数、日志模块
│   ├── __init__.py
│   └── logger.py          # 日志管理
├── logs/                   # 日志文件目录
├── uploads/                # 上传文件目录
├── results/                # 检测结果目录
├── config.py               # 系统配置
├── main.py                 # 程序入口
├── requirements.txt        # 依赖列表
└── README.md               # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+ / 8.0+
- CUDA 11.0+ (可选，GPU加速)

### 安装步骤

#### 1. 克隆项目

```bash
cd underwater_target_system
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置数据库

编辑 `config.py` 文件，修改数据库配置：

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '你的密码',  # 修改为实际密码
    'database': 'underwater_detection',
    'charset': 'utf8mb4'
}
```

**注意**：首次运行时，程序会自动创建数据库和表。

#### 4. 准备 YOLOv11 模型

将 YOLOv11 模型权重（如 `yolov11n.pt`）放入 `models/` 目录。

如果没有模型，首次运行时会自动下载默认模型。

#### 5. 运行程序

```bash
python main.py
```

## 📖 使用说明

### 登录系统

1. 启动程序后，进入登录界面
2. 使用默认账号登录：
   - 管理员：`admin` / `admin123`
   - 普通用户：`user` / `user123`
3. 或点击"注册"创建新账号

### 推理检测

1. 登录后进入主界面
2. 在左侧控制面板选择模型并加载
3. 调整置信度和 IOU 阈值
4. 选择数据源（摄像头/图片/视频）
5. 点击"开始检测"
6. 查看检测结果并保存

### 模型训练

1. 点击菜单栏 "工具" -> "模型训练"
2. 选择数据集目录（YOLO 格式）
3. 配置训练参数（epochs、batch size 等）
4. 点击"开始训练"
5. 实时监控训练进度和日志
6. 训练完成后，模型自动保存到模型仓库

### 管理员功能

1. 以管理员身份登录
2. 点击菜单栏 "管理" -> "管理员仪表盘"
3. 管理用户、模型、查看日志

## 🔧 数据集格式

训练数据集需遵循 YOLO 格式：

```
dataset/
├── images/
│   ├── train/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   └── val/
│       ├── img3.jpg
│       └── img4.jpg
└── labels/
    ├── train/
    │   ├── img1.txt
    │   └── img2.txt
    └── val/
        ├── img3.txt
        └── img4.txt
```

标注文件格式（每行一个目标）：
```
<class_id> <x_center> <y_center> <width> <height>
```

## 📦 打包部署

### 使用 PyInstaller 打包

#### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

#### 2. 生成 .spec 文件

```bash
pyi-makespec --windowed --name "UnderwaterDetection" main.py
```

#### 3. 编辑 .spec 文件

修改 `UnderwaterDetection.spec`：

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('models', 'models'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'PyQt6',
        'ultralytics',
        'pymysql',
        'cv2',
        'numpy',
        'torch',
        'torchvision',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='UnderwaterDetection',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # 可选：添加图标
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='UnderwaterDetection',
)
```

#### 4. 执行打包

```bash
pyinstaller UnderwaterDetection.spec
```

打包完成后，在 `dist/UnderwaterDetection/` 目录下生成可执行文件。

### 打包注意事项

1. **确保包含所有依赖**：PyInstaller 可能无法自动检测所有依赖
2. **模型文件**：确保 YOLOv11 模型文件被包含
3. **配置文件**：检查 config.py 是否正确打包
4. **测试**：打包后务必在干净的环境中测试

## ⚙️ 配置说明

### config.py 主要配置项

```python
# 数据库配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'underwater_detection',
}

# YOLO 配置
YOLO_CONFIG = {
    'default_model': 'yolov11n.pt',
    'conf_threshold': 0.25,
    'iou_threshold': 0.45,
    'classes': ['fish', 'coral', 'turtle', ...]
}

# 训练配置
TRAINING_CONFIG = {
    'epochs': 100,
    'batch_size': 16,
    'img_size': 640,
    'lr': 0.01,
}

# 系统配置
SYSTEM_CONFIG = {
    'device': 'cuda',  # cuda / cpu
    'language': 'zh_CN',
    'theme': 'light',
}
```

## 🛠️ 技术栈

- **UI框架**：PyQt6
- **深度学习**：PyTorch + Ultralytics YOLOv11
- **数据库**：MySQL + PyMySQL
- **图像处理**：OpenCV
- **数据处理**：NumPy, Pandas
- **可视化**：Matplotlib, Seaborn

## 📝 开发规范

### 代码风格

- 遵循 PEP 8 规范
- 类和函数包含文档字符串
- 使用类型注解

### 日志规范

系统使用分模块日志：
- `system.log` - 系统日志
- `auth.log` - 认证日志
- `inference.log` - 推理日志
- `training.log` - 训练日志

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👥 联系方式

- 项目维护者：Underwater Detection Team
- Email: admin@underwater.com

## 🙏 致谢

- [Ultralytics YOLOv11](https://github.com/ultralytics/ultralytics)
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- [OpenCV](https://opencv.org/)

---

**注意**：本系统仅供学习研究使用，请遵守相关法律法规。
