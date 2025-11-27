"""
训练管理界面
提供模型训练、监控功能
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
                             QFileDialog, QMessageBox, QGroupBox, QTextEdit, QProgressBar,
                             QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from services import training_service, model_manager
import config
from pathlib import Path

class TrainingThread(QThread):
    """训练线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    
    def __init__(self, data_yaml, epochs, batch_size, img_size, lr, project_name, user_id):
        super().__init__()
        self.data_yaml = data_yaml
        self.epochs = epochs
        self.batch_size = batch_size
        self.img_size = img_size
        self.lr = lr
        self.project_name = project_name
        self.user_id = user_id
    
    def run(self):
        """执行训练"""
        self.progress.emit('正在准备训练...')
        
        # 准备模型
        if not training_service.prepare_training():
            self.finished.emit({'success': False, 'error': '模型准备失败'})
            return
        
        self.progress.emit('训练开始...')
        
        # 开始训练
        result = training_service.start_training(
            data_yaml=self.data_yaml,
            epochs=self.epochs,
            batch_size=self.batch_size,
            img_size=self.img_size,
            lr=self.lr,
            project_name=self.project_name,
            user_id=self.user_id
        )
        
        self.finished.emit(result)

class TrainingWindow(QMainWindow):
    """训练窗口类"""
    
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.training_thread = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('模型训练管理')
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
        
        # 加载训练历史
        self.load_training_history()
    
    def create_config_panel(self):
        """创建配置面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel('🎓 模型训练配置')
        title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 数据集配置
        dataset_group = QGroupBox('数据集配置')
        dataset_layout = QVBoxLayout()
        
        dataset_layout.addWidget(QLabel('数据集路径：'))
        dataset_path_layout = QHBoxLayout()
        self.dataset_path_input = QLineEdit()
        self.dataset_path_input.setPlaceholderText('选择数据集目录')
        dataset_path_layout.addWidget(self.dataset_path_input)
        
        browse_dataset_btn = QPushButton('浏览')
        browse_dataset_btn.clicked.connect(self.select_dataset)
        dataset_path_layout.addWidget(browse_dataset_btn)
        dataset_layout.addLayout(dataset_path_layout)
        
        dataset_layout.addWidget(QLabel('训练集路径（相对）：'))
        self.train_path_input = QLineEdit()
        self.train_path_input.setPlaceholderText('例: images/train')
        self.train_path_input.setText('images/train')
        dataset_layout.addWidget(self.train_path_input)
        
        dataset_layout.addWidget(QLabel('验证集路径（相对）：'))
        self.val_path_input = QLineEdit()
        self.val_path_input.setPlaceholderText('例: images/val')
        self.val_path_input.setText('images/val')
        dataset_layout.addWidget(self.val_path_input)
        
        dataset_layout.addWidget(QLabel('类别名称（逗号分隔）：'))
        self.classes_input = QLineEdit()
        self.classes_input.setPlaceholderText('fish,coral,turtle,...')
        self.classes_input.setText(','.join(config.YOLO_CONFIG['classes']))
        dataset_layout.addWidget(self.classes_input)
        
        dataset_group.setLayout(dataset_layout)
        layout.addWidget(dataset_group)
        
        # 训练参数
        param_group = QGroupBox('训练参数')
        param_layout = QVBoxLayout()
        
        # Epochs
        epochs_layout = QHBoxLayout()
        epochs_layout.addWidget(QLabel('训练轮数 (Epochs)：'))
        self.epochs_input = QSpinBox()
        self.epochs_input.setMinimum(1)
        self.epochs_input.setMaximum(1000)
        self.epochs_input.setValue(config.TRAINING_CONFIG['epochs'])
        epochs_layout.addWidget(self.epochs_input)
        param_layout.addLayout(epochs_layout)
        
        # Batch Size
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel('批次大小 (Batch Size)：'))
        self.batch_input = QSpinBox()
        self.batch_input.setMinimum(1)
        self.batch_input.setMaximum(128)
        self.batch_input.setValue(config.TRAINING_CONFIG['batch_size'])
        batch_layout.addWidget(self.batch_input)
        param_layout.addLayout(batch_layout)
        
        # Image Size
        img_size_layout = QHBoxLayout()
        img_size_layout.addWidget(QLabel('图像大小：'))
        self.img_size_input = QSpinBox()
        self.img_size_input.setMinimum(320)
        self.img_size_input.setMaximum(1280)
        self.img_size_input.setSingleStep(32)
        self.img_size_input.setValue(config.TRAINING_CONFIG['img_size'])
        img_size_layout.addWidget(self.img_size_input)
        param_layout.addLayout(img_size_layout)
        
        # Learning Rate
        lr_layout = QHBoxLayout()
        lr_layout.addWidget(QLabel('学习率 (Learning Rate)：'))
        self.lr_input = QDoubleSpinBox()
        self.lr_input.setDecimals(4)
        self.lr_input.setMinimum(0.0001)
        self.lr_input.setMaximum(0.1)
        self.lr_input.setSingleStep(0.001)
        self.lr_input.setValue(config.TRAINING_CONFIG['lr'])
        lr_layout.addWidget(self.lr_input)
        param_layout.addLayout(lr_layout)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # 项目设置
        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel('项目名称：'))
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText('underwater_model')
        self.project_name_input.setText('underwater_model')
        project_layout.addWidget(self.project_name_input)
        layout.addLayout(project_layout)
        
        # 控制按钮
        control_layout = QVBoxLayout()
        
        self.start_train_btn = QPushButton('🚀 开始训练')
        self.start_train_btn.clicked.connect(self.start_training)
        self.start_train_btn.setStyleSheet('background-color: #27ae60; color: white; padding: 10px; font-weight: bold;')
        control_layout.addWidget(self.start_train_btn)
        
        self.stop_train_btn = QPushButton('⏹ 停止训练')
        self.stop_train_btn.clicked.connect(self.stop_training)
        self.stop_train_btn.setEnabled(False)
        self.stop_train_btn.setStyleSheet('background-color: #e74c3c; color: white; padding: 10px; font-weight: bold;')
        control_layout.addWidget(self.stop_train_btn)
        
        layout.addLayout(control_layout)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_monitor_panel(self):
        """创建监控面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 训练日志
        log_group = QGroupBox('训练日志')
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # 进度条
        progress_group = QGroupBox('训练进度')
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel('准备就绪')
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 训练历史
        history_group = QGroupBox('训练历史')
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(['ID', '模型', 'Epochs', 'Batch', '状态', '开始时间'])
        history_layout.addWidget(self.history_table)
        
        refresh_btn = QPushButton('刷新历史')
        refresh_btn.clicked.connect(self.load_training_history)
        history_layout.addWidget(refresh_btn)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        panel.setLayout(layout)
        return panel
    
    def select_dataset(self):
        """选择数据集"""
        dir_path = QFileDialog.getExistingDirectory(self, '选择数据集目录')
        if dir_path:
            self.dataset_path_input.setText(dir_path)
    
    def start_training(self):
        """开始训练"""
        # 验证输入
        dataset_path = self.dataset_path_input.text().strip()
        if not dataset_path:
            QMessageBox.warning(self, '警告', '请选择数据集路径')
            return
        
        # 创建数据集配置
        classes = [c.strip() for c in self.classes_input.text().split(',')]
        train_path = self.train_path_input.text().strip()
        val_path = self.val_path_input.text().strip()
        
        data_yaml = training_service.create_dataset_yaml(
            dataset_path=dataset_path,
            class_names=classes,
            train_path=train_path,
            val_path=val_path
        )
        
        # 获取训练参数
        epochs = self.epochs_input.value()
        batch_size = self.batch_input.value()
        img_size = self.img_size_input.value()
        lr = self.lr_input.value()
        project_name = self.project_name_input.text().strip()
        
        # 创建训练线程
        self.training_thread = TrainingThread(
            data_yaml=data_yaml,
            epochs=epochs,
            batch_size=batch_size,
            img_size=img_size,
            lr=lr,
            project_name=project_name,
            user_id=self.user_info['id']
        )
        
        self.training_thread.progress.connect(self.update_progress)
        self.training_thread.finished.connect(self.training_finished)
        
        # 更新UI状态
        self.start_train_btn.setEnabled(False)
        self.stop_train_btn.setEnabled(True)
        self.log_text.clear()
        self.log_text.append('=== 训练开始 ===\n')
        
        # 开始训练
        self.training_thread.start()
    
    def stop_training(self):
        """停止训练"""
        if self.training_thread:
            training_service.stop_training()
            self.log_text.append('\n[系统] 正在停止训练...')
    
    def update_progress(self, message):
        """更新进度"""
        self.log_text.append(f'[进度] {message}')
        self.progress_label.setText(message)
    
    def training_finished(self, result):
        """训练完成"""
        self.start_train_btn.setEnabled(True)
        self.stop_train_btn.setEnabled(False)
        
        if result['success']:
            self.log_text.append(f'\n=== 训练完成 ===')
            self.log_text.append(f'mAP: {result.get("final_map", 0):.4f}')
            self.log_text.append(f'权重保存: {result.get("weights_path", "N/A")}')
            self.progress_bar.setValue(100)
            
            QMessageBox.information(self, '成功', 
                                   f'训练完成！\nmAP: {result.get("final_map", 0):.4f}')
            
            # 刷新历史
            self.load_training_history()
        else:
            self.log_text.append(f'\n=== 训练失败 ===')
            self.log_text.append(f'错误: {result.get("error", "未知错误")}')
            QMessageBox.critical(self, '错误', f'训练失败: {result.get("error", "未知错误")}')
    
    def load_training_history(self):
        """加载训练历史"""
        logs = training_service.get_training_logs(user_id=self.user_info['id'])
        self.history_table.setRowCount(len(logs))
        
        for i, log in enumerate(logs):
            self.history_table.setItem(i, 0, QTableWidgetItem(str(log['id'])))
            self.history_table.setItem(i, 1, QTableWidgetItem(log.get('model_name', '')))
            self.history_table.setItem(i, 2, QTableWidgetItem(str(log.get('epochs', 0))))
            self.history_table.setItem(i, 3, QTableWidgetItem(str(log.get('batch_size', 0))))
            self.history_table.setItem(i, 4, QTableWidgetItem(log.get('status', '')))
            self.history_table.setItem(i, 5, QTableWidgetItem(str(log.get('start_time', ''))))
