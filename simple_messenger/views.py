''' views.py '''
from uuid import UUID

import arrow
from flask import Blueprint, jsonify, request

from simple_messenger.exceptions import SimpleMessengerException
from simple_messenger.models import (
    db,
    Message,
    User,
)


api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/users', methods=['POST'])
def new_user():
    user = User()
    db.session.add(user)
    db.session.commit()

    return (
        jsonify(user.serialize()),
        201,
        {'Location': f'/api/users/{user.user_id}'}
    )


@api.route('/users', methods=['GET'])
def list_users():
    users = db.session.query(User).all()
    return jsonify([user.serialize() for user in users]), 200


@api.route('/users/<uuid:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.query(User).get_or_404(user_id)
    return jsonify(user.serialize()), 200


@api.route('/messages', methods=['POST'])
def new_message():

    message_data = request.json
    sender = User.get_or_create(message_data['sender_id'])
    receiver = User.get_or_create(message_data['receiver_id'])

    message = Message(
        message_text=message_data['message_text'],
        sender_id=sender.user_id,
        receiver_id=receiver.user_id,
    )
    db.session.add(message)
    db.session.commit()

    return (
        jsonify(message.serialize()),
        201,
        {'Location': f'/api/messages/{message.message_id}'}
    )


@api.route('/messages', methods=['GET'])
def list_messages():

    # if either are specified, both must be
    # both must also be valid uuids
    sender_query_id = request.args.get('sender_id')
    receiver_query_id = request.args.get('receiver_id')
    if sender_query_id is not None or receiver_query_id is not None:

        try:
            sender_query_id = UUID(sender_query_id)
            receiver_query_id = UUID(receiver_query_id)
        except (TypeError, ValueError):
            raise SimpleMessengerException(
                (
                    'Cannot list messages between '
                    f'sender:{sender_query_id} and '
                    f'receiver:{receiver_query_id}, '
                    'query IDs must both be valid UUIDs'
                ),
                'BAD_REQUEST',
                400,
            )

        base_query = db.session.query(
            Message,
        ).filter(
            Message.sender_id == sender_query_id,
        ).filter(
            Message.receiver_id == receiver_query_id
        ).order_by(
            Message.created_at.desc(),
        )

    else:
        base_query = db.session.query(
            Message,
        ).order_by(
            Message.created_at.desc(),
        )

    if 'since' in request.args:
        try:
            since = arrow.get(request.args['since']).naive
        except Exception as e:
            raise SimpleMessengerException(
                (
                    f'Cannot apply since query with value: {request.args["since"]}! '
                    f'Error parsing to datetime: {e}'
                ),
                'BAD_REQUEST',
                400,
            )

        base_query = base_query.filter(
            Message.created_at >= since,
        )

    if 'limit' in request.args:
        try:
            limit = int(request.args['limit'])
        except Exception as e:
            raise SimpleMessengerException(
                (
                    f'Cannot apply limit query with value: {request.args["limit"]}! '
                    f'Error parsing to integer: {e}'
                ),
                'BAD_REQUEST',
                400,
            )
        base_query = base_query.limit(limit)

    return jsonify([
        message.serialize() for message in base_query.all()
    ]), 200
