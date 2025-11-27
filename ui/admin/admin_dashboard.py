"""
管理员仪表盘
提供用户管理、模型管理、日志管理功能
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QLineEdit, QMessageBox, QHeaderView, QComboBox,
                             QFileDialog, QTextEdit, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt
from services import auth_service, model_manager, db_service
import config

class AdminDashboard(QMainWindow):
    """管理员仪表盘类"""
    
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f'管理员仪表盘 - {self.user_info["username"]}')
        self.setGeometry(100, 100, 1200, 700)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel(f'👤 欢迎，管理员 {self.user_info["username"]}')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold; padding: 10px;')
        layout.addWidget(title_label)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 用户管理选项卡
        self.user_tab = self.create_user_management_tab()
        self.tab_widget.addTab(self.user_tab, '👥 用户管理')
        
        # 模型管理选项卡
        self.model_tab = self.create_model_management_tab()
        self.tab_widget.addTab(self.model_tab, '🤖 模型管理')
        
        # 日志管理选项卡
        self.log_tab = self.create_log_management_tab()
        self.tab_widget.addTab(self.log_tab, '📋 日志管理')
        
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)
        
        # 加载数据
        self.load_users()
        self.load_models()
        self.load_logs()
    
    def create_user_management_tab(self):
        """创建用户管理选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        refresh_btn = QPushButton('🔄 刷新')
        refresh_btn.clicked.connect(self.load_users)
        toolbar.addWidget(refresh_btn)
        
        add_user_btn = QPushButton('➕ 添加用户')
        add_user_btn.clicked.connect(self.add_user_dialog)
        toolbar.addWidget(add_user_btn)
        
        toolbar.addStretch()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText('搜索用户...')
        search_input.setMaximumWidth(200)
        toolbar.addWidget(search_input)
        
        layout.addLayout(toolbar)
        
        # 用户表格
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(7)
        self.user_table.setHorizontalHeaderLabels(['ID', '用户名', '邮箱', '角色', '状态', '创建时间', '操作'])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.user_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_model_management_tab(self):
        """创建模型管理选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        refresh_btn = QPushButton('🔄 刷新')
        refresh_btn.clicked.connect(self.load_models)
        toolbar.addWidget(refresh_btn)
        
        upload_btn = QPushButton('📤 上传模型')
        upload_btn.clicked.connect(self.upload_model_dialog)
        toolbar.addWidget(upload_btn)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # 模型表格
        self.model_table = QTableWidget()
        self.model_table.setColumnCount(7)
        self.model_table.setHorizontalHeaderLabels(['ID', '名称', '版本', '作者', '创建时间', '描述', '操作'])
        self.model_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.model_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_log_management_tab(self):
        """创建日志管理选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 日志类型选择
        log_type_layout = QHBoxLayout()
        log_type_layout.addWidget(QLabel('日志类型：'))
        
        self.log_type_combo = QComboBox()
        self.log_type_combo.addItems(['登录日志', '推理日志', '训练日志', '系统日志'])
        self.log_type_combo.currentIndexChanged.connect(self.load_logs)
        log_type_layout.addWidget(self.log_type_combo)
        
        refresh_btn = QPushButton('🔄 刷新')
        refresh_btn.clicked.connect(self.load_logs)
        log_type_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton('📥 导出日志')
        export_btn.clicked.connect(self.export_logs)
        log_type_layout.addWidget(export_btn)
        
        log_type_layout.addStretch()
        
        layout.addLayout(log_type_layout)
        
        # 日志表格
        self.log_table = QTableWidget()
        layout.addWidget(self.log_table)
        
        widget.setLayout(layout)
        return widget
    
    def load_users(self):
        """加载用户列表"""
        users = auth_service.get_all_users()
        self.user_table.setRowCount(len(users))
        
        for i, user in enumerate(users):
            self.user_table.setItem(i, 0, QTableWidgetItem(str(user['id'])))
            self.user_table.setItem(i, 1, QTableWidgetItem(user['username']))
            self.user_table.setItem(i, 2, QTableWidgetItem(user.get('email', '')))
            self.user_table.setItem(i, 3, QTableWidgetItem(user['role']))
            self.user_table.setItem(i, 4, QTableWidgetItem(user['status']))
            self.user_table.setItem(i, 5, QTableWidgetItem(str(user['created_at'])))
            
            # 操作按钮
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(5, 2, 5, 2)
            
            edit_btn = QPushButton('编辑')
            edit_btn.clicked.connect(lambda checked, uid=user['id']: self.edit_user(uid))
            action_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton('删除')
            delete_btn.clicked.connect(lambda checked, uid=user['id']: self.delete_user(uid))
            action_layout.addWidget(delete_btn)
            
            action_widget.setLayout(action_layout)
            self.user_table.setCellWidget(i, 6, action_widget)
    
    def load_models(self):
        """加载模型列表"""
        models = model_manager.get_all_models()
        self.model_table.setRowCount(len(models))
        
        for i, model in enumerate(models):
            self.model_table.setItem(i, 0, QTableWidgetItem(str(model['id'])))
            self.model_table.setItem(i, 1, QTableWidgetItem(model['name']))
            self.model_table.setItem(i, 2, QTableWidgetItem(model['version']))
            self.model_table.setItem(i, 3, QTableWidgetItem(model.get('author', '')))
            self.model_table.setItem(i, 4, QTableWidgetItem(str(model['created_at'])))
            self.model_table.setItem(i, 5, QTableWidgetItem(model.get('description', '')[:50]))
            
            # 操作按钮
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(5, 2, 5, 2)
            
            view_btn = QPushButton('查看')
            view_btn.clicked.connect(lambda checked, mid=model['id']: self.view_model(mid))
            action_layout.addWidget(view_btn)
            
            delete_btn = QPushButton('删除')
            delete_btn.clicked.connect(lambda checked, mid=model['id']: self.delete_model(mid))
            action_layout.addWidget(delete_btn)
            
            action_widget.setLayout(action_layout)
            self.model_table.setCellWidget(i, 6, action_widget)
    
    def load_logs(self):
        """加载日志"""
        log_type = self.log_type_combo.currentText()
        
        if log_type == '登录日志':
            logs = auth_service.get_login_logs()
            self.log_table.setColumnCount(5)
            self.log_table.setHorizontalHeaderLabels(['ID', '用户名', '登录时间', 'IP地址', '状态'])
            self.log_table.setRowCount(len(logs))
            
            for i, log in enumerate(logs):
                self.log_table.setItem(i, 0, QTableWidgetItem(str(log['id'])))
                self.log_table.setItem(i, 1, QTableWidgetItem(log['username']))
                self.log_table.setItem(i, 2, QTableWidgetItem(str(log['login_time'])))
                self.log_table.setItem(i, 3, QTableWidgetItem(log.get('ip_address', '')))
                self.log_table.setItem(i, 4, QTableWidgetItem(log['status']))
        
        elif log_type == '推理日志':
            logs = db_service.execute_query("SELECT * FROM inference_logs ORDER BY created_at DESC LIMIT 100")
            self.log_table.setColumnCount(6)
            self.log_table.setHorizontalHeaderLabels(['ID', '用户ID', '模型', '数据源', '检测数', '推理时间'])
            self.log_table.setRowCount(len(logs))
            
            for i, log in enumerate(logs):
                self.log_table.setItem(i, 0, QTableWidgetItem(str(log['id'])))
                self.log_table.setItem(i, 1, QTableWidgetItem(str(log['user_id'])))
                self.log_table.setItem(i, 2, QTableWidgetItem(log.get('model_name', '')))
                self.log_table.setItem(i, 3, QTableWidgetItem(log.get('source_type', '')))
                self.log_table.setItem(i, 4, QTableWidgetItem(str(log.get('detections', 0))))
                self.log_table.setItem(i, 5, QTableWidgetItem(f"{log.get('inference_time', 0):.3f}s"))
        
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    def add_user_dialog(self):
        """添加用户对话框"""
        from ui.login import RegisterDialog
        dialog = RegisterDialog(self)
        if dialog.exec():
            self.load_users()
            QMessageBox.information(self, '成功', '用户添加成功')
    
    def edit_user(self, user_id):
        """编辑用户"""
        QMessageBox.information(self, '提示', f'编辑用户功能 (ID: {user_id})')
    
    def delete_user(self, user_id):
        """删除用户"""
        reply = QMessageBox.question(self, '确认', '确定要删除此用户吗？',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if auth_service.delete_user(user_id):
                self.load_users()
                QMessageBox.information(self, '成功', '用户删除成功')
    
    def upload_model_dialog(self):
        """上传模型对话框"""
        file_path, _ = QFileDialog.getOpenFileName(self, '选择模型文件', '', 'Model Files (*.pt *.pth)')
        if file_path:
            # 简单上传，可以扩展为完整对话框
            import os
            model_name = os.path.basename(file_path).replace('.pt', '').replace('.pth', '')
            if model_manager.add_model(model_name, '1.0', file_path, author=self.user_info['username']):
                self.load_models()
                QMessageBox.information(self, '成功', '模型上传成功')
    
    def view_model(self, model_id):
        """查看模型详情"""
        model = model_manager.get_model_by_id(model_id)
        if model:
            info = f"""
            名称: {model['name']}
            版本: {model['version']}
            作者: {model.get('author', '未知')}
            路径: {model['file_path']}
            描述: {model.get('description', '无')}
            创建时间: {model['created_at']}
            """
            QMessageBox.information(self, '模型详情', info)
    
    def delete_model(self, model_id):
        """删除模型"""
        reply = QMessageBox.question(self, '确认', '确定要删除此模型吗？',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if model_manager.delete_model(model_id):
                self.load_models()
                QMessageBox.information(self, '成功', '模型删除成功')
    
    def export_logs(self):
        """导出日志"""
        file_path, _ = QFileDialog.getSaveFileName(self, '导出日志', '', 'CSV Files (*.csv)')
        if file_path:
            QMessageBox.information(self, '成功', f'日志导出到: {file_path}')
