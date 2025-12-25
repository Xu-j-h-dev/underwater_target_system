
"""
问题反馈对话框
提供用户提交问题反馈的界面
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                          QLineEdit, QTextEdit, QComboBox, QPushButton,
                          QMessageBox, QFormLayout)
from PyQt6.QtCore import Qt
from services import feedback_service
from utils import system_logger
import config

class FeedbackDialog(QDialog):
    """反馈对话框类"""

    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('🐛 问题反馈')
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
            QLineEdit, QTextEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 2px solid #4facfe;
            }
            QPushButton {
                background-color: #4facfe;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00f2fe;
            }
            QPushButton:pressed {
                background-color: #3a8bfd;
            }
        """)

        layout = QVBoxLayout()

        # 标题
        title_label = QLabel('🐛 问题反馈')
        title_label.setStyleSheet('font-size: 18px; color: #4facfe; margin-bottom: 15px;')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 表单布局
        form_layout = QFormLayout()

        # 反馈类型
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            '功能建议', '界面问题', '功能错误', '性能问题', '其他问题'
        ])
        form_layout.addRow('反馈类型:', self.category_combo)

        # 标题
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText('请简要描述您的问题')
        form_layout.addRow('标题:', self.title_input)

        # 联系邮箱
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('选填，便于我们回复您')
        form_layout.addRow('联系邮箱:', self.email_input)

        # 详细内容
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText('请详细描述您遇到的问题或建议...')
        self.content_input.setMinimumHeight(150)
        form_layout.addRow('详细内容:', self.content_input)

        layout.addLayout(form_layout)

        # 提示信息
        tip_label = QLabel('💡 您的反馈对我们非常重要，我们会尽快处理并回复您！')
        tip_label.setStyleSheet('color: #7f8c8d; font-size: 12px; padding: 10px;')
        layout.addWidget(tip_label)

        # 按钮
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)

        submit_btn = QPushButton('提交反馈')
        submit_btn.clicked.connect(self.submit_feedback)

        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(submit_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def submit_feedback(self):
        """提交反馈"""
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()
        email = self.email_input.text().strip()
        category = self.category_combo.currentText()

        # 验证必填字段
        if not title:
            QMessageBox.warning(self, '提示', '请输入反馈标题！')
            self.title_input.setFocus()
            return

        if not content:
            QMessageBox.warning(self, '提示', '请输入反馈内容！')
            self.content_input.setFocus()
            return

        # 提交反馈
        try:
            success = feedback_service.submit_feedback(
                user_id=self.user_info['id'],
                title=title,
                content=content,
                category=category,
                email=email if email else None
            )

            if success:
                QMessageBox.information(self, '成功', '反馈提交成功！感谢您的宝贵意见。')
                self.accept()
            else:
                QMessageBox.critical(self, '错误', '反馈提交失败，请稍后再试。')
        except Exception as e:
            system_logger.error(f"提交反馈异常: {str(e)}")
            QMessageBox.critical(self, '错误', f'提交反馈时发生错误：{str(e)}')
