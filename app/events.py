from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from app.models import Message, User, Group
from flask_login import current_user
from datetime import datetime

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('message', {'msg': username + ' has entered the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('message', {'msg': username + ' has left the room.'}, room=room)

@socketio.on('message')
def on_message(data):
    room = data['room']
    user_id = current_user.id
    group_id = room # Assuming room is group_id
    content = data['msg']
    message = Message(content=content, user_id=user_id, group_id=group_id)
    db.session.add(message)
    db.session.commit()
    emit('message', {'msg': current_user.username + ': ' + content, 'username': current_user.username, 'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}, room=room)
