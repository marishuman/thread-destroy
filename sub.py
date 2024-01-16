import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://127.0.0.1:2001')
socket.setsockopt_string(zmq.SUBSCRIBE, '')

listener = ["hi", "hello"]

while(True):
    message = socket.recv_pyobj()
    msgIndex = message.keys()[0]
    if(msgIndex in listeners):
        print(message.get(msgIndex))