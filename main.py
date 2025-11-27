"""
水下目标识别系统 - 主程序入口
基于 Python + PyQt6 + YOLOv11 + MySQL
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.login import LoginWindow
from ui.main import MainWindow
from utils import system_logger

class Application:
    """应用程序类"""
    
    def __init__(self):
        """初始化应用程序"""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName('水下目标识别系统')
        self.app.setOrganizationName('Underwater Detection')
        
        # 设置高DPI支持
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        self.login_window = None
        self.main_window = None
        
        system_logger.info('应用程序启动')
    
    def start(self):
        """启动应用程序"""
        # 显示登录窗口
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.show()
        
        return self.app.exec()
    
    def on_login_success(self, user_info):
        """登录成功回调"""
        system_logger.info(f'用户登录: {user_info["username"]} ({user_info["role"]})')
        
        # 创建主窗口
        self.main_window = MainWindow(user_info)
        self.main_window.show()

def main():
    """主函数"""
    try:
        app = Application()
        sys.exit(app.start())
    except Exception as e:
        system_logger.error(f'应用程序错误: {str(e)}', exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
