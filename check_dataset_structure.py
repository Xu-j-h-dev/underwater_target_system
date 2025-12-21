"""
数据集结构检查工具
快速验证 YOLO 数据集目录结构是否正确
"""
import sys
from pathlib import Path

def check_dataset_structure(dataset_path):
    """检查数据集目录结构"""
    dataset_path = Path(dataset_path)
    
    print("=" * 60)
    print("YOLO 数据集结构检查工具")
    print("=" * 60)
    print(f"数据集路径: {dataset_path}")
    print()
    
    if not dataset_path.exists():
        print(f"❌ 错误: 数据集目录不存在!")
        return False
    
    # 检查必需的目录
    required_dirs = {
        'images/train': '训练集图片',
        'images/val': '验证集图片',
        'labels/train': '训练集标注',
        'labels/val': '验证集标注'
    }
    
    all_ok = True
    
    for dir_path, desc in required_dirs.items():
        full_path = dataset_path / dir_path
        if full_path.exists():
            # 统计文件数量
            files = list(full_path.glob('*'))
            count = len(files)
            print(f"✓ {desc:12} : {full_path}")
            print(f"  文件数量: {count}")
        else:
            print(f"❌ {desc:12} : 目录不存在 - {full_path}")
            all_ok = False
    
    print()
    print("=" * 60)
    
    if all_ok:
        print("✓ 数据集结构检查通过!")
        print()
        print("你可以在训练界面中这样配置:")
        print(f"  数据集路径: {dataset_path}")
        print(f"  训练集路径: images/train")
        print(f"  验证集路径: images/val")
    else:
        print("❌ 数据集结构不完整，请确保包含以下目录:")
        print("  - images/train/")
        print("  - images/val/")
        print("  - labels/train/")
        print("  - labels/val/")
    
    print("=" * 60)
    return all_ok

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python check_dataset_structure.py <数据集路径>")
        print()
        print("示例:")
        print("  python check_dataset_structure.py C:\\Users\\22742\\Desktop\\my_dataset")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    check_dataset_structure(dataset_path)
