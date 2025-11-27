# 示例数据集说明

本目录用于存放示例数据和测试数据。

## 目录结构

```
data/
├── images/              # 示例图片
│   ├── test_image1.jpg
│   ├── test_image2.jpg
│   └── ...
├── videos/              # 示例视频
│   └── test_video.mp4
└── datasets/            # 训练数据集
    └── underwater/
        ├── images/
        │   ├── train/
        │   └── val/
        └── labels/
            ├── train/
            └── val/
```

## 数据集格式

训练数据集遵循 YOLO 格式：

### 图片要求
- 格式：JPG、PNG
- 建议分辨率：640x640 或以上

### 标注格式
每个图片对应一个同名的 .txt 文件，每行表示一个目标：

```
<class_id> <x_center> <y_center> <width> <height>
```

其中：
- `class_id`: 类别ID（从0开始）
- `x_center`, `y_center`: 目标中心点坐标（归一化到0-1）
- `width`, `height`: 目标宽高（归一化到0-1）

### 示例
```
0 0.5 0.5 0.2 0.3
1 0.3 0.7 0.15 0.2
```

## 下载数据集

您可以从以下来源获取水下目标检测数据集：

1. **Roboflow Universe**
   - 搜索 "underwater detection"
   - 下载 YOLO 格式数据集

2. **Kaggle**
   - Underwater Object Detection Dataset

3. **自建数据集**
   - 使用 LabelImg 或 Roboflow 标注工具

## 使用说明

1. 将数据集放入 `data/datasets/` 目录
2. 在训练界面选择数据集路径
3. 确保数据集包含 train 和 val 分割
4. 开始训练
