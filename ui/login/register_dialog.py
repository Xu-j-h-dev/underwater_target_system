"""
注册对话框
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from services import auth_service

class RegisterDialog(QDialog):
    """注册对话框类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('用户注册')
        self.setFixedSize(350, 300)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 用户名
        layout.addWidget(QLabel('用户名：'))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        layout.addWidget(self.username_input)
        
        # 密码
        layout.addWidget(QLabel('密码：'))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        # 确认密码
        layout.addWidget(QLabel('确认密码：'))
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('请再次输入密码')
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password_input)
        
        # 邮箱
        layout.addWidget(QLabel('邮箱（可选）：'))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('请输入邮箱')
        layout.addWidget(self.email_input)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        register_btn = QPushButton('注册')
        register_btn.clicked.connect(self.handle_register)
        button_layout.addWidget(register_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def handle_register(self):
        """处理注册"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        email = self.email_input.text().strip()
        
        # 验证
        if not username or not password:
            QMessageBox.warning(self, '警告', '用户名和密码不能为空')
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, '警告', '两次输入的密码不一致')
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, '警告', '密码长度至少6位')
            return
        
        # 调用注册服务
        success = auth_service.register(username, password, email)
        
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, '错误', '注册失败，用户名可能已存在')
