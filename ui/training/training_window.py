"""
训练管理界面
提供模型训练、监控功能
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
                             QFileDialog, QMessageBox, QGroupBox, QTextEdit, QProgressBar,
                             QTableWidget, QTableWidgetItem, QComboBox, QDialog, QFormLayout, 
                             QDialogButtonBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from services import training_service, model_manager
import config
from pathlib import Path

class TrainingThread(QThread):
    """训练线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    
    def __init__(self, base_model, data_yaml, epochs, batch_size, img_size, lr, project_name, user_id):
        super().__init__()
        self.base_model = base_model
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
        if not training_service.prepare_training(self.base_model):
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
        
        # 基础模型选择
        model_group = QGroupBox('基础模型')
        model_layout = QVBoxLayout()
        
        model_layout.addWidget(QLabel('选择基础模型：'))
        self.base_model_combo = QComboBox()
        self.base_model_combo.currentIndexChanged.connect(self.on_base_model_changed)
        self.load_available_models()
        model_layout.addWidget(self.base_model_combo)
        
        refresh_models_btn = QPushButton('🔄 刷新模型列表')
        refresh_models_btn.clicked.connect(self.load_available_models)
        model_layout.addWidget(refresh_models_btn)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
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
        
        # 历史操作按钮
        history_btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton('🔄 刷新历史')
        refresh_btn.clicked.connect(self.load_training_history)
        history_btn_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton('🗑️ 删除选中')
        delete_btn.clicked.connect(self.delete_training_history)
        delete_btn.setStyleSheet('background-color: #e74c3c; color: white;')
        history_btn_layout.addWidget(delete_btn)
        
        clear_all_btn = QPushButton('🗑️ 清空全部')
        clear_all_btn.clicked.connect(self.clear_all_history)
        clear_all_btn.setStyleSheet('background-color: #c0392b; color: white;')
        history_btn_layout.addWidget(clear_all_btn)
        
        history_layout.addLayout(history_btn_layout)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        panel.setLayout(layout)
        return panel
    
    def select_dataset(self):
        """选择数据集"""
        dir_path = QFileDialog.getExistingDirectory(self, '选择数据集目录')
        if dir_path:
            self.dataset_path_input.setText(dir_path)
    
    def load_available_models(self):
        """加载可用模型列表"""
        self.base_model_combo.clear()
        
        # 获取所有已注册的模型
        models = model_manager.get_all_models()
        
        if models:
            for model in models:
                display_text = f"{model['name']} (v{model['version']})"
                # 存储完整的模型信息
                self.base_model_combo.addItem(display_text, model)
            # 只在log_text存在时才记录日志
            if hasattr(self, 'log_text'):
                self.log_text.append(f"[系统] 已加载 {len(models)} 个可用模型")
        else:
            self.base_model_combo.addItem('无可用模型', None)
            if hasattr(self, 'log_text'):
                self.log_text.append("[警告] 未找到已注册的模型，请先注册模型")
    
    def on_base_model_changed(self, index):
        """基础模型改变时，自动加载类别信息"""
        # 检查classes_input是否已经创建
        if not hasattr(self, 'classes_input'):
            return
        
        model_info = self.base_model_combo.currentData()
        if model_info and isinstance(model_info, dict):
            # 从模型信息中获取类别列表
            classes = model_info.get('classes', [])
            if classes:
                # 更新类别输入框
                self.classes_input.setText(','.join(classes))
                if hasattr(self, 'log_text'):
                    self.log_text.append(f"[系统] 已从模型 '{model_info['name']}' 加载 {len(classes)} 个类别")
    
    def start_training(self):
        """开始训练"""
        # 验证输入
        dataset_path = self.dataset_path_input.text().strip()
        if not dataset_path:
            QMessageBox.warning(self, '警告', '请选择数据集路径')
            return
        
        # 获取选中的模型
        model_info = self.base_model_combo.currentData()
        if not model_info or not isinstance(model_info, dict):
            QMessageBox.warning(self, '警告', '请先注册模型或选择一个可用模型')
            return
        
        base_model = model_info.get('file_path')
        if not base_model:
            QMessageBox.warning(self, '警告', '所选模型文件路径无效')
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
            base_model=base_model,
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
        self.log_text.append('=== 训练开始 ===')
        self.log_text.append(f'基础模型: {self.base_model_combo.currentText()}')
        self.log_text.append(f'数据集: {dataset_path}')
        self.log_text.append(f'训练轮数: {epochs}')
        self.log_text.append('')
        
        # 开始训练
        self.training_thread.start()
    
    def stop_training(self):
        """停止训练"""
        if self.training_thread and self.training_thread.isRunning():
            reply = QMessageBox.question(
                self,
                '确认停止',
                '确定要停止当前训练吗？\n\n'
                '注意：由于 YOLO 训练机制限制，\n'
                '停止可能需要等待当前 epoch 完成。',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                training_service.stop_training()
                self.log_text.append('\n[系统] 正在停止训练...')
                self.log_text.append('[提示] 请等待当前 epoch 完成，训练将保留已训练的权重')
                
                # 尝试终止线程（强制停止）
                self.training_thread.stop()
                # 给予一些时间让线程自然结束
                self.training_thread.wait(5000)  # 等待5秒
                
                if self.training_thread.isRunning():
                    # 如果还在运行，强制终止
                    self.training_thread.terminate()
                    self.training_thread.wait()
                    self.log_text.append('[警告] 已强制终止训练进程')
                
                self.start_train_btn.setEnabled(True)
                self.stop_train_btn.setEnabled(False)
                self.log_text.append('[系统] 训练已停止')
    
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
            
            # 刷新历史
            self.load_training_history()
            
            # 提示是否保存模型
            weights_path = result.get('weights_path')
            if weights_path:
                reply = QMessageBox.question(
                    self,
                    '训练完成',
                    f'训练完成！\nmAP: {result.get("final_map", 0):.4f}\n\n'
                    f'是否将训练好的模型保存到模型管理器？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.save_trained_model_dialog(weights_path)
            else:
                QMessageBox.information(self, '成功', 
                                       f'训练完成！\nmAP: {result.get("final_map", 0):.4f}')
        else:
            self.log_text.append(f'\n=== 训练失败 ===')
            self.log_text.append(f'错误: {result.get("error", "未知错误")}')
            QMessageBox.critical(self, '错误', f'训练失败: {result.get("error", "未知错误")}')
    
    def save_trained_model_dialog(self, weights_path):
        """保存训练好的模型对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle('保存训练模型')
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # 模型名称
        name_input = QLineEdit()
        name_input.setPlaceholderText('请输入模型名称')
        name_input.setText(self.project_name_input.text() or 'trained_model')
        form_layout.addRow('模型名称*:', name_input)
        
        # 版本号
        version_input = QLineEdit()
        version_input.setPlaceholderText('请输入版本号')
        version_input.setText('1.0')
        form_layout.addRow('版本号*:', version_input)
        
        # 作者
        author_input = QLineEdit()
        author_input.setPlaceholderText('请输入作者名称')
        author_input.setText(self.user_info.get('username', ''))
        form_layout.addRow('作者:', author_input)
        
        # 描述
        desc_input = QTextEdit()
        desc_input.setPlaceholderText('请输入模型描述')
        desc_input.setMaximumHeight(80)
        form_layout.addRow('描述:', desc_input)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_input.text().strip()
            version = version_input.text().strip()
            author = author_input.text().strip() or None
            description = desc_input.toPlainText().strip() or None
            
            if not name or not version:
                QMessageBox.warning(self, '警告', '请填写模型名称和版本号！')
                return
            
            # 获取类别列表
            classes = [c.strip() for c in self.classes_input.text().split(',')]
            
            # 保存模型
            success = training_service.save_trained_model(
                weights_path=weights_path,
                model_name=name,
                version=version,
                classes=classes,
                description=description,
                author=author
            )
            
            if success:
                QMessageBox.information(self, '成功', f'模型已保存：{name} v{version}')
                self.log_text.append(f'\n[系统] 模型已保存到模型管理器: {name} v{version}')
                # 刷新模型列表
                self.load_available_models()
            else:
                QMessageBox.critical(self, '错误', '模型保存失败！')
    
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
    
    def delete_training_history(self):
        """删除选中的训练历史"""
        selected_rows = self.history_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, '警告', '请先选择要删除的历史记录')
            return
        
        # 获取选中的ID列表
        log_ids = []
        for row in selected_rows:
            id_item = self.history_table.item(row.row(), 0)
            if id_item:
                log_ids.append(int(id_item.text()))
        
        # 确认删除
        reply = QMessageBox.question(
            self,
            '确认删除',
            f'确定要删除选中的 {len(log_ids)} 条训练记录吗？\n此操作不可恢复！',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success_count = 0
            for log_id in log_ids:
                if training_service.delete_training_log(log_id):
                    success_count += 1
            
            if success_count > 0:
                QMessageBox.information(self, '成功', f'已删除 {success_count} 条记录')
                self.load_training_history()  # 刷新列表
            else:
                QMessageBox.warning(self, '失败', '删除失败，请查看日志')
    
    def clear_all_history(self):
        """清空所有训练历史"""
        reply = QMessageBox.warning(
            self,
            '危险操作',
            '确定要清空所有训练历史记录吗？\n\n⚠️ 此操作将删除所有记录且不可恢复！',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 二次确认
            confirm = QMessageBox.question(
                self,
                '最终确认',
                '请再次确认：真的要清空所有训练历史吗？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                if training_service.clear_all_training_logs(self.user_info['id']):
                    QMessageBox.information(self, '成功', '已清空所有训练历史')
                    self.load_training_history()  # 刷新列表
                else:
                    QMessageBox.warning(self, '失败', '清空失败，请查看日志')
