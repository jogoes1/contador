#!/usr/bin/python
# -*- coding: utf-8 -*-

from localsocket import LocalSocket
import time
from datetime import datetime

__contador = 0
__localSocket = None
__tiempoRecepcion = 1
initialTime = None
endingTime = None
flagReadInitialTime = True
recThroughput = 0
totalData = bytearray()


# test 2
def localSocketConnectionOpen():
    print('Connection Open')


def localSocketDataRead(data):
    global __contador
    global __tiempoRecepcion
    global flagReadInitialTime
    global endingTime
    global initialTime
    global recThroughput
    global totalData

    totalData.extend(data)

    if flagReadInitialTime:
        flagReadInitialTime = False
        print "READ INITIAL TIMER"
        initialTime = datetime.now()
    # __localSocket.writeData(data)

    #    __localSocket.writeData(data)
    #    print "número de bytes leídos= ",len(data)
    # print "número de Es leídas =",data.count("E")
    __contador = __contador + len(data)
    # print('__contador %s = '%__contador)
    # print('data [%s]' % data)

    # Finalizamos conexión al recibir una E
    if data.count("E") == 1:


        # recThroughput=__contador/(str(__tiempoRecepcion)[20:0])
        flagReadInitialTime = True
        endingTime = datetime.now()
        __tiempoRecepcion = endingTime - initialTime
        recThroughput = len(totalData) / __tiempoRecepcion.total_seconds()
        print "//////////////////////////FIN DE UPLOAD TEST///////////////"
        print "tiempo de recepción", __tiempoRecepcion
        print "Número de bytes totales", __contador
        print "Throughput de recepción", recThroughput, "bytes/s"
        print "totalData Length", len(totalData)
        print "Reset Contador bytes"
        print "//////////////////////////////////////////////////////////"
        __contador = 0

        print "Fin de recepción de datos"
        time.sleep(1)
        print "Envío comando de envío datos S==>C"
        __localSocket.writeData("B")
        time.sleep(2)
        print "Envío de datos"
        __localSocket.writeData(totalData)

        print "Cerrar socket"
        __localSocket.stop()


def localSocketConnectionClosed():
    print('Connection Closed')


if __name__ == "__main__":

    __contador = 0
    global __localSocket
    __localSocket = LocalSocket()
    __localSocket.connOpenCallback = localSocketConnectionOpen
    __localSocket.dataReadCallback = localSocketDataRead
    __localSocket.connClosedCallback = localSocketConnectionClosed

    # Check correct values
    if __localSocket.start(5001, 5002, 'TCP'):

        # print "time.sleep start"
        # time.sleep(20)
        # print "time.sleep stop"

        # Serial and local socket are both connected
        # now just enable redirection
        print('Waiting for local socket connection')
    else:
        print('Error opening local ports')
