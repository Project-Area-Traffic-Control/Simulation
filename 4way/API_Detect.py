import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

@sio.event
def my_message(data):
    print('message received with ', data)
    sio.emit('my response', {'response': 'my response'})

@sio.event
def disconnect():
    print('disconnected from server')

@sio.on('setPhase5')
def on_message(data):
    print('I received a message!',data)

@sio.on('setMode5')
def on_message(data):
    print('I received a message!',data)

sio.connect('http://localhost:3000')