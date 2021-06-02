from timeit import default_timer as timer
import threading
import datetime
import socket
import ntplib
import datetime
from time import ctime
from dateutil import parser

HOST = '127.0.0.1'  # IP HOST
K = 1 * 1000000  # K is in microseconds


# function used to send time at client side
def sendingTime(slave_client):
    # provide server with clock time at the client
    slave_client.send(str(datetime.datetime.now()).encode())


# client thread function used to receive synchronized time
def startReceivingTime(slave_client):
    c = ntplib.NTPClient()

    while True:
        # receive data from the server
        message = slave_client.recv(1024).decode()
        if (message == "REQUEST_TIME"):
           sendingTime(slave_client)
        else:
            # get time of ntplib k.pool.ntp.org to comparison
            response = c.request('uk.pool.ntp.org', version=3)
            response.offset
            ntpDate = parser.parse(ctime(response.tx_time))
            serverDate =  parser.parse(message)

            if ntpDate > serverDate:
                dif = ntpDate - serverDate 
            else:
                dif = serverDate - ntpDate 
            
            # take the difference in microseconds and check if it is greater than k
            if (dif.seconds*1000000) + dif.microseconds > K:
                print("Time change\nBefore: ", serverDate, " After: ", ntpDate, end="\n\n")
            else:
                print("Synchronized time at the client is: " + str(message), end="\n\n")

            


# function used to Synchronize client process time
def initiateSlaveClient(port=8080):

    slave_client = socket.socket()

    # connect to the clock server on local computer
    slave_client.connect((HOST, port))

    # send time for the first time
    sendingTime(slave_client)

    # start recieving synchronized from server
    print("Starting to recieving synchronized time\n")
    receive_time_thread = threading.Thread(
        target=startReceivingTime,
        args=(slave_client, ))
    receive_time_thread.start()


# Driver function
if __name__ == '__main__':

    # initialize the Slave / Client
    initiateSlaveClient(port=8080)


# ntpDate = datetime.datetime.strptime(ctime(response.tx_time), "%a %b %d %H:%M:%S %Y")
# serverDate = datetime.datetime.strptime(message, '%Y-%m-%d %H:%M:%S.%f')
