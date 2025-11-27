# 系统架构设计文档

## 1. 系统架构概览

水下目标识别系统采用经典的分层架构设计，包含以下几个层次：

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│         (UI Layer - PyQt6)              │
├─────────────────────────────────────────┤
│         Business Logic Layer            │
│         (Services Layer)                │
├─────────────────────────────────────────┤
│         Data Access Layer               │
│         (Database Service)              │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │
│    (MySQL, File System, YOLOv11)       │
└─────────────────────────────────────────┘
```

## 2. 层次划分

### 2.1 表现层 (UI Layer)

**技术栈**: PyQt6

**职责**:
- 用户交互界面
- 数据展示与可视化
- 事件响应与处理

**主要模块**:
- `login/` - 登录模块
  - `LoginWindow` - 登录窗口
  - `RegisterDialog` - 注册对话框
  
- `admin/` - 管理员模块
  - `AdminDashboard` - 管理员仪表盘
  
- `main/` - 主界面模块
  - `MainWindow` - 主窗口（推理界面）
  
- `training/` - 训练模块
  - `TrainingWindow` - 训练管理窗口

### 2.2 业务逻辑层 (Services Layer)

**职责**:
- 核心业务逻辑实现
- 数据处理与转换
- 业务规则验证

**主要服务**:

#### AuthService (认证服务)
```python
class AuthService:
    - register()        # 用户注册
    - login()           # 用户登录
    - change_password() # 修改密码
    - get_all_users()   # 获取用户列表
    - update_user()     # 更新用户信息
    - delete_user()     # 删除用户
```

#### InferenceEngine (推理引擎)
```python
class InferenceEngine:
    - load_model()      # 加载模型
    - predict_image()   # 图片推理
    - predict_video()   # 视频推理
    - predict_camera()  # 摄像头实时推理
    - set_parameters()  # 设置推理参数
```

#### TrainingService (训练服务)
```python
class TrainingService:
    - prepare_training()    # 准备训练
    - start_training()      # 开始训练
    - stop_training()       # 停止训练
    - validate_model()      # 验证模型
    - export_model()        # 导出模型
```

#### ModelManager (模型管理)
```python
class ModelManager:
    - add_model()       # 添加模型
    - get_all_models()  # 获取模型列表
    - update_model()    # 更新模型信息
    - delete_model()    # 删除模型
    - search_models()   # 搜索模型
```

### 2.3 数据访问层 (Data Access Layer)

**技术栈**: PyMySQL

**职责**:
- 数据库连接管理
- SQL 查询执行
- 事务处理

**核心类**:
```python
class DatabaseService:
    - get_connection()  # 获取数据库连接
    - execute_query()   # 执行查询
    - execute_many()    # 批量执行
```

### 2.4 基础设施层 (Infrastructure Layer)

**组件**:
- MySQL 数据库
- 文件系统 (模型、日志、结果存储)
- YOLOv11 推理引擎
- PyTorch 训练框架

## 3. 数据库设计

### 3.1 ER 图

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  users   │────┬───▶│  models  │         │login_logs│
└──────────┘    │    └──────────┘         └──────────┘
                │                               ▲
                │    ┌──────────────┐          │
                └───▶│inference_logs│──────────┘
                │    └──────────────┘
                │
                │    ┌──────────────┐
                └───▶│training_logs │
                     └──────────────┘
```

### 3.2 数据表说明

#### users (用户表)
```sql
- id (主键)
- username (用户名，唯一)
- password (密码哈希)
- email (邮箱)
- role (角色: admin/user)
- status (状态: active/inactive)
- created_at (创建时间)
- updated_at (更新时间)
```

#### models (模型表)
```sql
- id (主键)
- name (模型名称)
- version (版本号)
- file_path (文件路径)
- classes (类别列表 JSON)
- description (描述)
- author (作者)
- created_at (创建时间)
```

#### login_logs (登录日志)
```sql
- id (主键)
- user_id (外键)
- username (用户名)
- login_time (登录时间)
- ip_address (IP地址)
- status (状态: success/failed)
```

#### inference_logs (推理日志)
```sql
- id (主键)
- user_id (外键)
- model_name (模型名称)
- source_type (数据源类型)
- source_path (数据源路径)
- detections (检测数量)
- inference_time (推理时间)
- created_at (创建时间)
```

#### training_logs (训练日志)
```sql
- id (主键)
- user_id (外键)
- model_name (模型名称)
- dataset_path (数据集路径)
- epochs (训练轮数)
- batch_size (批次大小)
- status (状态: running/completed/failed)
- start_time (开始时间)
- end_time (结束时间)
- final_map (最终mAP)
```

## 4. 核心流程

### 4.1 用户登录流程

```
用户输入 → LoginWindow → AuthService.login()
                              ↓
                         验证用户名密码
                              ↓
                         记录登录日志
                              ↓
                    返回用户信息 → MainWindow
```

### 4.2 推理检测流程

```
选择模型 → InferenceEngine.load_model()
             ↓
选择数据源 → 图片/视频/摄像头
             ↓
开始检测 → predict_xxx()
             ↓
         YOLO推理
             ↓
      绘制检测框 → 显示结果
             ↓
         保存结果
             ↓
      记录推理日志
```

### 4.3 模型训练流程

```
选择数据集 → 创建data.yaml
              ↓
配置参数 → 训练超参数设置
              ↓
开始训练 → TrainingService.start_training()
              ↓
          训练循环 (YOLO)
              ↓
      监控训练指标 → 实时显示
              ↓
         保存权重 → 模型仓库
              ↓
      记录训练日志
```

## 5. 设计模式应用

### 5.1 单例模式
- `DatabaseService` - 全局唯一数据库服务实例
- `InferenceEngine` - 全局推理引擎
- `ModelManager` - 全局模型管理器

### 5.2 工厂模式
- `LogManager` - 日志记录器工厂

### 5.3 观察者模式
- PyQt6 信号槽机制
- 训练进度回调

### 5.4 策略模式
- 不同数据源的推理策略（图片/视频/摄像头）

## 6. 安全设计

### 6.1 密码安全
- 使用 SHA256 哈希存储密码
- 不存储明文密码

### 6.2 SQL注入防护
- 使用参数化查询
- 避免字符串拼接SQL

### 6.3 权限控制
- 角色基于访问控制 (RBAC)
- 管理员/普通用户权限分离

## 7. 性能优化

### 7.1 数据库优化
- 添加索引 (username, role, login_time 等)
- 使用连接池
- 分页查询

### 7.2 推理优化
- GPU 加速 (CUDA)
- 批处理推理
- 多线程处理

### 7.3 UI响应性
- 使用 QThread 避免阻塞UI
- 异步加载数据

## 8. 可扩展性设计

### 8.1 模块化设计
- 各层职责清晰
- 低耦合高内聚

### 8.2 配置化
- 统一配置管理 (config.py)
- 易于修改参数

### 8.3 插件化
- 支持自定义模型加载
- 支持多种数据源

## 9. 部署架构

### 9.1 开发环境
```
Python 3.8+
MySQL 8.0
PyQt6
YOLOv11
```

### 9.2 生产环境
```
打包后的可执行文件
独立的MySQL数据库
GPU服务器(可选)
```

## 10. 未来扩展方向

- 支持分布式训练
- 云端模型管理
- Web界面版本
- 移动端应用
- 实时流媒体检测
- 模型压缩与优化
- 多GPU并行推理
