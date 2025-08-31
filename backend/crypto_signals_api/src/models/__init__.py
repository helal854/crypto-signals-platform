from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .telegram_user import TelegramUser
from .integration import Integration
from .message_template import MessageTemplate
from .spot_signal import SpotSignal
from .futures_signal import FuturesSignal
from .payment import Payment
from .broadcast_message import BroadcastMessage
from .futures_setting import FuturesSetting
from .futures_trader import FuturesTrader
from .audit_log import AuditLog

