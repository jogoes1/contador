import socket
import select
import errno
import threading
from time import sleep
from pprint import pprint


RX_BUFFER_SIZE = 4096

class LocalSocket(object):
# This class receives connection requests from the drivers and handles the
# communication with them to get the driver_id and return the new ip and port
# of the engine to connect to

    # Callback
    dataReadCallback = None
    connOpenCallback = None
    connClosedCallback = None

    def __init__(self):
        self.status = False
        self.connOpen = False
        self.__socketType = ''
        self.__listenSocket = None
        self.__connSocket = None
        self.__udpDownSocket = None
        self.__socketThread = None
        self.__remoteAddress = ('', 5001)

    def start(self, port, downPort, socketType):
        result = True

        if self.status and socketType not in ['TCP', 'UDP']:
            result = False
        else:
            try:
                if socketType == 'TCP':
                    self.__listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    # Bind the socket to the port
                    self.__remoteAddress = ("", port)  # to connect from outside the machine
                    self.__listenSocket.bind(self.__remoteAddress)
                    print('Starting request port on port ' + str(port))
                    target = self._listen_thread
                    self.status = True

                elif socketType == 'UDP':
                    # Uplink socket (read)
                    self.__connSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    uplinkAddr = ("127.0.0.1", port)
                    self.__connSocket.bind(uplinkAddr)
                    self.__connSocket.setblocking(0)
                    self.__connSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                    # Downlink socket (write)
                    self.__remoteAddress = ("127.0.0.1", downPort)
                    self.__udpDownSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    self.__udpDownSocket.setblocking(0)

                    print('Open socket on port ' + str(port))
                    target = self._udp_listen_thread
                    self.status = True
                    self.connOpenCallback()

            except socket.error, v:
                print('Error starting local socket Port ' + v.strerror)
                result = False

        if result:
            self.__socketType = socketType
            self.__socketThread = threading.Thread(target=target, args=())
            self.__socketThread.start()

        return result

    def stop(self):
        if self.status:
            self.status = False
            self.connOpen = False

	    print "connSocket"
            if self.__connSocket is not None:
                try:
		    print "connSocket shutdown + close"
                    self.__connSocket.shutdown(socket.SHUT_RDWR)
                    self.__connSocket.close()
                except socket.error, v:
                    print('Error closing Socket Port' + v.strerror)

            if self.__listenSocket is not None:
                try:
		    print "listenSocket shutdown + close"
                    self.__listenSocket.shutdown(socket.SHUT_RDWR)
                    self.__listenSocket.close()
                except socket.error, v:
                    print('Error closing Socket Port, ' + v.strerror)

#            if self.__socketThread.isAlive():
#		print "socketThread.join()"
#                self.__socketThread.join()

    def _listen_thread(self):

        if not self.status:
            return

        try:
            # Listen for incoming connections
            self.__listenSocket.listen(1)
        except socket.error, v:
            print('Socket error listening, ' + v.strerror)

        while self.status:

            try:
                print('Waiting for new connection')
                # Wait for a connection
                self.__connSocket, client_address = self.__listenSocket.accept()
                print('New Connection from ' + client_address[0])
                self.connOpen = True
                self.connOpenCallback()

                if not self._receive_data():
                    print('Connection closed')
                    self.connClosedCallback()
                    self.stop()

            except socket.error:
                print('Exception accepting new connection')
                self.stop()

    def _receive_data(self):

        rx_error = False
        while self.status and not rx_error:
            try:
                rx_bytes = bytearray(self.__connSocket.recv(RX_BUFFER_SIZE))
                if rx_bytes is not None:
                    self.dataReadCallback(rx_bytes)
                else:
                    # Connection closed
                    rx_error = True

            except socket.error:
                rx_error = True

        return rx_error

    def _udp_listen_thread(self):

        rx_error = False

        while self.status and not rx_error:
            try:
                ready_to_read, ready_to_write, in_error = select.select(
                    [self.__connSocket], [], [])

                if ready_to_read:
                    data, addr = self.__connSocket.recvfrom(RX_BUFFER_SIZE)

                    #print "Message received %s" % data
                    if data:
                        rx_bytes = bytearray(data)
                        self.dataReadCallback(rx_bytes)
                        #sleep(0.001)
                elif ready_to_write:
                    continue
                else:
                    # Connection closed
                    rx_error = True

            except socket.error, v:
                rx_error = True
                print('Exception receiving data new connection, ' + v.strerror)

        print "exit udp read"
        return rx_error


    def writeData(self, tx_data):

        #print "Sending message %s length %d" % (tx_data, len(tx_data))
        if self.status:
            try:
                if self.__socketType == 'TCP':
                    self.__connSocket.sendall(tx_data)
                else:
                    self.__udpDownSocket.sendto(tx_data, self.__remoteAddress)
            except socket.error, v:
                print("Error sending mesage " + v.strerror)
