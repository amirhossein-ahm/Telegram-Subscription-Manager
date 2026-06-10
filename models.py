from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    create_engine,
    event,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from config import Config


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    if not Config.DATABASE_URL.startswith("sqlite"):
        return

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


Base = declarative_base()

engine = create_engine(Config.DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

subscription_channels = Table(
    "subscription_channels",
    Base.metadata,
    Column(
        "subscription_id",
        Integer,
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "channel_id",
        Integer,
        ForeignKey("channels.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)

    name = Column(String(255), nullable=False)

    remark_name = Column(String(255), nullable=True)

    token = Column(String(128), nullable=False, unique=True)

    base64_enabled = Column(Boolean, default=True, nullable=False)

    message_limit = Column(
        Integer,
        nullable=False,
        default=Config.DEFAULT_MESSAGE_LIMIT,
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    channels = relationship(
        "Channel",
        secondary=subscription_channels,
        lazy="joined",
    )


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)

    level = Column(String(20), nullable=False)

    message = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


@contextmanager
def db_session():
    db = SessionLocal()

    try:
        yield db

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
