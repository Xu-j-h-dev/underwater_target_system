"""
登录界面
提供用户登录功能
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from services import auth_service

class LoginWindow(QWidget):
    """登录窗口类"""
    
    # 登录成功信号，传递用户信息
    login_success = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('水下目标识别系统 - 登录')
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLabel {
                font-size: 12px;
                color: #34495e;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                background-color: #3498db;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f6391;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # 标题
        title_label = QLabel('🌊 水下目标识别系统')
        title_label.setObjectName('title')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Logo区域（可选）
        subtitle = QLabel('Underwater Target Detection System')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet('color: #7f8c8d; font-size: 11px;')
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(20)
        
        # 用户名
        username_label = QLabel('用户名')
        main_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        main_layout.addWidget(self.username_input)
        
        # 密码
        password_label = QLabel('密码')
        main_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        main_layout.addWidget(self.password_input)
        
        # 记住密码和忘记密码
        remember_layout = QHBoxLayout()
        self.info_label = QLabel('默认账号: admin/admin123, user/user123')
        self.info_label.setStyleSheet('color: #95a5a6; font-size: 10px;')
        remember_layout.addWidget(self.info_label)
        remember_layout.addStretch()
        main_layout.addLayout(remember_layout)
        
        # 登录按钮
        self.login_button = QPushButton('登 录')
        self.login_button.clicked.connect(self.handle_login)
        main_layout.addWidget(self.login_button)
        
        # 注册按钮
        self.register_button = QPushButton('注 册')
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.register_button.clicked.connect(self.show_register_dialog)
        main_layout.addWidget(self.register_button)
        
        main_layout.addStretch()
        
        # 版本信息
        version_label = QLabel('Version 1.0.0 | Powered by YOLOv11')
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet('color: #bdc3c7; font-size: 9px;')
        main_layout.addWidget(version_label)
        
        self.setLayout(main_layout)
        
        # 回车键登录
        self.password_input.returnPressed.connect(self.handle_login)
    
    def handle_login(self):
        """处理登录"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, '提示', '请输入用户名和密码')
            return
        
        # 调用认证服务
        user_info = auth_service.login(username, password)
        
        if user_info:
            QMessageBox.information(self, '成功', f'欢迎回来，{username}！')
            self.login_success.emit(user_info)
            self.close()
        else:
            QMessageBox.critical(self, '错误', '用户名或密码错误')
            self.password_input.clear()
            self.password_input.setFocus()
    
    def show_register_dialog(self):
        """显示注册对话框"""
        from .register_dialog import RegisterDialog
        dialog = RegisterDialog(self)
        if dialog.exec():
            QMessageBox.information(self, '成功', '注册成功，请登录')
