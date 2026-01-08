"""
数据增强窗口
提供图片和标签的几何变换增强功能
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QCheckBox, QTextEdit,
                             QProgressBar, QMessageBox, QGroupBox, QRadioButton,
                             QButtonGroup, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from services.data_augmentation_service import data_augmentation_service
import os

class AugmentationWorker(QThread):
    """数据增强工作线程"""
    progress = pyqtSignal(int, int, str)  # 当前, 总数, 消息
    finished = pyqtSignal(int, int, list)  # 成功数, 失败数, 错误列表
    
    def __init__(self, image_dir, label_dir, output_image_dir, output_label_dir, transforms):
        super().__init__()
        self.image_dir = image_dir
        self.label_dir = label_dir
        self.output_image_dir = output_image_dir
        self.output_label_dir = output_label_dir
        self.transforms = transforms
    
    def run(self):
        """执行数据增强"""
        success, failed, errors = data_augmentation_service.augment_dataset(
            self.image_dir,
            self.label_dir,
            self.output_image_dir,
            self.output_label_dir,
            self.transforms,
            progress_callback=self.progress.emit
        )
        self.finished.emit(success, failed, errors)

class DataAugmentationWindow(QMainWindow):
    """数据增强窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('数据增强工具')
        self.setGeometry(100, 100, 1000, 700)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        
        # 左侧配置面板
        left_panel = self.create_config_panel()
        main_layout.addWidget(left_panel, stretch=1)
        
        # 右侧监控面板
        right_panel = self.create_monitor_panel()
        main_layout.addWidget(right_panel, stretch=2)
        
        central_widget.setLayout(main_layout)
    
    def create_config_panel(self):
        """创建配置面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel('🎨 数据增强配置')
        title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 输入路径组
        input_group = QGroupBox('📁 输入路径')
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)
        
        # 图片文件夹
        input_layout.addWidget(QLabel('图片文件夹:'))
        img_layout = QHBoxLayout()
        self.image_dir_input = QLineEdit()
        self.image_dir_input.setPlaceholderText('选择包含图片的文件夹')
        img_layout.addWidget(self.image_dir_input)
        browse_img_btn = QPushButton('浏览')
        browse_img_btn.clicked.connect(self.browse_image_dir)
        img_layout.addWidget(browse_img_btn)
        input_layout.addLayout(img_layout)
        
        # 标签文件夹
        input_layout.addWidget(QLabel('标签文件夹:'))
        label_layout = QHBoxLayout()
        self.label_dir_input = QLineEdit()
        self.label_dir_input.setPlaceholderText('选择包含标签的文件夹')
        label_layout.addWidget(self.label_dir_input)
        browse_label_btn = QPushButton('浏览')
        browse_label_btn.clicked.connect(self.browse_label_dir)
        label_layout.addWidget(browse_label_btn)
        input_layout.addLayout(label_layout)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 输出策略组
        output_group = QGroupBox('💾 输出策略')
        output_layout = QVBoxLayout()
        output_layout.setSpacing(8)
        
        self.output_btn_group = QButtonGroup()
        
        self.output_original_radio = QRadioButton('放回原文件夹（与原图混合）')
        self.output_btn_group.addButton(self.output_original_radio, 1)
        output_layout.addWidget(self.output_original_radio)
        
        self.output_default_radio = QRadioButton('默认路径（原文件夹下创建 augmented_images/ 和 augmented_labels/）')
        self.output_default_radio.setChecked(True)
        self.output_btn_group.addButton(self.output_default_radio, 2)
        output_layout.addWidget(self.output_default_radio)
        
        custom_layout = QHBoxLayout()
        self.output_custom_radio = QRadioButton('自定义:')
        self.output_btn_group.addButton(self.output_custom_radio, 3)
        custom_layout.addWidget(self.output_custom_radio)
        self.custom_output_input = QLineEdit()
        self.custom_output_input.setPlaceholderText('选择输出文件夹')
        self.custom_output_input.setEnabled(False)
        custom_layout.addWidget(self.custom_output_input)
        browse_custom_btn = QPushButton('浏览')
        browse_custom_btn.clicked.connect(self.browse_custom_output)
        custom_layout.addWidget(browse_custom_btn)
        output_layout.addLayout(custom_layout)
        
        self.output_custom_radio.toggled.connect(
            lambda checked: self.custom_output_input.setEnabled(checked)
        )
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # 变换选项组
        transform_group = QGroupBox('🔄 变换选项')
        transform_layout = QVBoxLayout()
        transform_layout.setSpacing(8)
        
        # 添加小标题
        geo_label = QLabel('📐 几何变换（修改标签坐标）')
        geo_label.setStyleSheet('font-weight: bold; color: #2c3e50;')
        transform_layout.addWidget(geo_label)
        
        self.horizontal_flip_cb = QCheckBox('↔ 水平翻转')
        self.horizontal_flip_cb.setChecked(True)
        transform_layout.addWidget(self.horizontal_flip_cb)
        
        self.vertical_flip_cb = QCheckBox('↕ 垂直翻转')
        self.vertical_flip_cb.setChecked(True)
        transform_layout.addWidget(self.vertical_flip_cb)
        
        self.rotate_90_cb = QCheckBox('↻ 旋转90度（逆时针）')
        self.rotate_90_cb.setChecked(True)
        transform_layout.addWidget(self.rotate_90_cb)
        
        self.rotate_180_cb = QCheckBox('⟲ 旋转180度')
        self.rotate_180_cb.setChecked(True)
        transform_layout.addWidget(self.rotate_180_cb)
        
        transform_layout.addSpacing(10)
        
        # 像素级变换
        pixel_label = QLabel('🎨 像素级变换（不修改标签）')
        pixel_label.setStyleSheet('font-weight: bold; color: #2c3e50;')
        transform_layout.addWidget(pixel_label)
        
        self.gaussian_noise_cb = QCheckBox('📊 高斯噪声')
        self.gaussian_noise_cb.setChecked(False)
        transform_layout.addWidget(self.gaussian_noise_cb)
        
        self.brightness_cb = QCheckBox('💡 亮度增强')
        self.brightness_cb.setChecked(False)
        transform_layout.addWidget(self.brightness_cb)
        
        self.contrast_cb = QCheckBox('🌗 对比度增强')
        self.contrast_cb.setChecked(False)
        transform_layout.addWidget(self.contrast_cb)
        
        self.gaussian_blur_cb = QCheckBox('🌫️ 高斯模糊')
        self.gaussian_blur_cb.setChecked(False)
        transform_layout.addWidget(self.gaussian_blur_cb)
        
        transform_group.setLayout(transform_layout)
        layout.addWidget(transform_group)
        
        # 控制按钮
        control_layout = QVBoxLayout()
        
        self.start_button = QPushButton('🚀 开始增强')
        self.start_button.clicked.connect(self.start_augmentation)
        self.start_button.setStyleSheet('background-color: #27ae60; color: white; padding: 10px; font-weight: bold;')
        control_layout.addWidget(self.start_button)
        
        self.cancel_button = QPushButton('⏹ 停止')
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet('background-color: #e74c3c; color: white; padding: 10px; font-weight: bold;')
        control_layout.addWidget(self.cancel_button)
        
        layout.addLayout(control_layout)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_monitor_panel(self):
        """创建监控面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 处理日志
        log_group = QGroupBox('处理日志')
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # 进度组
        progress_group = QGroupBox('处理进度')
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel('准备就绪')
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        panel.setLayout(layout)
        return panel
    
    def browse_image_dir(self):
        """浏览图片文件夹"""
        dir_path = QFileDialog.getExistingDirectory(self, '选择图片文件夹')
        if dir_path:
            self.image_dir_input.setText(dir_path)
    
    def browse_label_dir(self):
        """浏览标签文件夹"""
        dir_path = QFileDialog.getExistingDirectory(self, '选择标签文件夹')
        if dir_path:
            self.label_dir_input.setText(dir_path)
    
    def browse_custom_output(self):
        """浏览自定义输出文件夹"""
        dir_path = QFileDialog.getExistingDirectory(self, '选择输出文件夹')
        if dir_path:
            self.custom_output_input.setText(dir_path)
    
    def get_output_paths(self):
        """根据用户选择获取输出路径"""
        image_dir = self.image_dir_input.text()
        label_dir = self.label_dir_input.text()
        
        selected_option = self.output_btn_group.checkedId()
        
        if selected_option == 1:  # 放回原文件夹
            return image_dir, label_dir
        elif selected_option == 2:  # 默认路径
            output_image_dir = os.path.join(os.path.dirname(image_dir), 'augmented_images')
            output_label_dir = os.path.join(os.path.dirname(label_dir), 'augmented_labels')
            return output_image_dir, output_label_dir
        else:  # 自定义路径
            custom_path = self.custom_output_input.text()
            if not custom_path:
                return None, None
            output_image_dir = os.path.join(custom_path, 'images')
            output_label_dir = os.path.join(custom_path, 'labels')
            return output_image_dir, output_label_dir
    
    def start_augmentation(self):
        """开始数据增强"""
        # 验证输入
        image_dir = self.image_dir_input.text()
        label_dir = self.label_dir_input.text()
        
        if not image_dir or not label_dir:
            QMessageBox.warning(self, '警告', '请选择图片和标签文件夹')
            return
        
        if not os.path.exists(image_dir):
            QMessageBox.warning(self, '警告', '图片文件夹不存在')
            return
        
        if not os.path.exists(label_dir):
            QMessageBox.warning(self, '警告', '标签文件夹不存在')
            return
        
        # 获取输出路径
        output_image_dir, output_label_dir = self.get_output_paths()
        if output_image_dir is None or output_label_dir is None:
            QMessageBox.warning(self, '警告', '请选择或指定输出路径')
            return
        
        # 获取变换选项
        transforms = {
            'horizontal_flip': self.horizontal_flip_cb.isChecked(),
            'vertical_flip': self.vertical_flip_cb.isChecked(),
            'rotate_90': self.rotate_90_cb.isChecked(),
            'rotate_180': self.rotate_180_cb.isChecked(),
            'gaussian_noise': self.gaussian_noise_cb.isChecked(),
            'brightness': self.brightness_cb.isChecked(),
            'contrast': self.contrast_cb.isChecked(),
            'gaussian_blur': self.gaussian_blur_cb.isChecked()
        }
        
        if not any(transforms.values()):
            QMessageBox.warning(self, '警告', '请至少选择一种变换')
            return
        
        # 禁用控件
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText('处理中...')
        self.log_text.clear()
        self.log_text.append('开始数据增强...\n')
        
        # 创建并启动工作线程
        self.worker = AugmentationWorker(
            image_dir,
            label_dir,
            output_image_dir,
            output_label_dir,
            transforms
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.augmentation_finished)
        self.worker.start()
    
    def update_progress(self, current, total, message):
        """更新进度"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f'处理中: {current}/{total} ({progress}%)')
        self.log_text.append(f'[{current}/{total}] {message}')
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def augmentation_finished(self, success, failed, errors):
        """数据增强完成"""
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(100)
        self.progress_label.setText('完成')
        
        summary = f'\n✅ 数据增强完成！\n成功: {success} 个图片\n失败: {failed} 个图片'
        self.log_text.append(summary)
        
        if errors:
            self.log_text.append(f'\n错误详情（前10条）:')
            for error in errors[:10]:
                self.log_text.append(f'  - {error}')
        
        # 显示完成对话框
        QMessageBox.information(
            self, 
            '完成', 
            f'数据增强完成！\n\n成功: {success}\n失败: {failed}\n\n详细信息请查看日志。'
        )
