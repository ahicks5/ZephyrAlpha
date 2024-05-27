from flask_socketio import emit, join_room
from flask import request
from .. import socketio, db  # Import socketio instance and db from your app package
from ..models.models import Message  # Adjust import as necessary
from ..utilities.message_utils import clean_message

@socketio.on('connect')
def handle_connect():
    print(f"User {request.sid} connected.")
    # Additional connect logic here

@socketio.on('send_message')
def handle_send_message(data):
    print("~~~~Send Message Data Received:~~~~", data)

    # Clean the message first
    cleaned_message = clean_message(data['message'])

    # Create a new Message instance with the cleaned data
    message = Message(text=cleaned_message, game_id=data['roomId'])

    # Add the Message instance to the session and commit
    try:
        db.session.add(message)
        db.session.commit()
        print("~~~~Send Message Data Uploaded:~~~~", cleaned_message)
        emit('receive_message', {'message': cleaned_message}, room=data['roomId'], include_self=True)
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"An error occurred: {e}")


@socketio.on('join_room')
def on_join(data):
    room = data['roomId']
    join_room(room)
    print(f"User {request.sid} joined room {room}.")
    emit('join_confirmation', {'room': room}, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"User {request.sid} disconnected.")
