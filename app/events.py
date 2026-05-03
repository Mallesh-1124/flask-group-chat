from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from app.models import Message, User, Group, MessageReadReceipt
from flask_login import current_user
from datetime import datetime


@socketio.on('join')
def on_join(data):
    # Fix: guard against unauthenticated SocketIO connections
    if not current_user.is_authenticated:
        return
    username = data.get('username')
    room = data.get('room')
    if not room:
        return
    join_room(room)
    emit('message', {'msg': username + ' has entered the room.'}, room=room)


@socketio.on('leave')
def on_leave(data):
    if not current_user.is_authenticated:
        return
    username = data.get('username')
    room = data.get('room')
    if not room:
        return
    leave_room(room)
    emit('message', {'msg': username + ' has left the room.'}, room=room)


@socketio.on('message')
def on_message(data):
    if not current_user.is_authenticated:
        return
    room = data.get('room')
    content = data.get('msg', '').strip()
    if not room or not content:
        return

    group_id = room  # room equals group_id
    message = Message(content=content, user_id=current_user.id, group_id=group_id)
    db.session.add(message)
    db.session.commit()

    emit(
        'message',
        {
            'msg': current_user.username + ': ' + content,
            'username': current_user.username,
            'timestamp': message.timestamp.isoformat(),
            'message_id': message.id
        },
        room=room
    )


@socketio.on('typing_start')
def on_typing_start(data):
    if not current_user.is_authenticated:
        return
    room = data.get('room')
    if not room:
        return
    emit('typing_start', {'username': current_user.username}, room=room, include_self=False)


@socketio.on('typing_stop')
def on_typing_stop(data):
    if not current_user.is_authenticated:
        return
    room = data.get('room')
    if not room:
        return
    emit('typing_stop', {'username': current_user.username}, room=room, include_self=False)


@socketio.on('message_read')
def on_message_read(data):
    if not current_user.is_authenticated:
        return
    message_id = data.get('message_id')
    room = data.get('room')
    if not message_id or not room:
        return

    user_id = current_user.id

    # Check if the read receipt already exists
    read_receipt = db.session.get(MessageReadReceipt, (user_id, message_id))
    if not read_receipt:
        read_receipt = MessageReadReceipt(user_id=user_id, message_id=message_id)
        db.session.add(read_receipt)
        db.session.commit()

        emit(
            'message_read_status_update',
            {
                'message_id': message_id,
                'user_id': user_id,
                'timestamp': read_receipt.timestamp.isoformat()
            },
            room=room
        )

@socketio.on('delete_message')
def on_delete_message(data):
    if not current_user.is_authenticated:
        return
    message_id = data.get('message_id')
    room = data.get('room')
    if not message_id or not room:
        return

    message = db.session.get(Message, message_id)
    if message and message.user_id == current_user.id and str(message.group_id) == str(room):
        db.session.delete(message)
        db.session.commit()
        emit('message_deleted', {'message_id': message_id}, room=room)
