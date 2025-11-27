# 安装指南

本文档提供详细的安装和部署步骤。

## 系统要求

### 硬件要求
- **CPU**: Intel i5 及以上（推荐 i7）
- **内存**: 8GB 及以上（推荐 16GB）
- **显卡**: NVIDIA GPU（可选，用于 CUDA 加速）
  - 显存: 4GB+ (推荐 6GB+)
- **硬盘**: 至少 10GB 可用空间

### 软件要求
- **操作系统**: 
  - Windows 10/11
  - Ubuntu 18.04+
  - macOS 10.14+
- **Python**: 3.8, 3.9, 3.10, 3.11
- **MySQL**: 5.7+ 或 8.0+
- **CUDA**: 11.0+ (如果使用 GPU)

## 安装步骤

### 1. 安装 Python

#### Windows
1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载 Python 3.8+ 安装包
3. 安装时勾选 "Add Python to PATH"
4. 验证安装：
   ```bash
   python --version
   ```

#### Linux (Ubuntu)
```bash
sudo apt update
sudo apt install python3.8 python3-pip
python3 --version
```

#### macOS
```bash
brew install python@3.8
python3 --version
```

### 2. 安装 MySQL

#### Windows
1. 下载 [MySQL Installer](https://dev.mysql.com/downloads/installer/)
2. 选择 Developer Default 安装
3. 设置 root 密码（记住此密码）
4. 启动 MySQL 服务

#### Linux (Ubuntu)
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo mysql_secure_installation
```

#### macOS
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

### 3. 安装 CUDA (可选，GPU 加速)

如果您有 NVIDIA GPU，建议安装 CUDA 以加速推理和训练。

1. 访问 [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
2. 选择对应的操作系统和版本
3. 下载并安装
4. 验证安装：
   ```bash
   nvcc --version
   ```

### 4. 克隆/下载项目

```bash
# 如果使用 Git
git clone <repository-url>
cd underwater_target_system

# 或直接解压下载的压缩包
cd underwater_target_system
```

### 5. 创建虚拟环境（推荐）

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

### 6. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

**注意**：
- 如果安装 PyTorch 时遇到问题，访问 [PyTorch 官网](https://pytorch.org/) 获取适合您系统的安装命令
- GPU 版本：
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```
- CPU 版本：
  ```bash
  pip install torch torchvision torchaudio
  ```

### 7. 配置数据库

#### 7.1 创建数据库用户（可选）

登录 MySQL：
```bash
mysql -u root -p
```

创建专用用户：
```sql
CREATE USER 'underwater_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON underwater_detection.* TO 'underwater_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 7.2 修改配置文件

编辑 `config.py`，修改数据库配置：

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',  # 或 'underwater_user'
    'password': '你的密码',  # 修改为实际密码
    'database': 'underwater_detection',
    'charset': 'utf8mb4'
}
```

**注意**：程序首次运行会自动创建数据库和表。

### 8. 下载 YOLOv11 模型（可选）

系统首次运行时会自动下载默认模型。您也可以手动下载：

```bash
# 在 Python 中执行
from ultralytics import YOLO
model = YOLO('yolov11n.pt')  # 会自动下载
```

将下载的模型文件放入 `models/` 目录。

### 9. 运行程序

#### Windows
```bash
# 使用启动脚本
start.bat

# 或直接运行
python main.py
```

#### Linux/macOS
```bash
# 添加执行权限
chmod +x start.sh

# 运行启动脚本
./start.sh

# 或直接运行
python3 main.py
```

## 常见问题

### Q1: ImportError: No module named 'PyQt6'

**解决方案**：
```bash
pip install PyQt6
```

### Q2: 数据库连接失败

**解决方案**：
1. 确保 MySQL 服务已启动
2. 检查 `config.py` 中的数据库配置
3. 验证数据库用户权限
4. 检查防火墙设置

### Q3: CUDA out of memory

**解决方案**：
1. 减小 batch size
2. 使用更小的模型（yolov11n.pt）
3. 切换到 CPU 模式（修改 config.py 中的 device 为 'cpu'）

### Q4: ultralytics 安装失败

**解决方案**：
```bash
# 使用镜像源
pip install ultralytics -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q5: PyQt6 在 Linux 上显示问题

**解决方案**：
```bash
sudo apt install libxcb-xinerama0
```

## 验证安装

运行测试脚本验证安装：

```bash
python -c "import PyQt6; import torch; import ultralytics; print('All modules imported successfully!')"
```

## 卸载

### 1. 删除虚拟环境

```bash
# Windows
rmdir /s venv

# Linux/macOS
rm -rf venv
```

### 2. 删除数据库

```sql
DROP DATABASE underwater_detection;
```

### 3. 删除项目目录

```bash
# 根据需要删除整个项目目录
```

## 下一步

- 阅读 [README.md](README.md) 了解系统功能
- 查看 [ARCHITECTURE.md](ARCHITECTURE.md) 了解系统架构
- 开始使用系统进行目标检测和模型训练

## 技术支持

如遇到问题，请：
1. 查看日志文件（`logs/` 目录）
2. 检查系统配置
3. 提交 Issue 或联系开发团队
