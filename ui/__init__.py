"""
UI模块
"""
from .login import LoginWindow, RegisterDialog
from .admin import AdminDashboard
from .main import MainWindow
from .training import TrainingWindow

__all__ = [
    'LoginWindow',
    'RegisterDialog',
    'AdminDashboard',
    'MainWindow',
    'TrainingWindow'
]
