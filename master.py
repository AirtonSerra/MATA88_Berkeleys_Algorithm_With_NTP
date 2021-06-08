import threading
import datetime
import socket
import time
from dateutil import parser

HOST = '127.0.0.1'  # IP do HOST.
Port = 1234         # Porta que o processo ficará escutando.

# Datastructure usado para guardar os enderessos dos clientes e o tempo.
client_data = {}
client_data_updated = 0
timeToResync = 5

# Função de thread usada para receber a hora do relógio de um cliente conectado.

def startRecieveingClockTime(connector, address):
    global client_data_updated

    while True:
        # Recebendo tempo do slave.
        clock_time_string = connector.recv(1024).decode()
        clock_time = parser.parse(clock_time_string)
        clock_time_diff = datetime.datetime.now() - \
            clock_time

        client_data[address] = {
            "clock_time": clock_time,
            "time_difference": clock_time_diff,
            "connector": connector
        }

        # Número de clientes que enviaram seu tempo.
        client_data_updated += 1


# Função principal de thread usada para aceitar cliente em uma porta.

def startConnecting(master_server):

    # Recebe a hora dos slaves
    while True:
        # Aceita um novo slave
        master_slave_connector, addr = master_server.accept()
        slave_address = str(addr[0]) + ":" + str(addr[1])

        print(slave_address + " conectou-se com sucesso.")

        current_thread = threading.Thread(
            target=startRecieveingClockTime,
            args=(master_slave_connector,
                  slave_address, ))
        current_thread.start()


# Função usada para buscar a diferença média dos relógios.
def getAverageClockDiff():
    time_difference_list = list(client['time_difference']
                                for client_addr, client
                                in client_data.items())

    sum_of_clock_difference = sum(time_difference_list,
                                  datetime.timedelta(0, 0))

    average_clock_difference = sum_of_clock_difference \
        / len(client_data)

    return average_clock_difference


# Função thread usada para gerar ciclos de sincronização dos relógios dos slaves.

def synchronizeAllClocks():
    global client_data_updated, timeToResync
    while True:

        print("Nova sincronização iniciada.")
        print("Numero de clientes para ser sincronizados: " + str(len(client_data)))

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
                            print("Algo deu errado ao enviar a hora sincronizada para " + str(client_addr))
                time.sleep(1)
        else:
            print("Sem cliente conectados, sincronização não realizada.")

        print("\n\n")

        time.sleep(timeToResync)


# Função utilizada para iniciar o processo principal de Master.
def initiateClockServer():

    master_server = socket.socket()
    master_server.setsockopt(socket.SOL_SOCKET,
                             socket.SO_REUSEADDR, 1)

    master_server.bind((HOST, Port))

    # Começa a escutar as requisições.
    master_server.listen(10)
    print("Master iniciado e escutando a porta: ", Port)

    # Lança a thread responsável por receber novas requisições.
    master_thread = threading.Thread(
        target=startConnecting,
        args=(master_server, ))
    master_thread.start()

    # Lança a thead responsável pela sincronização dos telógios
    sync_thread = threading.Thread(
        target=synchronizeAllClocks,
        args=())
    sync_thread.start()
    

if __name__ == '__main__':

    # Lança o Master Server.
    initiateClockServer()
