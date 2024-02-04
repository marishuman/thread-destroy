import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://127.0.0.1:2000')
socket.setsockopt_string(zmq.SUBSCRIBE, '')

listeners = ["hi", "hello"]

while(True):
    message = socket.recv_pyobj()
    first_value = list(message)[0]
    second_value = list(message)[1]
    print(first_value)
    print(second_value)
