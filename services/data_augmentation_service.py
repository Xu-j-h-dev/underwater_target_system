"""
数据增强服务
提供图片和标签的几何变换增强功能
"""
import os
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
from typing import Dict, List, Callable
import numpy as np
from utils import system_logger

class DataAugmentationService:
    """数据增强服务类"""
    
    def __init__(self):
        """初始化数据增强服务"""
        self.supported_transforms = {
            # 几何变换（需要修改标签）
            "horizontal_flip": "水平翻转",
            "vertical_flip": "垂直翻转",
            "rotate_90": "旋转90度",
            "rotate_180": "旋转180度",
            # 像素级变换（不需要修改标签）
            "gaussian_noise": "高斯噪声",
            "brightness": "亮度调整",
            "contrast": "对比度调整",
            "gaussian_blur": "高斯模糊"
        }
    
    def transform_label(self, label_lines: List[str], img_w: int, img_h: int, transform_type: str) -> List[str]:
        """
        根据图片变换类型，修正标签坐标
        
        Args:
            label_lines: 原始标签行列表
            img_w: 原始图片宽度
            img_h: 原始图片高度
            transform_type: 变换类型
            
        Returns:
            List[str]: 修正后的标签行列表
        """
        transformed_labels = []
        for line in label_lines:
            if not line.strip():
                continue
            # 解析标签：类别、x_center(%)、y_center(%)、w(%)、h(%)
            try:
                cls, xc, yc, w, h = map(float, line.strip().split())
            except ValueError:
                system_logger.warning(f"标签行格式错误，跳过: {line}")
                continue
            
            # 根据变换类型修正坐标
            if transform_type == "horizontal_flip":
                # 水平翻转：x_center = 1 - x_center，其他不变
                xc = 1.0 - xc
            elif transform_type == "vertical_flip":
                # 垂直翻转：y_center = 1 - y_center，其他不变
                yc = 1.0 - yc
            elif transform_type == "rotate_90":
                # 旋转90度：宽高互换，x_center ↔ y_center，w ↔ h，x_center = 1 - 原y_center
                xc, yc = yc, 1.0 - xc
                w, h = h, w
            elif transform_type == "rotate_180":
                # 旋转180度：x_center = 1 - x_center，y_center = 1 - y_center
                xc = 1.0 - xc
                yc = 1.0 - yc
            
            # 确保坐标在0-1范围内（避免浮点误差）
            xc = max(0.001, min(0.999, xc))
            yc = max(0.001, min(0.999, yc))
            w = max(0.001, min(0.999, w))
            h = max(0.001, min(0.999, h))
            
            # 重新拼接标签行（保留6位小数，保证精度）
            transformed_line = f"{int(cls)} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n"
            transformed_labels.append(transformed_line)
        
        return transformed_labels
    
    def transform_image(self, img: Image.Image, transform_type: str) -> Image.Image:
        """
        对图片执行几何变换
        
        Args:
            img: PIL图片对象
            transform_type: 变换类型
            
        Returns:
            Image.Image: 变换后的图片
        """
        # 几何变换
        if transform_type == "horizontal_flip":
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        elif transform_type == "vertical_flip":
            return img.transpose(Image.FLIP_TOP_BOTTOM)
        elif transform_type == "rotate_90":
            return img.rotate(90, expand=True)
        elif transform_type == "rotate_180":
            return img.rotate(180)
        # 像素级变换
        elif transform_type == "gaussian_noise":
            # 添加高斯噪声
            img_array = np.array(img)
            noise = np.random.normal(0, 25, img_array.shape).astype(np.uint8)
            noisy_img = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            return Image.fromarray(noisy_img)
        elif transform_type == "brightness":
            # 亮度调整（随机1.2倍）
            enhancer = ImageEnhance.Brightness(img)
            return enhancer.enhance(1.2)
        elif transform_type == "contrast":
            # 对比度调整（随机1.3倍）
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(1.3)
        elif transform_type == "gaussian_blur":
            # 高斯模糊
            return img.filter(ImageFilter.GaussianBlur(radius=2))
        else:
            return img
    
    def augment_dataset(self, 
                       image_dir: str, 
                       label_dir: str,
                       output_image_dir: str,
                       output_label_dir: str,
                       transforms: Dict[str, bool],
                       progress_callback: Callable[[int, int, str], None] = None) -> tuple:
        """
        批量增强数据集
        
        Args:
            image_dir: 原始图片文件夹路径
            label_dir: 原始标签文件夹路径
            output_image_dir: 输出图片文件夹路径
            output_label_dir: 输出标签文件夹路径
            transforms: 要执行的变换字典 {变换名: 是否执行}
            progress_callback: 进度回调函数 (当前, 总数, 消息)
            
        Returns:
            tuple: (成功数, 失败数, 错误消息列表)
        """
        # 创建输出文件夹
        os.makedirs(output_image_dir, exist_ok=True)
        os.makedirs(output_label_dir, exist_ok=True)
        
        # 获取所有图片文件
        image_files = []
        for f in os.listdir(image_dir):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_files.append(f)
        
        if not image_files:
            system_logger.error(f"图片文件夹为空: {image_dir}")
            return (0, 0, ["图片文件夹为空"])
        
        # 按数字排序（支持 image_1.jpg, image_10.jpg 等格式）
        import re
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]
        image_files.sort(key=natural_sort_key)
        total_images = len(image_files)
        success_count = 0
        failed_count = 0
        errors = []
        
        for idx, img_file in enumerate(image_files, 1):
            # 解析文件名（支持 image_N.jpg 或其他格式）
            base_name = os.path.splitext(img_file)[0]
            img_suffix = os.path.splitext(img_file)[1]
            img_path = os.path.join(image_dir, img_file)
            label_path = os.path.join(label_dir, f"{base_name}.txt")
            
            # 检查对应的标签文件是否存在
            if not os.path.exists(label_path):
                msg = f"标签文件不存在: {label_path}"
                system_logger.warning(msg)
                errors.append(msg)
                failed_count += 1
                if progress_callback:
                    progress_callback(idx, total_images, msg)
                continue
            
            # 读取图片和标签
            try:
                img = Image.open(img_path)
                img_w, img_h = img.size
                with open(label_path, "r", encoding="utf-8") as f:
                    label_lines = f.readlines()
            except Exception as e:
                msg = f"读取 {img_file} 失败: {str(e)}"
                system_logger.error(msg)
                errors.append(msg)
                failed_count += 1
                if progress_callback:
                    progress_callback(idx, total_images, msg)
                continue
            
            # 执行每种变换
            transforms_applied = 0
            for transform_name, do_transform in transforms.items():
                if not do_transform:
                    continue
                
                try:
                    # 1. 处理图片变换
                    augmented_img = self.transform_image(img, transform_name)
                    
                    # 2. 处理标签变换（仅几何变换需要修改标签）
                    if transform_name in ['horizontal_flip', 'vertical_flip', 'rotate_90', 'rotate_180']:
                        augmented_labels = self.transform_label(label_lines, img_w, img_h, transform_name)
                    else:
                        # 像素级变换不改变标签
                        augmented_labels = label_lines
                    
                    # 3. 保存扩充后的图片和标签
                    new_img_name = f"{base_name}_{transform_name}{img_suffix}"
                    new_label_name = f"{base_name}_{transform_name}.txt"
                    
                    augmented_img.save(os.path.join(output_image_dir, new_img_name))
                    with open(os.path.join(output_label_dir, new_label_name), "w", encoding="utf-8") as f:
                        f.writelines(augmented_labels)
                    
                    transforms_applied += 1
                except Exception as e:
                    msg = f"处理 {img_file} 的 {transform_name} 变换失败: {str(e)}"
                    system_logger.error(msg)
                    errors.append(msg)
            
            if transforms_applied > 0:
                success_count += 1
                msg = f"完成 {img_file} 的 {transforms_applied} 种变换"
            else:
                failed_count += 1
                msg = f"{img_file} 未应用任何变换"
            
            system_logger.info(msg)
            if progress_callback:
                progress_callback(idx, total_images, msg)
        
        summary_msg = f"数据增强完成！成功: {success_count}, 失败: {failed_count}"
        system_logger.info(summary_msg)
        return (success_count, failed_count, errors)

# 全局数据增强服务实例
data_augmentation_service = DataAugmentationService()
