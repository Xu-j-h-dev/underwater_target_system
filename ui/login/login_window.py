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
        self.setFixedSize(500, 780)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
            QLabel#title {
                font-size: 32px;
                font-weight: bold;
                color: #ffffff;
                letter-spacing: 1px;
            }
            QLabel#subtitle {
                color: #a0a0a0;
                font-size: 13px;
            }
            QLabel {
                font-size: 13px;
                color: #e0e0e0;
                background: transparent;
            }
            QLabel#field_label {
                font-size: 13px;
                color: #ffffff;
                font-weight: 600;
                margin-bottom: 5px;
            }
            QLabel#info_label {
                color: #888888;
                font-size: 11px;
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
                font-size: 15px;
                font-weight: bold;
                border-radius: 8px;
                background-color: #3498db;
                color: white;
                border: none;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton#register_btn {
                background-color: transparent;
                border: 2px solid #3498db;
                color: #3498db;
            }
            QPushButton#register_btn:hover {
                background-color: #2d3e50;
                border: 2px solid #2980b9;
                color: #5dade2;
            }
            QFrame#login_card {
                background-color: #252525;
                border-radius: 12px;
                border: 1px solid #3a3a3a;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 35, 40, 35)
        main_layout.setSpacing(0)
        
        # 顶部空白
        main_layout.addSpacing(25)
        
        # 图标
        icon_label = QLabel('🌊')
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet('font-size: 60px; margin: 0px; background: transparent;')
        main_layout.addWidget(icon_label)
        
        main_layout.addSpacing(15)
        
        # 标题
        title_label = QLabel('水下目标识别系统')
        title_label.setObjectName('title')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        main_layout.addSpacing(8)
        
        # 副标题
        subtitle = QLabel('Underwater Target Detection System')
        subtitle.setObjectName('subtitle')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(35)
        
        # 登录卡片
        from PyQt6.QtWidgets import QFrame
        login_card = QFrame()
        login_card.setObjectName('login_card')
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(0)
        
        # 用户名输入框
        username_label = QLabel('👤 用户名')
        username_label.setObjectName('field_label')
        card_layout.addWidget(username_label)
        
        card_layout.addSpacing(8)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        card_layout.addWidget(self.username_input)
        
        card_layout.addSpacing(28)
        
        # 密码输入框
        password_label = QLabel('🔒 密码')
        password_label.setObjectName('field_label')
        card_layout.addWidget(password_label)
        
        card_layout.addSpacing(8)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        card_layout.addWidget(self.password_input)
        
        # 提示信息
        card_layout.addSpacing(20)
        self.info_label = QLabel('💡 默认账号: admin/admin123 或 user/user123')
        self.info_label.setObjectName('info_label')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.info_label)
        
        card_layout.addSpacing(32)
        
        # 登录按钮
        self.login_button = QPushButton('🚀 登录')
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        card_layout.addWidget(self.login_button)
        
        card_layout.addSpacing(18)
        
        # 注册按钮
        self.register_button = QPushButton('✨ 创建新账号')
        self.register_button.setObjectName('register_btn')
        self.register_button.clicked.connect(self.show_register_dialog)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        card_layout.addWidget(self.register_button)
        
        login_card.setLayout(card_layout)
        main_layout.addWidget(login_card)
        
        main_layout.addSpacing(25)
        
        # 版本信息
        version_label = QLabel('Version 1.0.0 | Powered by YOLOv11 🤖')
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet('color: #606060; font-size: 10px; background: transparent;')
        main_layout.addWidget(version_label)
        
        main_layout.addSpacing(15)
        
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
