from .admin import admin_router
from .chat import chat_router
from .prediction import prediction_router
from .common import common_router

__all__ = ['admin_router', 'chat_router', 'prediction_router', 'common_router']