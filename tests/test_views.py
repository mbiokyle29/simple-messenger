''' test_views.py '''
from uuid import uuid4

import arrow
from flask import url_for

from simple_messenger.models import (
    db,
    Message,
    User,
)
from tests.base import Base


class TestNewUser(Base):

    def test_new_user(self):
        res = self.client.post(url_for('api.new_user'))
        self.assertEqual(res.status_code, 201)

        self.assertEqual(
            db.session.query(User).count(),
            1,
        )
        created_user = db.session.query(User).all()[0]

        self.assertTrue(res.location.endswith(f'api/users/{created_user.user_id}'))
        self.assertEqual(res.json, created_user.serialize())


class TestListUsers(Base):

    def test_list_users_empty(self):
        res = self.client.get(url_for('api.list_users'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, [])

    def test_list_users_one(self):
        user = self.create_user()
        res = self.client.get(url_for('api.list_users'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json,
            [user.serialize()],
        )

    def test_list_users_many(self):
        num_users = 10
        users = sorted(
            [
                self.create_user().serialize()
                for _ in range(num_users)
            ],
            key=lambda user_dat: user_dat['user_id']
        )

        res = self.client.get(url_for('api.list_users'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            sorted(
                res.json,
                key=lambda user_dat: user_dat['user_id']
            ),
            users,
        )


class TestGetUser(Base):

    def test_get_user_no_users(self):
        res = self.client.get(url_for('api.get_user', user_id=str(uuid4())))
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json['status'], 'NOT_FOUND')

    def test_get_user_wrong_id(self):
        self.create_user()
        res = self.client.get(url_for('api.get_user', user_id=str(uuid4())))
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json['status'], 'NOT_FOUND')

    def test_get_user(self):
        user = self.create_user()
        res = self.client.get(url_for('api.get_user', user_id=str(user.user_id)))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json,
            user.serialize(),
        )


class TestNewMessage(Base):

    def test_new_message_empty_payload_error(self):
        payload = {}
        res = self.client.post(
            url_for('api.new_message'),
            json=payload,
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['status'], 'BAD_REQUEST')
        self.assertIn('create new message', res.json['message'])

        self.assertEqual(
            db.session.query(Message).count(),
            0,
        )

    def test_new_message_no_message_text_error(self):
        payload = {
            'sender_id': str(uuid4()),
            'receiver_id': str(uuid4()),
        }
        res = self.client.post(
            url_for('api.new_message'),
            json=payload,
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['status'], 'BAD_REQUEST')
        self.assertIn('create new message', res.json['message'])

        self.assertEqual(
            db.session.query(Message).count(),
            0,
        )

    def test_new_message_malformed_uuids_error(self):
        payload = {
            'message_text': 'hello',
            'sender_id': 'foobar',
            'receiver_id': str(uuid4()),
        }
        res = self.client.post(
            url_for('api.new_message'),
            json=payload,
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['status'], 'BAD_REQUEST')
        self.assertIn('create new message', res.json['message'])

        self.assertEqual(
            db.session.query(Message).count(),
            0,
        )

    def test_new_message(self):
        sender = self.create_user()
        receiver = self.create_user()

        payload = {
            'sender_id': str(sender.user_id),
            'receiver_id': str(receiver.user_id),
            'message_text': 'test',
        }

        res = self.client.post(
            url_for('api.new_message'),
            json=payload,
        )
        self.assertEqual(res.status_code, 201)

        self.assertEqual(
            db.session.query(Message).count(),
            1,
        )
        created_message = db.session.query(Message).all()[0]

        self.assertTrue(res.location.endswith(f'api/messages/{created_message.message_id}'))
        self.assertEqual(res.json, created_message.serialize())

        self.assertEqual(sender.sent_messages, [created_message])
        self.assertEqual(receiver.received_messages, [created_message])

    def test_new_message_users_created(self):

        sender_id = uuid4()
        receiver_id = uuid4()

        payload = {
            'sender_id': str(sender_id),
            'receiver_id': str(receiver_id),
            'message_text': 'test',
        }

        res = self.client.post(
            url_for('api.new_message'),
            json=payload,
        )
        self.assertEqual(res.status_code, 201)

        self.assertEqual(
            db.session.query(Message).count(),
            1,
        )
        created_message = db.session.query(Message).all()[0]

        self.assertTrue(res.location.endswith(f'api/messages/{created_message.message_id}'))
        self.assertEqual(res.json, created_message.serialize())

        sender = db.session.query(User).get(sender_id)
        receiver = db.session.query(User).get(receiver_id)

        self.assertEqual(sender.sent_messages, [created_message])
        self.assertEqual(receiver.received_messages, [created_message])


