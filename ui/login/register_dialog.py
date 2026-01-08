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
        self.setWindowTitle('新用户注册')
        self.setFixedSize(450, 750)
        self.setModal(True)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
                font-weight: 500;
                background: transparent;
            }
            QLabel#field_label {
                font-size: 13px;
                color: #ffffff;
                font-weight: 600;
                margin-bottom: 5px;
            }
            QLabel#header {
                font-size: 28px;
                font-weight: bold;
                color: #ffffff;
                letter-spacing: 2px;
            }
            QLineEdit {
                padding: 14px 16px;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                font-size: 14px;
                background-color: #2d2d2d;
                color: #ffffff;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #353535;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
            QPushButton {
                padding: 14px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
                min-height: 20px;
            }
            QPushButton#register_btn {
                background-color: #3498db;
                color: white;
            }
            QPushButton#register_btn:hover {
                background-color: #2980b9;
            }
            QPushButton#cancel_btn {
                background-color: transparent;
                border: 2px solid #3498db;
                color: #3498db;
            }
            QPushButton#cancel_btn:hover {
                background-color: #2d3e50;
                border: 2px solid #2980b9;
                color: #5dade2;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(45, 50, 45, 45)
        
        # 头部区域
        header_layout = QVBoxLayout()
        header_layout.setSpacing(0)
        
        icon_label = QLabel('✨')
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet('font-size: 60px; margin: 0px;')
        header_layout.addWidget(icon_label)
        
        header_layout.addSpacing(15)
        
        title_label = QLabel('注册新账号')
        title_label.setObjectName('header')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        from PyQt6.QtGui import QFont
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        header_layout.addWidget(title_label)
        
        header_layout.addSpacing(8)
        
        subtitle_label = QLabel('加入水下目标识别系统')
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet('color: #a0a0a0; font-size: 12px;')
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        layout.addSpacing(30)
        
        # 用户名
        username_label = QLabel('👤 用户名')
        username_label.setObjectName('field_label')
        layout.addWidget(username_label)
        
        layout.addSpacing(8)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请设置您的用户名')
        layout.addWidget(self.username_input)
        
        layout.addSpacing(18)
        
        # 密码
        password_label = QLabel('🔒 密码')
        password_label.setObjectName('field_label')
        layout.addWidget(password_label)
        
        layout.addSpacing(8)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请设置密码（至少6位）')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(18)
        
        # 确认密码
        confirm_label = QLabel('🔓 确认密码')
        confirm_label.setObjectName('field_label')
        layout.addWidget(confirm_label)
        
        layout.addSpacing(8)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('请再次输入密码')
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password_input)
        
        layout.addSpacing(18)
        
        # 邮箱
        email_label = QLabel('📧 邮箱（可选）')
        email_label.setObjectName('field_label')
        layout.addWidget(email_label)
        
        layout.addSpacing(8)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('请输入您的邮箱地址')
        layout.addWidget(self.email_input)
        
        layout.addSpacing(25)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        register_btn = QPushButton('✅ 立即注册')
        register_btn.setObjectName('register_btn')
        register_btn.clicked.connect(self.handle_register)
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(register_btn)
        
        cancel_btn = QPushButton('❌ 取消')
        cancel_btn.setObjectName('cancel_btn')
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
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
