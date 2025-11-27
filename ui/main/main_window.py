"""
主界面 - 推理界面
提供实时/离线检测功能
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QSlider, QFileDialog,
                             QMessageBox, QGroupBox, QTextEdit, QSpinBox, QDoubleSpinBox,
                             QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
from services import inference_engine, model_manager
import config
from pathlib import Path

class InferenceThread(QThread):
    """推理线程"""
    frame_ready = pyqtSignal(np.ndarray, list, float)
    finished = pyqtSignal()
    
    def __init__(self, source_type, source, inference_engine):
        super().__init__()
        self.source_type = source_type
        self.source = source
        self.engine = inference_engine
        self.running = True
    
    def run(self):
        """执行推理"""
        if self.source_type == 'camera':
            self.engine.predict_camera(self.source, self.callback)
        elif self.source_type == 'video':
            self.engine.predict_video(self.source, callback=self.callback)
        self.finished.emit()
    
    def callback(self, frame, detections, fps):
        """回调函数"""
        if self.running:
            self.frame_ready.emit(frame, detections, fps)
            return True
        return False
    
    def stop(self):
        """停止推理"""
        self.running = False

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.current_model = None
        self.inference_thread = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f'水下目标识别系统 - {self.user_info["username"]}')
        self.setGeometry(50, 50, 1400, 800)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        
        # 左侧控制面板
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, stretch=1)
        
        # 右侧显示区域
        right_panel = self.create_display_panel()
        main_layout.addWidget(right_panel, stretch=3)
        
        central_widget.setLayout(main_layout)
        
        # 菜单栏
        self.create_menu_bar()
        
        # 加载模型列表
        self.load_model_list()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        # 训练菜单
        train_action = tools_menu.addAction('模型训练')
        train_action.triggered.connect(self.open_training_window)
        
        # 如果是管理员，添加管理菜单
        if self.user_info.get('role') == 'admin':
            admin_menu = menubar.addMenu('管理')
            dashboard_action = admin_menu.addAction('管理员仪表盘')
            dashboard_action.triggered.connect(self.open_admin_dashboard)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        about_action = help_menu.addAction('关于')
        about_action.triggered.connect(self.show_about)
    
    def create_control_panel(self):
        """创建控制面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 模型选择
        model_group = QGroupBox('模型配置')
        model_layout = QVBoxLayout()
        
        model_layout.addWidget(QLabel('选择模型：'))
        self.model_combo = QComboBox()
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        model_layout.addWidget(self.model_combo)
        
        load_model_btn = QPushButton('加载模型')
        load_model_btn.clicked.connect(self.load_model)
        model_layout.addWidget(load_model_btn)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # 参数设置
        param_group = QGroupBox('参数设置')
        param_layout = QVBoxLayout()
        
        # 置信度阈值
        param_layout.addWidget(QLabel('置信度阈值：'))
        conf_layout = QHBoxLayout()
        self.conf_slider = QSlider(Qt.Orientation.Horizontal)
        self.conf_slider.setMinimum(1)
        self.conf_slider.setMaximum(100)
        self.conf_slider.setValue(int(config.YOLO_CONFIG['conf_threshold'] * 100))
        self.conf_slider.valueChanged.connect(self.update_conf_label)
        conf_layout.addWidget(self.conf_slider)
        
        self.conf_label = QLabel(f"{config.YOLO_CONFIG['conf_threshold']:.2f}")
        conf_layout.addWidget(self.conf_label)
        param_layout.addLayout(conf_layout)
        
        # IOU阈值
        param_layout.addWidget(QLabel('IOU阈值：'))
        iou_layout = QHBoxLayout()
        self.iou_slider = QSlider(Qt.Orientation.Horizontal)
        self.iou_slider.setMinimum(1)
        self.iou_slider.setMaximum(100)
        self.iou_slider.setValue(int(config.YOLO_CONFIG['iou_threshold'] * 100))
        self.iou_slider.valueChanged.connect(self.update_iou_label)
        iou_layout.addWidget(self.iou_slider)
        
        self.iou_label = QLabel(f"{config.YOLO_CONFIG['iou_threshold']:.2f}")
        iou_layout.addWidget(self.iou_label)
        param_layout.addLayout(iou_layout)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # 数据源选择
        source_group = QGroupBox('数据源')
        source_layout = QVBoxLayout()
        
        self.source_button_group = QButtonGroup()
        
        self.camera_radio = QRadioButton('摄像头')
        self.camera_radio.setChecked(True)
        self.source_button_group.addButton(self.camera_radio)
        source_layout.addWidget(self.camera_radio)
        
        self.image_radio = QRadioButton('图片')
        self.source_button_group.addButton(self.image_radio)
        source_layout.addWidget(self.image_radio)
        
        self.video_radio = QRadioButton('视频')
        self.source_button_group.addButton(self.video_radio)
        source_layout.addWidget(self.video_radio)
        
        # 文件选择
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel('未选择文件')
        file_layout.addWidget(self.file_path_label)
        
        select_file_btn = QPushButton('浏览')
        select_file_btn.clicked.connect(self.select_source_file)
        file_layout.addWidget(select_file_btn)
        source_layout.addLayout(file_layout)
        
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # 控制按钮
        control_layout = QVBoxLayout()
        
        self.start_btn = QPushButton('▶ 开始检测')
        self.start_btn.clicked.connect(self.start_detection)
        self.start_btn.setStyleSheet('background-color: #27ae60; color: white; padding: 10px; font-weight: bold;')
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton('⏹ 停止检测')
        self.stop_btn.clicked.connect(self.stop_detection)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet('background-color: #e74c3c; color: white; padding: 10px; font-weight: bold;')
        control_layout.addWidget(self.stop_btn)
        
        self.save_btn = QPushButton('💾 保存结果')
        self.save_btn.clicked.connect(self.save_result)
        control_layout.addWidget(self.save_btn)
        
        layout.addLayout(control_layout)
        
        # 统计信息
        stats_group = QGroupBox('统计信息')
        stats_layout = QVBoxLayout()
        
        self.fps_label = QLabel('FPS: 0.0')
        stats_layout.addWidget(self.fps_label)
        
        self.detection_count_label = QLabel('检测数: 0')
        stats_layout.addWidget(self.detection_count_label)
        
        self.inference_time_label = QLabel('推理时间: 0.0ms')
        stats_layout.addWidget(self.inference_time_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_display_panel(self):
        """创建显示面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 图像显示区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet('background-color: #2c3e50; border: 2px solid #34495e;')
        self.image_label.setMinimumSize(800, 600)
        self.image_label.setText('请选择数据源并开始检测')
        self.image_label.setStyleSheet('background-color: #2c3e50; color: white; font-size: 16px;')
        layout.addWidget(self.image_label)
        
        # 检测结果显示
        result_group = QGroupBox('检测结果')
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        result_layout.addWidget(self.result_text)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        panel.setLayout(layout)
        return panel
    
    def load_model_list(self):
        """加载模型列表"""
        self.model_combo.clear()
        models = model_manager.get_all_models()
        
        for model in models:
            self.model_combo.addItem(f"{model['name']} (v{model['version']})", model['id'])
        
        if self.model_combo.count() == 0:
            self.model_combo.addItem('暂无可用模型', None)
    
    def on_model_changed(self, index):
        """模型选择改变"""
        self.current_model = self.model_combo.currentData()
    
    def load_model(self):
        """加载模型"""
        if not self.current_model:
            QMessageBox.warning(self, '警告', '请先选择模型')
            return
        
        model_info = model_manager.get_model_by_id(self.current_model)
        if model_info:
            success = inference_engine.load_model(model_info['file_path'])
            if success:
                QMessageBox.information(self, '成功', f'模型加载成功: {model_info["name"]}')
            else:
                QMessageBox.critical(self, '错误', '模型加载失败')
    
    def update_conf_label(self, value):
        """更新置信度标签"""
        conf = value / 100.0
        self.conf_label.setText(f'{conf:.2f}')
        inference_engine.set_parameters(conf_threshold=conf)
    
    def update_iou_label(self, value):
        """更新IOU标签"""
        iou = value / 100.0
        self.iou_label.setText(f'{iou:.2f}')
        inference_engine.set_parameters(iou_threshold=iou)
    
    def select_source_file(self):
        """选择源文件"""
        if self.image_radio.isChecked():
            file_path, _ = QFileDialog.getOpenFileName(self, '选择图片', '', 
                                                       'Images (*.png *.jpg *.jpeg *.bmp)')
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, '选择视频', '', 
                                                       'Videos (*.mp4 *.avi *.mov)')
        
        if file_path:
            self.file_path_label.setText(Path(file_path).name)
            self.file_path_label.setProperty('full_path', file_path)
    
    def start_detection(self):
        """开始检测"""
        if not inference_engine.model:
            QMessageBox.warning(self, '警告', '请先加载模型')
            return
        
        if self.camera_radio.isChecked():
            # 摄像头检测
            self.inference_thread = InferenceThread('camera', 0, inference_engine)
            self.inference_thread.frame_ready.connect(self.update_frame)
            self.inference_thread.finished.connect(self.detection_finished)
            self.inference_thread.start()
            
        elif self.image_radio.isChecked():
            # 图片检测
            file_path = self.file_path_label.property('full_path')
            if not file_path:
                QMessageBox.warning(self, '警告', '请先选择图片')
                return
            
            result = inference_engine.predict_image(file_path)
            if result['success']:
                self.display_image_result(result)
            
        elif self.video_radio.isChecked():
            # 视频检测
            file_path = self.file_path_label.property('full_path')
            if not file_path:
                QMessageBox.warning(self, '警告', '请先选择视频')
                return
            
            self.inference_thread = InferenceThread('video', file_path, inference_engine)
            self.inference_thread.frame_ready.connect(self.update_frame)
            self.inference_thread.finished.connect(self.detection_finished)
            self.inference_thread.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
    
    def stop_detection(self):
        """停止检测"""
        if self.inference_thread:
            self.inference_thread.stop()
            self.inference_thread.wait()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def update_frame(self, frame, detections, fps):
        """更新帧显示"""
        # 转换为QImage
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
        
        # 缩放显示
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
        
        # 更新统计
        self.fps_label.setText(f'FPS: {fps:.1f}')
        self.detection_count_label.setText(f'检测数: {len(detections)}')
        
        # 更新检测结果
        result_text = '\n'.join([f"{det['class_name']}: {det['confidence']:.2f}" for det in detections])
        self.result_text.setText(result_text)
    
    def display_image_result(self, result):
        """显示图片检测结果"""
        frame = result['image']
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
        
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
        
        # 更新统计
        self.detection_count_label.setText(f'检测数: {len(result["detections"])}')
        self.inference_time_label.setText(f'推理时间: {result["inference_time"]*1000:.1f}ms')
        
        # 显示结果
        result_text = '\n'.join([f"{det['class_name']}: {det['confidence']:.2f}" 
                                for det in result['detections']])
        self.result_text.setText(result_text)
    
    def detection_finished(self):
        """检测完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def save_result(self):
        """保存结果"""
        file_path, _ = QFileDialog.getSaveFileName(self, '保存结果', '', 
                                                   'Images (*.jpg);;Videos (*.mp4)')
        if file_path:
            QMessageBox.information(self, '成功', f'结果已保存: {file_path}')
    
    def open_training_window(self):
        """打开训练窗口"""
        from ui.training import TrainingWindow
        self.training_window = TrainingWindow(self.user_info)
        self.training_window.show()
    
    def open_admin_dashboard(self):
        """打开管理员仪表盘"""
        from ui.admin import AdminDashboard
        self.admin_dashboard = AdminDashboard(self.user_info)
        self.admin_dashboard.show()
    
    def show_about(self):
        """显示关于信息"""
        QMessageBox.about(self, '关于', 
                         '水下目标识别系统 v1.0.0\n\n'
                         '基于 YOLOv11 + PyQt6 开发\n'
                         '支持实时/离线目标检测与模型训练')
