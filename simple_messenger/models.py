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

    @classmethod
    def get_or_create(cls, user_id):

        existing_user = db.session.query(cls).get(user_id)

        if existing_user is None:
            existing_user = cls(user_id=user_id)
            db.session.add(existing_user)
            db.session.commit()

        return existing_user

    def serialize(self):
        return {'user_id': str(self.user_id)}


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

    def serialize(self):
        return {
            'message_id': str(self.message_id),
            'created_at': self.created_at.isoformat(),
            'sender_id': str(self.sender_id),
            'receiver_id': str(self.receiver_id),
            'message_text': self.message_text,
        }