class TestListMessages(Base):

    def create_message(self, **kwargs):

        message = Message(
            sender_id=kwargs.get('sender_id', self.create_user().user_id),
            receiver_id=kwargs.get('receiver_id', self.create_user().user_id),
            message_text=kwargs.get('message_text', 'TEST MESSAGE'),
        )

        db.session.add(message)
        db.session.commit()

        return message

    def test_list_messages_empty(self):
        res = self.client.get(url_for('api.list_messages'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, [])

    def test_list_messages_empty_limit(self):
        res = self.client.get(url_for('api.list_messages', limit=1))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, [])

    def test_list_messages_invalid_limit(self):
        res = self.client.get(url_for('api.list_messages', limit='foorbar'))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['status'], 'BAD_REQUEST')
        self.assertIn('limit query', res.json['message'])

    def test_list_messages_empty_since(self):
        res = self.client.get(url_for('api.list_messages', since=arrow.now().isoformat()))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, [])

    def test_list_messages_invalid_since(self):
        res = self.client.get(url_for('api.list_messages', since='foobar'))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['status'], 'BAD_REQUEST')
        self.assertIn('since query', res.json['message'])

    def test_list_messages_empty_conversation(self):
        res = self.client.get(
            url_for(
                'api.list_messages',
                sender_id=str(uuid4()),
                receiver_id=str(uuid4()),
            )
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, [])

    def test_list_messages_missing_sender(self):
        res = self.client.get(
            url_for(
                'api.list_messages',
                receiver_id=str(uuid4()),
            )
        )

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['status'], 'BAD_REQUEST')
        self.assertIn('Cannot list messages between', res.json['message'])

    def test_list_messages_missing_receiver(self):
        res = self.client.get(
            url_for(
                'api.list_messages',
                sender_id=str(uuid4()),
            )
        )

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['status'], 'BAD_REQUEST')
        self.assertIn('Cannot list messages between', res.json['message'])

    def test_list_messages_invalid_sender(self):
        res = self.client.get(
            url_for(
                'api.list_messages',
                sender_id='foobar',
                receiver_id=str(uuid4()),
            )
        )

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['status'], 'BAD_REQUEST')
        self.assertIn('Cannot list messages between', res.json['message'])

    def test_list_messages_invalid_receiver(self):
        res = self.client.get(
            url_for(
                'api.list_messages',
                sender_id=str(uuid4()),
                receiver_id='foobar',
            )
        )

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['status'], 'BAD_REQUEST')
        self.assertIn('Cannot list messages between', res.json['message'])

    def test_list_messages(self):
        message = self.create_message()
        res = self.client.get(url_for('api.list_messages'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, [message.serialize()])

    def test_list_messages_limit(self):
        messages = [
            self.create_message()
            for _ in range(10)
        ]
        res = self.client.get(url_for('api.list_messages', limit=5))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json,
            [message.serialize() for message in messages[-5:][::-1]]
        )

    def test_list_messages_since(self):
        messages = [
            self.create_message()
            for _ in range(10)
        ]
        res = self.client.get(
            url_for(
                'api.list_messages',
                since=messages[-5].created_at.isoformat()
            )
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json,
            [message.serialize() for message in messages[-5:][::-1]]
        )

    def test_list_messages_complex(self):

        # 'old' messages
        for _ in range(10):
            self.create_message()

        # 'new' messages
        new_messages = [
            self.create_message() for _ in range(10)
        ]

        res = self.client.get(
            url_for(
                'api.list_messages',
                limit=5,
                since=new_messages[0].created_at.isoformat(),
            ),
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json,
            [message.serialize() for message in new_messages[-5:][::-1]],
        )

    def test_list_messages_conversation(self):
        sender = self.create_user()
        receiver = self.create_user()

        messages = [
            self.create_message(
                sender_id=str(sender.user_id),
                receiver_id=str(receiver.user_id),
            )
            for _ in range(10)
        ]

        # create some messages outside of this conversation
        self.create_message()
        self.create_message()
        self.create_message()

        res = self.client.get(
            url_for(
                'api.list_messages',
                sender_id=str(sender.user_id),
                receiver_id=str(receiver.user_id),
            ),
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json,
            [
                message.serialize()
                for message in messages[::-1]
            ],
        )

    def test_list_messages_conversation_limit(self):
        sender = self.create_user()
        receiver = self.create_user()

        messages = [
            self.create_message(
                sender_id=str(sender.user_id),
                receiver_id=str(receiver.user_id),
            )
            for _ in range(10)
        ]

        # create some messages outside of this conversation
        self.create_message()
        self.create_message()
        self.create_message()

        res = self.client.get(
            url_for(
                'api.list_messages',
                sender_id=str(sender.user_id),
                receiver_id=str(receiver.user_id),
                limit=2
            ),
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json,
            [
                message.serialize()
                for message in messages[-2:][::-1]
            ],
        )

    def test_list_messages_conversation_since(self):
        sender = self.create_user()
        receiver = self.create_user()

        messages = [
            self.create_message(
                sender_id=str(sender.user_id),
                receiver_id=str(receiver.user_id),
            )
            for _ in range(10)
        ]

        # create some messages outside of this conversation
        self.create_message()
        self.create_message()
        self.create_message()

        res = self.client.get(
            url_for(
                'api.list_messages',
                sender_id=str(sender.user_id),
                receiver_id=str(receiver.user_id),
                since=messages[-3].created_at.isoformat(),
            ),
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json,
            [
                message.serialize()
                for message in messages[-3:][::-1]
            ],
        )

    def test_list_messages_conversation_complex(self):
        sender = self.create_user()
        receiver = self.create_user()

        messages = [
            self.create_message(
                sender_id=str(sender.user_id),
                receiver_id=str(receiver.user_id),
            )
            for _ in range(10)
        ]

        # create some messages outside of this conversation
        self.create_message()
        self.create_message()
        self.create_message()

        res = self.client.get(
            url_for(
                'api.list_messages',
                sender_id=str(sender.user_id),
                receiver_id=str(receiver.user_id),
                since=messages[-3].created_at.isoformat(),
                limit=2,
            ),
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json,
            [
                message.serialize()
                for message in messages[-2:][::-1]
            ],
        )
