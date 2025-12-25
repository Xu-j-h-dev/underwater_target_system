
"""
反馈管理界面
提供管理员查看和处理用户反馈的功能
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QTableWidget, QTableWidgetItem, 
                          QHeaderView, QMessageBox, QTextEdit, QComboBox,
                          QDialog, QFormLayout, QSplitter)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont
from services import feedback_service
from utils import system_logger
from datetime import datetime

class FeedbackManagementDialog(QDialog):
    """反馈管理对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_feedback_id = None
        self.init_ui()
        self.load_feedbacks()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('🐛 反馈管理')
        self.setMinimumSize(1000, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #f0f0f0;
                selection-background-color: #e3f2fd;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #bbdefb;
                color: #1565c0;
            }
            QPushButton {
                background-color: #4facfe;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00f2fe;
            }
            QPushButton:pressed {
                background-color: #3a8bfd;
            }
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)

        layout = QVBoxLayout()

        # 标题
        title_label = QLabel('🐛 用户反馈管理')
        title_label.setStyleSheet('font-size: 18px; color: #4facfe; margin-bottom: 15px;')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧反馈列表
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # 刷新按钮
        refresh_btn = QPushButton('🔄 刷新列表')
        refresh_btn.clicked.connect(self.load_feedbacks)
        left_layout.addWidget(refresh_btn)

        # 反馈表格
        self.feedback_table = QTableWidget()
        self.feedback_table.setColumnCount(6)
        self.feedback_table.setHorizontalHeaderLabels(['ID', '标题', '用户', '类型', '状态', '提交时间'])
        self.feedback_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.feedback_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.feedback_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.feedback_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.feedback_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.feedback_table.itemSelectionChanged.connect(self.on_feedback_selected)
        left_layout.addWidget(self.feedback_table)

        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # 右侧详情
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # 详情标题
        detail_title = QLabel('反馈详情')
        detail_title.setStyleSheet('font-size: 16px; margin-bottom: 10px;')
        right_layout.addWidget(detail_title)

        # 反馈信息表单
        form_layout = QFormLayout()

        # 标题
        self.title_label = QLabel('未选择反馈')
        self.title_label.setWordWrap(True)
        form_layout.addRow('标题:', self.title_label)

        # 用户
        self.user_label = QLabel('-')
        form_layout.addRow('用户:', self.user_label)

        # 类型
        self.category_label = QLabel('-')
        form_layout.addRow('类型:', self.category_label)

        # 邮箱
        self.email_label = QLabel('-')
        form_layout.addRow('邮箱:', self.email_label)

        # 状态
        self.status_combo = QComboBox()
        self.status_combo.addItems(['待处理', '处理中', '已解决', '已关闭'])
        self.status_combo.currentTextChanged.connect(self.on_status_changed)
        form_layout.addRow('状态:', self.status_combo)

        # 提交时间
        self.created_time_label = QLabel('-')
        form_layout.addRow('提交时间:', self.created_time_label)

        right_layout.addLayout(form_layout)

        # 内容
        content_label = QLabel('反馈内容:')
        right_layout.addWidget(content_label)

        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        right_layout.addWidget(self.content_text)

        # 回复
        response_label = QLabel('回复内容:')
        right_layout.addWidget(response_label)

        self.response_text = QTextEdit()
        self.response_text.setPlaceholderText('在此输入回复内容...')
        right_layout.addWidget(self.response_text)

        # 按钮
        button_layout = QHBoxLayout()

        save_btn = QPushButton('💾 保存回复')
        save_btn.clicked.connect(self.save_response)

        delete_btn = QPushButton('🗑️ 删除反馈')
        delete_btn.clicked.connect(self.delete_feedback)
        delete_btn.setStyleSheet('background-color: #e74c3c;')

        button_layout.addWidget(save_btn)
        button_layout.addStretch()
        button_layout.addWidget(delete_btn)

        right_layout.addLayout(button_layout)

        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # 设置分割比例
        splitter.setSizes([600, 400])

        layout.addWidget(splitter)
        self.setLayout(layout)

    def load_feedbacks(self):
        """加载反馈列表"""
        try:
            feedbacks = feedback_service.get_all_feedbacks()

            self.feedback_table.setRowCount(0)

            for row, feedback in enumerate(feedbacks):
                self.feedback_table.insertRow(row)

                # ID
                self.feedback_table.setItem(row, 0, QTableWidgetItem(str(feedback['id'])))

                # 标题
                title = feedback['title']
                if len(title) > 30:
                    title = title[:30] + '...'
                self.feedback_table.setItem(row, 1, QTableWidgetItem(title))

                # 用户
                username = feedback.get('username', '未知')
                self.feedback_table.setItem(row, 2, QTableWidgetItem(username))

                # 类型
                category = feedback.get('category', '-')
                self.feedback_table.setItem(row, 3, QTableWidgetItem(category))

                # 状态
                status = feedback['status']
                status_text = {
                    'pending': '待处理',
                    'processing': '处理中',
                    'resolved': '已解决',
                    'closed': '已关闭'
                }.get(status, status)
                self.feedback_table.setItem(row, 4, QTableWidgetItem(status_text))

                # 提交时间
                created_time = feedback['created_at']
                if isinstance(created_time, datetime):
                    created_time = created_time.strftime('%Y-%m-%d %H:%M')
                self.feedback_table.setItem(row, 5, QTableWidgetItem(created_time))

            system_logger.info(f"加载了 {len(feedbacks)} 条反馈记录")
        except Exception as e:
            system_logger.error(f"加载反馈列表失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'加载反馈列表失败：{str(e)}')

    def on_feedback_selected(self):
        """反馈选择事件"""
        current_row = self.feedback_table.currentRow()
        if current_row < 0:
            return

        try:
            feedback_id = int(self.feedback_table.item(current_row, 0).text())

            # 获取详细信息
            feedbacks = feedback_service.get_all_feedbacks(limit=1000)  # 获取所有反馈
            feedback = next((f for f in feedbacks if f['id'] == feedback_id), None)

            if not feedback:
                return

            self.current_feedback_id = feedback_id

            # 更新详情
            self.title_label.setText(feedback['title'])
            self.user_label.setText(feedback.get('username', '未知'))
            self.category_label.setText(feedback.get('category', '-'))
            self.email_label.setText(feedback.get('email', '-'))

            # 状态
            status = feedback['status']
            status_index = {
                'pending': 0,
                'processing': 1,
                'resolved': 2,
                'closed': 3
            }.get(status, 0)
            self.status_combo.setCurrentIndex(status_index)

            # 时间
            created_time = feedback['created_at']
            if isinstance(created_time, datetime):
                created_time = created_time.strftime('%Y-%m-%d %H:%M:%S')
            self.created_time_label.setText(created_time)

            # 内容
            self.content_text.setText(feedback['content'])

            # 回复
            self.response_text.setText(feedback.get('response', ''))

        except Exception as e:
            system_logger.error(f"加载反馈详情失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'加载反馈详情失败：{str(e)}')

    def on_status_changed(self, status_text):
        """状态改变事件"""
        if not self.current_feedback_id:
            return

        status_map = {
            '待处理': 'pending',
            '处理中': 'processing',
            '已解决': 'resolved',
            '已关闭': 'closed'
        }

        status = status_map.get(status_text, 'pending')

        try:
            success = feedback_service.update_feedback_status(
                feedback_id=self.current_feedback_id,
                status=status
            )

            if success:
                system_logger.info(f"反馈状态更新成功: id={self.current_feedback_id}, status={status}")
                self.load_feedbacks()  # 刷新列表
            else:
                QMessageBox.warning(self, '警告', '状态更新失败')
        except Exception as e:
            system_logger.error(f"更新反馈状态失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'状态更新失败：{str(e)}')

    def save_response(self):
        """保存回复"""
        if not self.current_feedback_id:
            QMessageBox.warning(self, '警告', '请先选择一条反馈')
            return

        response = self.response_text.toPlainText().strip()

        try:
            status_map = {
                '待处理': 'pending',
                '处理中': 'processing',
                '已解决': 'resolved',
                '已关闭': 'closed'
            }

            status = status_map.get(self.status_combo.currentText(), 'processing')

            success = feedback_service.update_feedback_status(
                feedback_id=self.current_feedback_id,
                status=status,
                response=response if response else None
            )

            if success:
                QMessageBox.information(self, '成功', '回复已保存')
                self.load_feedbacks()  # 刷新列表
            else:
                QMessageBox.warning(self, '警告', '保存回复失败')
        except Exception as e:
            system_logger.error(f"保存回复失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'保存回复失败：{str(e)}')

    def delete_feedback(self):
        """删除反馈"""
        if not self.current_feedback_id:
            QMessageBox.warning(self, '警告', '请先选择一条反馈')
            return

        reply = QMessageBox.question(
            self,
            '确认删除',
            '确定要删除这条反馈吗？此操作不可恢复。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            success = feedback_service.delete_feedback(self.current_feedback_id)

            if success:
                QMessageBox.information(self, '成功', '反馈已删除')
                self.load_feedbacks()  # 刷新列表

                # 清空详情
                self.current_feedback_id = None
                self.title_label.setText('未选择反馈')
                self.user_label.setText('-')
                self.category_label.setText('-')
                self.email_label.setText('-')
                self.status_combo.setCurrentIndex(0)
                self.created_time_label.setText('-')
                self.content_text.clear()
                self.response_text.clear()
            else:
                QMessageBox.warning(self, '警告', '删除反馈失败')
        except Exception as e:
            system_logger.error(f"删除反馈失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'删除反馈失败：{str(e)}')
