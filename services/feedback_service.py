
"""
反馈服务
提供用户问题反馈的提交、查看和处理功能
"""
from datetime import datetime
from typing import List, Dict, Optional
from .database import db_service
from utils import system_logger

class FeedbackService:
    """反馈服务类"""

    def submit_feedback(self, user_id: int, title: str, content: str, 
                      category: str = None, email: str = None) -> bool:
        """
        提交反馈

        Args:
            user_id: 用户ID
            title: 反馈标题
            content: 反馈内容
            category: 反馈类别
            email: 联系邮箱

        Returns:
            bool: 是否提交成功
        """
        try:
            db_service.execute_query(
                """INSERT INTO feedbacks 
                (user_id, title, content, category, email, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (user_id, title, content, category, email, 'pending', datetime.now()),
                fetch=False
            )
            system_logger.info(f"反馈提交成功: user_id={user_id}, title={title}")
            return True
        except Exception as e:
            system_logger.error(f"提交反馈失败: {str(e)}")
            return False

    def get_all_feedbacks(self, limit: int = 100) -> List[Dict]:
        """
        获取所有反馈（管理员用）

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict]: 反馈列表
        """
        try:
            feedbacks = db_service.execute_query(
                """SELECT f.*, u.username 
                FROM feedbacks f 
                LEFT JOIN users u ON f.user_id = u.id
                ORDER BY f.created_at DESC 
                LIMIT %s""",
                (limit,)
            )
            return feedbacks or []
        except Exception as e:
            system_logger.error(f"获取反馈列表失败: {str(e)}")
            return []

    def get_user_feedbacks(self, user_id: int, limit: int = 50) -> List[Dict]:
        """
        获取用户的反馈

        Args:
            user_id: 用户ID
            limit: 返回数量限制

        Returns:
            List[Dict]: 反馈列表
        """
        try:
            feedbacks = db_service.execute_query(
                """SELECT * FROM feedbacks 
                WHERE user_id = %s
                ORDER BY created_at DESC 
                LIMIT %s""",
                (user_id, limit)
            )
            return feedbacks or []
        except Exception as e:
            system_logger.error(f"获取用户反馈失败: {str(e)}")
            return []

    def update_feedback_status(self, feedback_id: int, status: str, 
                            response: str = None) -> bool:
        """
        更新反馈状态

        Args:
            feedback_id: 反馈ID
            status: 新状态
            response: 回复内容

        Returns:
            bool: 是否更新成功
        """
        try:
            if response:
                db_service.execute_query(
                    """UPDATE feedbacks 
                    SET status = %s, response = %s, updated_at = %s
                    WHERE id = %s""",
                    (status, response, datetime.now(), feedback_id),
                    fetch=False
                )
            else:
                db_service.execute_query(
                    """UPDATE feedbacks 
                    SET status = %s, updated_at = %s
                    WHERE id = %s""",
                    (status, datetime.now(), feedback_id),
                    fetch=False
                )
            system_logger.info(f"反馈状态更新成功: id={feedback_id}, status={status}")
            return True
        except Exception as e:
            system_logger.error(f"更新反馈状态失败: {str(e)}")
            return False

    def delete_feedback(self, feedback_id: int) -> bool:
        """
        删除反馈

        Args:
            feedback_id: 反馈ID

        Returns:
            bool: 是否删除成功
        """
        try:
            db_service.execute_query(
                "DELETE FROM feedbacks WHERE id = %s",
                (feedback_id,),
                fetch=False
            )
            system_logger.info(f"反馈删除成功: id={feedback_id}")
            return True
        except Exception as e:
            system_logger.error(f"删除反馈失败: {str(e)}")
            return False

# 全局反馈服务实例
feedback_service = FeedbackService()
