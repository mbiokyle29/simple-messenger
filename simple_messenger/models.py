''' models.py '''
import uuid

from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):

    user_id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )

    sent_messages = db.relationship(
        'Message',
        backref='sender',
        lazy=True,
        foreign_keys='Message.sender_id',
    )
    received_messages = db.relationship(
        'Message',
        backref='receiver',
        lazy=True,
        foreign_keys='Message.receiver_id',
    )


class Message(db.Model):

    message_id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    message_text = db.Column(
        db.String,
        nullable=False,
    )

    sender_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('user.user_id'),
        nullable=False,
    )

    receiver_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('user.user_id'),
        nullable=False,
    )
