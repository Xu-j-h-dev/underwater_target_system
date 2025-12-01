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
        self.setFixedSize(420, 520)
        self.setModal(True)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe, stop:0.5 #00f2fe, stop:1 #667eea);
            }
            QLabel {
                color: white;
                font-size: 13px;
                font-weight: 500;
                background: transparent;
            }
            QLabel#field_label {
                font-size: 14px;
                color: white;
                font-weight: 600;
                margin-bottom: 5px;
            }
            QLabel#header {
                font-size: 24px;
                font-weight: bold;
                color: white;
            }
            QLineEdit {
                padding: 14px 18px;
                border: 2px solid rgba(255, 255, 255, 0.4);
                border-radius: 10px;
                font-size: 15px;
                background-color: rgba(255, 255, 255, 0.95);
                color: #2c3e50;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid white;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
            QPushButton {
                padding: 14px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                border: none;
                min-height: 20px;
            }
            QPushButton#register_btn {
                background-color: white;
                color: #4facfe;
            }
            QPushButton#register_btn:hover {
                background-color: #f0f8ff;
                color: #00f2fe;
                border: 2px solid white;
            }
            QPushButton#cancel_btn {
                background-color: transparent;
                border: 2px solid rgba(255, 255, 255, 0.8);
                color: white;
            }
            QPushButton#cancel_btn:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border: 2px solid white;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 头部区域
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        icon_label = QLabel('✨')
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet('font-size: 40px; margin: 10px;')
        header_layout.addWidget(icon_label)
        
        title_label = QLabel('创建新账号')
        title_label.setObjectName('header')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel('加入水下目标识别系统')
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet('color: rgba(255, 255, 255, 0.8); font-size: 12px;')
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        
        # 用户名
        username_label = QLabel('👤 用户名')
        username_label.setObjectName('field_label')
        layout.addWidget(username_label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请设置您的用户名')
        self.username_input.setMinimumHeight(48)
        layout.addWidget(self.username_input)
        
        layout.addSpacing(8)
        
        # 密码
        password_label = QLabel('🔒 密码')
        password_label.setObjectName('field_label')
        layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请设置密码（至少6位）')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(48)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(8)
        
        # 确认密码
        confirm_label = QLabel('🔓 确认密码')
        confirm_label.setObjectName('field_label')
        layout.addWidget(confirm_label)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('请再次输入密码')
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setMinimumHeight(48)
        layout.addWidget(self.confirm_password_input)
        
        layout.addSpacing(8)
        
        # 邮箱
        email_label = QLabel('📧 邮箱（可选）')
        email_label.setObjectName('field_label')
        layout.addWidget(email_label)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('请输入您的邮箱地址')
        self.email_input.setMinimumHeight(48)
        layout.addWidget(self.email_input)
        
        layout.addSpacing(15)
        
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
