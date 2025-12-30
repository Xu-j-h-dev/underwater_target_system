
"""
我的反馈对话框
提供用户查看自己提交反馈的界面
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QPushButton, QMessageBox, QListWidget, QListWidgetItem,
                          QWidget, QFrame, QGridLayout, QTextEdit)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from datetime import datetime
from services import feedback_service
from utils import system_logger

class FeedbackItemWidget(QWidget):
    """反馈项小部件"""

    def __init__(self, feedback_data, parent=None):
        super().__init__(parent)
        self.feedback_data = feedback_data
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 标题和状态
        header_layout = QHBoxLayout()

        # 标题
        title_label = QLabel(self.feedback_data['title'])
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        # 状态标签
        status = self.feedback_data['status']
        status_color = {
            'pending': '#f39c12',  # 橙色
            'processing': '#3498db',  # 蓝色
            'resolved': '#27ae60',  # 绿色
            'rejected': '#e74c3c'  # 红色
        }.get(status, '#7f8c8d')

        status_text = {
            'pending': '待处理',
            'processing': '处理中',
            'resolved': '已解决',
            'rejected': '已拒绝'
        }.get(status, '未知')

        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"""
            background-color: {status_color};
            color: white;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 11px;
        """)
        header_layout.addWidget(status_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 类别和时间
        meta_layout = QHBoxLayout()

        category_label = QLabel(f"类别: {self.feedback_data['category'] or '未分类'}")
        category_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        meta_layout.addWidget(category_label)

        created_at = self.feedback_data.get('created_at')
        if created_at is None:
            time_str = "未知"
        elif isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
                time_str = created_at.strftime('%Y-%m-%d %H:%M')
            except:
                time_str = str(created_at)
        elif isinstance(created_at, datetime):
            time_str = created_at.strftime('%Y-%m-%d %H:%M')
        else:
            time_str = str(created_at)

        time_label = QLabel(f"提交时间: {time_str}")
        time_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        meta_layout.addWidget(time_label)

        meta_layout.addStretch()
        layout.addLayout(meta_layout)

        # 内容预览
        content_preview = self.feedback_data['content']
        if len(content_preview) > 100:
            content_preview = content_preview[:100] + '...'

        content_label = QLabel(content_preview)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("color: #2c3e50; font-size: 12px; margin: 5px 0;")
        layout.addWidget(content_label)

        # 如果有回复，显示回复预览
        if self.feedback_data.get('response'):
            response_label = QLabel("管理员回复:")
            response_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 11px; margin-top: 5px;")
            layout.addWidget(response_label)

            response_preview = self.feedback_data['response']
            if len(response_preview) > 100:
                response_preview = response_preview[:100] + '...'

            response_content = QLabel(response_preview)
            response_content.setWordWrap(True)
            response_content.setStyleSheet("color: #2c3e50; font-size: 12px; margin: 5px 0; padding-left: 10px; border-left: 2px solid #27ae60;")
            layout.addWidget(response_content)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
            QWidget:hover {
                border: 1px solid #4facfe;
            }
        """)

class FeedbackDetailDialog(QDialog):
    """反馈详情对话框"""

    def __init__(self, feedback_data, parent=None):
        super().__init__(parent)
        self.feedback_data = feedback_data
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('反馈详情')
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        layout = QVBoxLayout()

        # 标题和状态
        header_layout = QHBoxLayout()

        title_label = QLabel(self.feedback_data['title'])
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        # 状态标签
        status = self.feedback_data['status']
        status_color = {
            'pending': '#f39c12',  # 橙色
            'processing': '#3498db',  # 蓝色
            'resolved': '#27ae60',  # 绿色
            'rejected': '#e74c3c'  # 红色
        }.get(status, '#7f8c8d')

        status_text = {
            'pending': '待处理',
            'processing': '处理中',
            'resolved': '已解决',
            'rejected': '已拒绝'
        }.get(status, '未知')

        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"""
            background-color: {status_color};
            color: white;
            padding: 5px 15px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: bold;
        """)
        header_layout.addWidget(status_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # 基本信息
        info_layout = QGridLayout()

        # 类别
        info_layout.addWidget(QLabel("类别:"), 0, 0)
        category_label = QLabel(self.feedback_data['category'] or '未分类')
        info_layout.addWidget(category_label, 0, 1)

        # 邮箱
        info_layout.addWidget(QLabel("联系邮箱:"), 0, 2)
        email_label = QLabel(self.feedback_data['email'] or '未提供')
        info_layout.addWidget(email_label, 0, 3)

        # 提交时间
        info_layout.addWidget(QLabel("提交时间:"), 1, 0)
        created_at = self.feedback_data.get('created_at')
        if created_at is None:
            time_str = "未知"
        elif isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
                time_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
            except:
                time_str = str(created_at)
        elif isinstance(created_at, datetime):
            time_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = str(created_at)

        time_label = QLabel(time_str)
        info_layout.addWidget(time_label, 1, 1)

        # 更新时间
        info_layout.addWidget(QLabel("更新时间:"), 1, 2)
        updated_at = self.feedback_data.get('updated_at')
        if updated_at is None:
            update_time_label = QLabel("无")
        elif isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at)
                update_time_str = updated_at.strftime('%Y-%m-%d %H:%M:%S')
                update_time_label = QLabel(update_time_str)
            except:
                update_time_label = QLabel(str(updated_at))
        elif isinstance(updated_at, datetime):
            update_time_str = updated_at.strftime('%Y-%m-%d %H:%M:%S')
            update_time_label = QLabel(update_time_str)
        else:
            update_time_label = QLabel(str(updated_at))

        info_layout.addWidget(update_time_label, 1, 3)

        layout.addLayout(info_layout)

        # 分隔线
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)

        # 反馈内容
        content_label = QLabel("反馈内容:")
        content_label.setStyleSheet("font-weight: bold; font-size: 13px; margin-top: 10px;")
        layout.addWidget(content_label)

        content_text = QTextEdit()
        content_text.setPlainText(self.feedback_data['content'])
        content_text.setReadOnly(True)
        content_text.setMinimumHeight(100)
        layout.addWidget(content_text)

        # 如果有回复，显示回复内容
        if self.feedback_data.get('response'):
            response_label = QLabel("管理员回复:")
            response_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #27ae60; margin-top: 10px;")
            layout.addWidget(response_label)

            response_text = QTextEdit()
            response_text.setPlainText(self.feedback_data['response'])
            response_text.setReadOnly(True)
            response_text.setStyleSheet("""
                QTextEdit {
                    background-color: #f0f8ff;
                    border-left: 3px solid #27ae60;
                    padding-left: 10px;
                }
            """)
            response_text.setMinimumHeight(80)
            layout.addWidget(response_text)

        # 关闭按钮
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #4facfe;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00f2fe;
            }
        """)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c3e50;
            }
        """)

        # 确保对话框正确显示
        self.adjustSize()

