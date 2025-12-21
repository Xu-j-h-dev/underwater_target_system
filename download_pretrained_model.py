"""
下载 YOLOv11 预训练模型
"""
from ultralytics import YOLO
from config import MODELS_DIR
import sys

def download_yolo_model(model_name='yolov11n.pt'):
    """
    下载 YOLOv11 预训练模型
    
    Args:
        model_name: 模型名称，可选: yolov11n.pt, yolov11s.pt, yolov11m.pt, yolov11l.pt, yolov11x.pt
    """
    print("=" * 60)
    print("YOLOv11 预训练模型下载工具")
    print("=" * 60)
    print()
    
    try:
        print(f"正在下载模型: {model_name}")
        print("这可能需要几分钟时间，请耐心等待...")
        print()
        
        # YOLO 会自动下载模型到默认位置，然后我们可以使用它
        model = YOLO(model_name)
        
        print(f"✓ 模型下载成功!")
        print(f"  模型已保存到 ultralytics 缓存目录")
        print(f"  您可以在训练时直接使用 '{model_name}'")
        print()
        
        # 可选：将模型复制到项目的 models 目录
        import shutil
        from pathlib import Path
        
        # 查找下载的模型文件
        home = Path.home()
        cache_paths = [
            home / '.cache' / 'ultralytics',
            home / 'AppData' / 'Roaming' / 'Ultralytics',
        ]
        
        for cache_path in cache_paths:
            source_model = cache_path / model_name
            if source_model.exists():
                target_model = MODELS_DIR / model_name
                shutil.copy2(source_model, target_model)
                print(f"✓ 模型已复制到项目目录: {target_model}")
                break
        
        print()
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"✗ 下载失败: {str(e)}")
        print()
        print("请检查网络连接，或手动下载模型文件:")
        print("https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov11n.pt")
        print()
        print("=" * 60)
        return False

if __name__ == "__main__":
    # 默认下载 yolov11n (最小的模型)
    model_name = 'yolov11n.pt'
    
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
        if not model_name.endswith('.pt'):
            model_name += '.pt'
    
    print("可用的预训练模型:")
    print("  - yolov11n.pt (Nano, 最小最快)")
    print("  - yolov11s.pt (Small)")
    print("  - yolov11m.pt (Medium)")
    print("  - yolov11l.pt (Large)")
    print("  - yolov11x.pt (Extra Large, 最大最准)")
    print()
    
    download_yolo_model(model_name)
