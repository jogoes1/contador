#!/usr/bin/python
from localsocket import LocalSocket

#test 2
def localSocketConnectionOpen():
    print('Connection Open')

def localSocketDataRead(data):
    print('data [%s]' % data)

def localSocketConnectionClosed():
    print('Connection Closed')

if __name__ == "__main__":
    __localSocket = LocalSocket()
    __localSocket.connOpenCallback = localSocketConnectionOpen
    __localSocket.dataReadCallback = localSocketDataRead
    __localSocket.connClosedCallback = localSocketConnectionClosed

    # Check correct values
    if __localSocket.start(5001, 5002, 'TCP'):
        # Serial and local socket are both connected
        # now just enable redirection
        print('Waiting for local socket connection')
    else:
        print('Error opening local ports')