class MyFeedbackDialog(QDialog):
    """我的反馈对话框"""

    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.init_ui()
        self.load_feedbacks()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('💬 我的反馈')
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
            QListWidget {
                border: none;
                background-color: #f5f5f5;
            }
        """)

        layout = QVBoxLayout()

        # 标题
        title_label = QLabel('💬 我的反馈')
        title_label.setStyleSheet('font-size: 18px; color: #4facfe; margin-bottom: 15px;')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 反馈列表
        self.feedback_list = QListWidget()
        self.feedback_list.itemClicked.connect(self.show_feedback_detail)
        layout.addWidget(self.feedback_list)

        # 按钮
        button_layout = QHBoxLayout()

        refresh_btn = QPushButton('🔄 刷新')
        refresh_btn.clicked.connect(self.load_feedbacks)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4facfe;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00f2fe;
            }
        """)
        button_layout.addWidget(refresh_btn)

        new_feedback_btn = QPushButton('➕ 提交新反馈')
        new_feedback_btn.clicked.connect(self.open_new_feedback)
        new_feedback_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        button_layout.addWidget(new_feedback_btn)

        close_btn = QPushButton('✖ 关闭')
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_feedbacks(self):
        """加载反馈列表"""
        self.feedback_list.clear()

        try:
            feedbacks = feedback_service.get_user_feedbacks(self.user_info['id'])

            if not feedbacks:
                item = QListWidgetItem()
                item_widget = QLabel("暂无反馈记录，点击下方按钮提交您的第一条反馈！")
                item_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                item_widget.setStyleSheet("color: #7f8c8d; padding: 20px;")
                item.setSizeHint(item_widget.sizeHint())
                self.feedback_list.addItem(item)
                self.feedback_list.setItemWidget(item, item_widget)
                return

            for feedback in feedbacks:
                try:
                    item = QListWidgetItem()
                    item_widget = FeedbackItemWidget(feedback)
                    item.setSizeHint(item_widget.sizeHint())
                    self.feedback_list.addItem(item)
                    self.feedback_list.setItemWidget(item, item_widget)
                    # 存储完整数据，用于详情查看
                    item.setData(Qt.ItemDataRole.UserRole, feedback)
                except Exception as e:
                    system_logger.error(f"处理反馈项失败: {str(e)}")
                    continue

        except Exception as e:
            system_logger.error(f"加载反馈列表失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'加载反馈列表失败：{str(e)}')

    def show_feedback_detail(self, item):
        """显示反馈详情"""
        try:
            # 获取反馈数据
            widget = self.feedback_list.itemWidget(item)
            if isinstance(widget, FeedbackItemWidget):
                feedback_data = widget.feedback_data
                detail_dialog = FeedbackDetailDialog(feedback_data, self)
                detail_dialog.exec()
        except Exception as e:
            system_logger.error(f"显示反馈详情失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'显示反馈详情时发生错误：{str(e)}')

    def open_new_feedback(self):
        """打开新反馈对话框"""
        try:
            from ui.main.feedback_dialog import FeedbackDialog
            feedback_dialog = FeedbackDialog(self.user_info, self)
            if feedback_dialog.exec() == QDialog.DialogCode.Accepted:
                # 刷新列表
                self.load_feedbacks()
        except Exception as e:
            system_logger.error(f"打开反馈对话框失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'打开反馈对话框失败：{str(e)}')
