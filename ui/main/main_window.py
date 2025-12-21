"""
主界面 - 推理界面
提供实时/离线检测功能
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QSlider, QFileDialog,
                             QMessageBox, QGroupBox, QTextEdit, QSpinBox, QDoubleSpinBox,
                             QRadioButton, QButtonGroup, QToolBar, QFrame, QSizePolicy, QMenu,
                             QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QListWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QImage, QPixmap, QAction, QIcon
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
    
    # 添加切换账号信号
    logout_signal = pyqtSignal()
    
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
        
        # 创建顶部工具栏
        self.create_toolbar()
        
        # 隐藏默认菜单栏（菜单已集成到工具栏）
        self.menuBar().setVisible(False)
        
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
        
        # 加载模型列表
        self.load_model_list()
    
    def create_toolbar(self):
        """创建顶部工具栏（包含菜单）"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4facfe, stop:1 #00f2fe);
                border: none;
                padding: 8px;
                spacing: 10px;
            }
            QToolBar QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 15px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 5px;
            }
            QToolBar QPushButton {
                background-color: white;
                color: #4facfe;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QToolBar QPushButton:hover {
                background-color: #f0f8ff;
                color: #00f2fe;
            }
            QToolBar QPushButton#menu_btn {
                background-color: transparent;
                color: white;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QToolBar QPushButton#menu_btn:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QToolBar QLabel#role_badge {
                background: rgba(255, 215, 0, 0.9);
                color: #2c3e50;
                padding: 3px 10px;
                border-radius: 10px;
                font-size: 11px;
            }
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 30px 8px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #4facfe;
                color: white;
            }
        """)
        
        # 左侧：系统标题
        title_label = QLabel('🌊 水下目标识别系统')
        toolbar.addWidget(title_label)
        
        toolbar.addSeparator()
        
        # 菜单按钮区域
        # 视图菜单
        view_btn = QPushButton('👁️ 视图')
        view_btn.setObjectName('menu_btn')
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_menu = QMenu()
        
        # 全屏功能
        self.fullscreen_action = view_menu.addAction('🖼️ 全屏模式')
        self.fullscreen_action.setCheckable(True)
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)
        
        view_menu.addAction('📊 显示统计')
        
        # 主题设置
        theme_action = view_menu.addAction('🎨 主题设置')
        theme_action.triggered.connect(self.open_theme_settings)
        
        view_btn.setMenu(view_menu)
        toolbar.addWidget(view_btn)
        
        # 工具菜单
        tools_btn = QPushButton('🔧 工具')
        tools_btn.setObjectName('menu_btn')
        tools_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        tools_menu = QMenu()
        train_action = tools_menu.addAction('🎓 模型训练')
        train_action.triggered.connect(self.open_training_window)
        tools_menu.addAction('📦 模型仓库')
        register_action = tools_menu.addAction('➕ 注册模型')
        register_action.triggered.connect(self.register_model)
        tools_menu.addSeparator()
        if self.user_info.get('role') == 'admin':
            admin_action = tools_menu.addAction('👑 管理员仪表盘')
            admin_action.triggered.connect(self.open_admin_dashboard)
        tools_btn.setMenu(tools_menu)
        toolbar.addWidget(tools_btn)
        
        # 帮助菜单
        help_btn = QPushButton('❓ 帮助')
        help_btn.setObjectName('menu_btn')
        help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        help_menu = QMenu()
        about_action = help_menu.addAction('ℹ️ 关于系统')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction('📖 使用文档')
        help_menu.addAction('🐛 问题反馈')
        help_btn.setMenu(help_menu)
        toolbar.addWidget(help_btn)
        
        # 添加伸缩空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # 右侧：用户信息区域
        user_container = QWidget()
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(10)
        
        # 角色标识
        if self.user_info.get('role') == 'admin':
            role_badge = QLabel('👑 管理员')
            role_badge.setObjectName('role_badge')
            user_layout.addWidget(role_badge)
        
        # 用户名显示
        user_label = QLabel(f'👤 {self.user_info["username"]}')
        user_layout.addWidget(user_label)
        
        # 切换账号按钮
        switch_account_btn = QPushButton('🔄 切换账号')
        switch_account_btn.clicked.connect(self.switch_account)
        switch_account_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        user_layout.addWidget(switch_account_btn)
        
        # 退出按钮
        logout_btn = QPushButton('🚪 退出登录')
        logout_btn.clicked.connect(self.logout)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(231, 76, 60, 0.9);
                color: white;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        user_layout.addWidget(logout_btn)
        
        toolbar.addWidget(user_container)
        
        self.addToolBar(toolbar)
    
    def switch_account(self):
        """切换账号"""
        reply = QMessageBox.question(
            self, 
            '切换账号', 
            '确定要切换账号吗？\n当前工作将不会保存。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 停止正在进行的检测
            if self.inference_thread:
                self.stop_detection()
            
            # 发送登出信号
            self.logout_signal.emit()
            self.close()
    
    def logout(self):
        """退出登录"""
        reply = QMessageBox.question(
            self, 
            '退出登录', 
            '确定要退出系统吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 停止正在进行的检测
            if self.inference_thread:
                self.stop_detection()
            
            self.close()
            import sys
            sys.exit(0)
    
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
        """显示关于对话框"""
        QMessageBox.about(self, '关于', 
                         '水下目标识别系统 v1.0.0\n\n'
                         '基于 YOLOv11 + PyQt6 开发\n'
                         '支持实时/离线目标检测与模型训练')
    
    def toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_action.setChecked(False)
        else:
            self.showFullScreen()
            self.fullscreen_action.setChecked(True)
    
    def open_theme_settings(self):
        """打开主题设置对话框"""
        dialog = ThemeSettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            theme = dialog.get_selected_theme()
            self.apply_theme(theme)
    
    def apply_theme(self, theme_name):
        """应用主题"""
        themes = {
            'light': {
                'name': '浅色主题',
                'style': '''
                    QWidget {
                        background-color: #f5f5f5;
                        color: #333;
                    }
                    QGroupBox {
                        background-color: white;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        margin-top: 10px;
                        padding-top: 10px;
                        font-weight: bold;
                    }
                    QGroupBox::title {
                        color: #4facfe;
                    }
                    QPushButton {
                        background-color: #4facfe;
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #00f2fe;
                    }
                    QTextEdit {
                        background-color: white;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                    }
                '''
            },
            'dark': {
                'name': '深色主题',
                'style': '''
                    QWidget {
                        background-color: #2c3e50;
                        color: #ecf0f1;
                    }
                    QGroupBox {
                        background-color: #34495e;
                        border: 1px solid #4a5f7f;
                        border-radius: 5px;
                        margin-top: 10px;
                        padding-top: 10px;
                        font-weight: bold;
                    }
                    QGroupBox::title {
                        color: #3498db;
                    }
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                    QTextEdit {
                        background-color: #34495e;
                        border: 1px solid #4a5f7f;
                        border-radius: 5px;
                        color: #ecf0f1;
                    }
                    QLabel {
                        color: #ecf0f1;
                    }
                    QComboBox {
                        background-color: #34495e;
                        color: #ecf0f1;
                        border: 1px solid #4a5f7f;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QSlider::groove:horizontal {
                        background: #4a5f7f;
                        height: 8px;
                        border-radius: 4px;
                    }
                    QSlider::handle:horizontal {
                        background: #3498db;
                        width: 18px;
                        margin: -5px 0;
                        border-radius: 9px;
                    }
                '''
            },
            'ocean': {
                'name': '海洋主题',
                'style': '''
                    QWidget {
                        background-color: #e8f4f8;
                        color: #1a5490;
                    }
                    QGroupBox {
                        background-color: #d4eaf7;
                        border: 2px solid #4facfe;
                        border-radius: 8px;
                        margin-top: 10px;
                        padding-top: 10px;
                        font-weight: bold;
                    }
                    QGroupBox::title {
                        color: #00838f;
                    }
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #4facfe, stop:1 #00f2fe);
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #00f2fe, stop:1 #4facfe);
                    }
                    QTextEdit {
                        background-color: white;
                        border: 2px solid #b3e5fc;
                        border-radius: 5px;
                        color: #1a5490;
                    }
                '''
            }
        }
        
        if theme_name in themes:
            self.setStyleSheet(themes[theme_name]['style'])
            # 保存设置到配置文件
            config.SYSTEM_CONFIG['theme'] = theme_name
            QMessageBox.information(self, '成功', f'已切换到{themes[theme_name]["name"]}!')
    
    def register_model(self):
        """注册新模型"""
        dialog = ModelRegisterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 刷新模型列表
            self.load_model_list()
            QMessageBox.information(self, '成功', '模型注册成功！')


class ModelRegisterDialog(QDialog):
    """模型注册对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_file_path = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('注册新模型')
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # 表单布局
        form_layout = QFormLayout()
        
        # 模型名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('请输入模型名称，如: mine')
        form_layout.addRow('模型名称*:', self.name_input)
        
        # 版本号
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText('请输入版本号，如: 1.0')
        self.version_input.setText('1.0')
        form_layout.addRow('版本号*:', self.version_input)
        
        # 作者
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText('请输入作者名称')
        form_layout.addRow('作者:', self.author_input)
        
        # 描述
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText('请输入模型描述信息')
        self.description_input.setMaximumHeight(80)
        form_layout.addRow('描述:', self.description_input)
        
        # 类别列表
        self.classes_input = QLineEdit()
        self.classes_input.setPlaceholderText('用逗号分隔，如: fish,coral,turtle')
        self.classes_input.setText('fish,coral,turtle,shark,jellyfish,dolphin,submarine,diver')
        form_layout.addRow('检测类别:', self.classes_input)
        
        # 模型文件选择
        file_layout = QHBoxLayout()
        self.file_label = QLabel('未选择文件')
        file_layout.addWidget(self.file_label)
        
        browse_btn = QPushButton('浏览...')
        browse_btn.clicked.connect(self.select_model_file)
        file_layout.addWidget(browse_btn)
        
        file_widget = QWidget()
        file_widget.setLayout(file_layout)
        form_layout.addRow('模型文件*:', file_widget)
        
        layout.addLayout(form_layout)
        
        # 提示信息
        tip_label = QLabel('提示: 带 * 的字段为必填项')
        tip_label.setStyleSheet('color: #7f8c8d; font-size: 11px; padding: 5px;')
        layout.addWidget(tip_label)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def select_model_file(self):
        """选择模型文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择模型文件', 
            str(config.MODELS_DIR),
            'PyTorch Models (*.pt *.pth);;All Files (*)'
        )
        
        if file_path:
            self.model_file_path = file_path
            self.file_label.setText(Path(file_path).name)
            
            # 如果模型名称为空，自动填充
            if not self.name_input.text():
                model_name = Path(file_path).stem
                self.name_input.setText(model_name)
    
    def validate_and_accept(self):
        """验证并接受"""
        # 验证必填字段
        name = self.name_input.text().strip()
        version = self.version_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, '警告', '请输入模型名称！')
            return
        
        if not version:
            QMessageBox.warning(self, '警告', '请输入版本号！')
            return
        
        if not self.model_file_path:
            QMessageBox.warning(self, '警告', '请选择模型文件！')
            return
        
        # 检查模型文件是否存在
        if not Path(self.model_file_path).exists():
            QMessageBox.warning(self, '警告', '所选模型文件不存在！')
            return
        
        # 解析类别列表
        classes_text = self.classes_input.text().strip()
        classes = [c.strip() for c in classes_text.split(',') if c.strip()] if classes_text else None
        
        # 获取其他字段
        author = self.author_input.text().strip() or None
        description = self.description_input.toPlainText().strip() or None
        
        # 注册模型
        try:
            success = model_manager.add_model(
                name=name,
                version=version,
                file_path=self.model_file_path,
                classes=classes,
                description=description,
                author=author
            )
            
            if success:
                self.accept()
            else:
                QMessageBox.critical(self, '错误', '模型注册失败！请检查日志获取详细信息。')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'模型注册失败：{str(e)}')


class ThemeSettingsDialog(QDialog):
    """主题设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_theme = 'light'
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('🎨 主题设置')
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel('选择主题')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold; padding: 10px;')
        layout.addWidget(title_label)
        
        # 主题列表
        self.theme_list = QListWidget()
        self.theme_list.setStyleSheet('''
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 15px;
                border-radius: 5px;
                margin: 3px;
            }
            QListWidget::item:selected {
                background-color: #4facfe;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
        ''')
        
        # 添加主题选项
        themes = [
            ('🌞 浅色主题', 'light', '清新明亮，适合白天使用'),
            ('🌙 深色主题', 'dark', '柔和护眼，适合晚上使用'),
            ('🌊 海洋主题', 'ocean', '清凉温馨，水下专属主题')
        ]
        
        for icon_name, theme_id, description in themes:
            item_text = f"{icon_name}\n{description}"
            self.theme_list.addItem(item_text)
            self.theme_list.item(self.theme_list.count() - 1).setData(Qt.ItemDataRole.UserRole, theme_id)
        
        # 默认选中第一个
        self.theme_list.setCurrentRow(0)
        self.theme_list.currentRowChanged.connect(self.on_theme_changed)
        
        layout.addWidget(self.theme_list)
        
        # 预览提示
        preview_label = QLabel('👁️ 选择后点击确定即可应用主题')
        preview_label.setStyleSheet('color: #7f8c8d; font-size: 12px; padding: 10px;')
        layout.addWidget(preview_label)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def on_theme_changed(self, index):
        """主题选择改变"""
        if index >= 0:
            item = self.theme_list.item(index)
            self.selected_theme = item.data(Qt.ItemDataRole.UserRole)
    
    def get_selected_theme(self):
        """获取选中的主题"""
        return self.selected_theme
