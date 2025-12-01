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
        self.setFixedSize(450, 580)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe, stop:0.5 #00f2fe, stop:1 #667eea);
            }
            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                color: white;
                letter-spacing: 2px;
            }
            QLabel#subtitle {
                color: rgba(255, 255, 255, 0.9);
                font-size: 12px;
            }
            QLabel {
                font-size: 13px;
                color: white;
                font-weight: 500;
                background: transparent;
            }
            QLabel#field_label {
                font-size: 14px;
                color: white;
                font-weight: 600;
                margin-bottom: 5px;
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
                border: 2px solid #ffffff;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
            QPushButton {
                padding: 14px;
                font-size: 15px;
                font-weight: bold;
                border-radius: 10px;
                background-color: white;
                color: #4facfe;
                border: none;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #f0f8ff;
                color: #00f2fe;
                border: 2px solid white;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.8);
            }
            QPushButton#register_btn {
                background-color: transparent;
                border: 2px solid rgba(255, 255, 255, 0.8);
                color: white;
            }
            QPushButton#register_btn:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border: 2px solid white;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(15)
        
        # 顶部图标区域
        icon_label = QLabel('🌊')
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet('font-size: 48px; margin: 10px;')
        main_layout.addWidget(icon_label)
        
        # 标题
        title_label = QLabel('水下目标识别系统')
        title_label.setObjectName('title')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 副标题
        subtitle = QLabel('Underwater Target Detection System')
        subtitle.setObjectName('subtitle')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(30)
        
        # 用户名输入框
        username_label = QLabel('👤 用户名')
        username_label.setObjectName('field_label')
        main_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入您的用户名')
        self.username_input.setMinimumHeight(48)
        main_layout.addWidget(self.username_input)
        
        main_layout.addSpacing(10)
        
        # 密码输入框
        password_label = QLabel('🔒 密码')
        password_label.setObjectName('field_label')
        main_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入您的密码')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(48)
        main_layout.addWidget(self.password_input)
        
        # 提示信息
        main_layout.addSpacing(5)
        self.info_label = QLabel('💡 默认账号: admin/admin123 或 user/user123')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet('color: rgba(255, 255, 255, 0.8); font-size: 11px;')
        main_layout.addWidget(self.info_label)
        
        main_layout.addSpacing(10)
        
        # 登录按钮
        self.login_button = QPushButton('🚀 立即登录')
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        main_layout.addWidget(self.login_button)
        
        main_layout.addSpacing(5)
        
        # 注册按钮
        self.register_button = QPushButton('✨ 创建新账号')
        self.register_button.setObjectName('register_btn')
        self.register_button.clicked.connect(self.show_register_dialog)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        main_layout.addWidget(self.register_button)
        
        main_layout.addStretch()
        
        # 版本信息
        version_label = QLabel('Version 1.0.0 | Powered by YOLOv11 🤖')
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet('color: rgba(255, 255, 255, 0.6); font-size: 10px;')
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
