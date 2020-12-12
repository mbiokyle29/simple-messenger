''' test_models.py '''
from datetime import datetime
from uuid import UUID

from simple_messenger.models import (
    db,
    Message,
    User,
)
from tests.base import Base


class TestModels(Base):

    def create_user(self):
        user = User()
        db.session.add(user)
        db.session.commit()

        return user

    def test_user_create(self):
        user = User()
        db.session.add(user)
        db.session.commit()

        self.assertIs(type(user.user_id), UUID)
        self.assertEqual(user.sent_messages, [])
        self.assertEqual(user.received_messages, [])

    def test_message_create(self):

        user = self.create_user()

        message_text = 'foo bar test'
        message = Message(
            message_text=message_text,
            sender_id=user.user_id,
            receiver_id=user.user_id,
        )
        db.session.add(message)
        db.session.commit()

        self.assertIs(type(message.message_id), UUID)
        self.assertIs(type(message.sender_id), UUID)
        self.assertIs(type(message.receiver_id), UUID)
        self.assertIs(type(message.created_at), datetime)

    def test_sender_relationship(self):

        sender_user = self.create_user()
        receiver_user = self.create_user()

        message_text = 'foo bar test'
        message = Message(
            message_text=message_text,
            sender_id=sender_user.user_id,
            receiver_id=receiver_user.user_id,
        )
        db.session.add(message)
        db.session.commit()

        self.assertEqual(message.sender_id, sender_user.user_id)
        self.assertIs(message.sender, sender_user)
        self.assertEqual(sender_user.sent_messages, [message])

    def test_receiver_relationship(self):

        sender_user = self.create_user()
        receiver_user = self.create_user()

        message_text = 'foo bar test'
        message = Message(
            message_text=message_text,
            sender_id=sender_user.user_id,
            receiver_id=receiver_user.user_id,
        )
        db.session.add(message)
        db.session.commit()

        self.assertEqual(message.receiver_id, receiver_user.user_id)
        self.assertIs(message.receiver, receiver_user)
        self.assertEqual(receiver_user.received_messages, [message])

    def test_self_send(self):
        ''' Sending messages to yourself is supported '''
        user = self.create_user()

        message_text = 'foo bar test'
        message = Message(
            message_text=message_text,
            sender_id=user.user_id,
            receiver_id=user.user_id,
        )
        db.session.add(message)
        db.session.commit()

        self.assertEqual(message.sender_id, user.user_id)
        self.assertIs(message.sender, user)
        self.assertEqual(user.sent_messages, [message])

        self.assertEqual(message.receiver_id, user.user_id)
        self.assertIs(message.receiver, user)
        self.assertEqual(user.received_messages, [message])
