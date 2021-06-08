from timeit import default_timer as timer
import threading
import datetime
import socket
import ntplib
import datetime
from time import ctime
from dateutil import parser

HOST = '127.0.0.1'  # IP do HOST
Port = 1234         # Porta que o processo de Master ficará escutando.
K = 700000  # K em microsegundos
TimeSended = None


# Função utilizada para enviar o tempo.
def sendingTime(slave_client):
    global TimeSended
    TimeSended = str(datetime.datetime.now())
    slave_client.send(TimeSended.encode())


# Thread utilizada para receber as mensagens do Master.
def startReceivingTime(slave_client):
    global TimeSended

    while True:
        # Recebe dados de Master.
        message = slave_client.recv(1024).decode()
        if (message == "REQUEST_TIME"):
           sendingTime(slave_client)
        else:
            serverDate =  parser.parse(message)

            # Pega o tempo do servidor NTP[k.pool.ntp.org] para comparação.
            try:
                c = ntplib.NTPClient()
                response = c.request('uk.pool.ntp.org', version=3)
                response.offset
                ntpDate = parser.parse(ctime(response.tx_time))
            except:
                ntpDate = None
           
            if ntpDate != None:
                if ntpDate > serverDate:
                    dif = ntpDate - serverDate 
                else:
                    dif = serverDate - ntpDate


            print("Tempo antes da sincronização: {}\nTempo depois da sincronização: {}\nTempo NTP: {}\nDiferença entre tempo sincronizado e tempo NTP: {}".format(TimeSended, serverDate, (ntpDate if ntpDate !=  None else "Servidor NTP não respondeu."), (dif if ntpDate !=  None else "Incalculável.")))

            if ntpDate != None:
                # Pega a diferença em microssegundos e verifique se é maior que K.
                if (dif.seconds*1000000) + dif.microseconds > K:
                    print("Essa diferença é maior que K(", K,"), nova sicronização necessária.",  end="\n\n")
                else:
                    print("Essa diferença não é maior que K(", K,").",  end="\n\n")
            else:
                print("")


            

# Função utilizada para iniciar o processo principal de Slave.
def initiateSlaveClient():

    slave_client = socket.socket()

    # Conecta-se ao processo de Master.
    slave_client.connect((HOST, Port))

    # Envia o tempo para master pela primeira vês para que Master guarde seu endereço.
    sendingTime(slave_client)
    print("Salve iniciado e ao servidor {}:{}".format(str(HOST), str(Port)), end="\n\n")

    # Lança a threde responsável por receber o tempo sincronizado de master e fazer as comparações.
    receive_time_thread = threading.Thread(
        target=startReceivingTime,
        args=(slave_client, ))
    receive_time_thread.start()

if __name__ == '__main__':

    # Lança o client Slave
    initiateSlaveClient()
