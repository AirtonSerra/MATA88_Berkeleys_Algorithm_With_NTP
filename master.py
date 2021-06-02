from functools import reduce
import threading
import datetime
import socket
import time
from dateutil import parser

HOST = '127.0.0.1'  # IP HOST

# datastructure used to store client address and clock data
client_data = {}
client_data_updated = 0

''' nested thread function used to receive 
    clock time from a connected client '''


def startRecieveingClockTime(connector, address):
    global client_data_updated

    while True:
        # recieve clock time
        clock_time_string = connector.recv(1024).decode()
        clock_time = parser.parse(clock_time_string)
        clock_time_diff = datetime.datetime.now() - \
            clock_time

        client_data[address] = {
            "clock_time": clock_time,
            "time_difference": clock_time_diff,
            "connector": connector
        }

        # number of clients who sent their time
        client_data_updated += 1


''' master thread function used to open portal for 
    accepting clients over given port '''


def startConnecting(master_server):

    # fetch clock time at slaves / clients
    while True:
        # accepting a client / slave clock client
        master_slave_connector, addr = master_server.accept()
        slave_address = str(addr[0]) + ":" + str(addr[1])

        print(slave_address + " got connected successfully")

        current_thread = threading.Thread(
            target=startRecieveingClockTime,
            args=(master_slave_connector,
                  slave_address, ))
        current_thread.start()


# subroutine function used to fetch average clock difference
def getAverageClockDiff():

    current_client_data = client_data.copy()

    time_difference_list = list(client['time_difference']
                                for client_addr, client
                                in client_data.items())

    sum_of_clock_difference = sum(time_difference_list,
                                  datetime.timedelta(0, 0))

    average_clock_difference = sum_of_clock_difference \
        / len(client_data)

    return average_clock_difference


''' master sync thread function used to generate 
    cycles of clock synchronization in the network '''


def synchronizeAllClocks():
    global client_data_updated
    while True:

        print("New synchroniztion cycle started.")
        print("Number of clients to be synchronized: " + str(len(client_data)))

        if len(client_data) > 0:
            client_data_updated = 0

            for client_addr, client in client_data.items():
                client['connector'].send(str("REQUEST_TIME").encode())

            wU = True
            while wU == True:
                # Se recebeu a resposta com o tempo de todos os clientes
                if len(client_data) == client_data_updated:
                    wU = False

                    average_clock_difference = getAverageClockDiff()
                    for client_addr, client in client_data.items():
                        try:
                            synchronized_time = \
                                datetime.datetime.now() + \
                                average_clock_difference

                            client['connector'].send(str(
                                synchronized_time).encode())

                        except Exception as e:
                            print("Something went wrong while " +
                                "sending synchronized time " +
                                "through " + str(client_addr))

                time.sleep(1)
        else:
            print("No client data." +
                  " Synchronization not applicable.")

        print("\n\n")

        time.sleep(5)


# function used to initiate the Clock Server / Master Node
def initiateClockServer(port=8080):

    master_server = socket.socket()
    master_server.setsockopt(socket.SOL_SOCKET,
                             socket.SO_REUSEADDR, 1)

    print("Socket at master node created successfully\n")

    master_server.bind((HOST, port))

    # Start listening to requests
    master_server.listen(10)
    print("Clock server started...\n")

    # start making connections
    print("Starting to make connections...\n")
    master_thread = threading.Thread(
        target=startConnecting,
        args=(master_server, ))
    master_thread.start()

    # start synchroniztion
    print("Starting synchronization parallely...\n")
    sync_thread = threading.Thread(
        target=synchronizeAllClocks,
        args=())
    sync_thread.start()


# Driver function
if __name__ == '__main__':

    # Trigger the Clock Server
    initiateClockServer(port=8080)
