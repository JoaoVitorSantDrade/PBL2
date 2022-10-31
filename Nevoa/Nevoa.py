import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from random import seed
from random import randint
import time
import os

# Lista dos ids de clientes conectados
lista_clients_conectados = []
# Dicionario com dados do clientes conectados
#lista_clients = {}
lista_consumo_clients = {}
lista_vazao_clients = {}
lista_vazamento_clients = {}
lista_fechado_clients = {}
lista_vazamento_valor_clients = {}
lista_delay_clients = {}

#cria objeto nevoa
def nevoaCliente(id):
    client = create_default_client(id)
    return client
#------------------------------------------------------------------------------------------------
#   Conecta cliente ao Brocker
def Client_Connect(client,host,port):
    client.connect(host,port=port,keepalive=60)
    client.loop_start()
#-------------------------------------------------------------------------------------------------
#  Logs de conexão e publicação 
# Quando uma nova conexão é feita com o brocker
def on_connect_nuvem(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# Quando uma nova publicação é feita pela névoa no brocker
def on_publish_nevoa(client,userdata,mid):
    print(mid)

#-------------------------------------------------------------------------------------------------
#   Métodos para registro dos dados lidos no brocker 

# Quando é feita uma publicação no topico em que a névoa esta inscrita 
# Define o topico e atualiza os dados no dicionario
def on_message_nevoa(client,userdata,message,tmp=None):
    #id_client = int(client._client_id )
    #print(dir(client))
    topico = message.topic
    msg = message.payload
    
    subtopicos = topico.split('/')
    print(subtopicos[1])
    id_client = str(subtopicos[1])
    # salvar valor no client especifico
    if topico == "hidrometro/"+id_client+"/consumo":
        consumo = int(msg)
        lista_consumo_clients[id_client] = consumo
    elif topico == "hidrometro/"+id_client+"/vazao":
        vazao =float(msg)
        lista_vazao_clients[id_client] = vazao
    elif topico == "hidrometro/"+id_client+"/vazamento":
        vazamento = float(msg)
        lista_vazamento_clients[id_client] =vazamento
    elif topico == "hidrometro/"+id_client+"/fechado":
        fechado = bool(msg)
        print(fechado)
        lista_fechado_clients[id_client] = fechado
    elif topico == "hidrometro/"+id_client+"/vazamento_valor":
        vazamento_valor = float(msg)
        lista_vazamento_valor_clients[id_client] = vazamento_valor
    elif topico == "hidrometro/"+id_client+"/delay":
        delay = float(msg)
        lista_vazamento_valor_clients[id_client] = delay

# Quando é feita uma publicação no topico de ids de hidrometros
# Insere o id na Lista
def on_message_nevoa_to_getClients(client, userdata, message,tmp=None):
    lista_clients_conectados.append(client.id)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")
#-------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------
#   Métodos de inscrição de topicos para o cliente
def sub_to_getClients(client):
    client.subscribe("IDENTIFIER/#")
    return client

def sub_to_getValues(client):
    client.subscribe("hidrometro/#") # se inscreve no topico de publicações dos hidrometros
    return client

def on_publish(client,userdata,mid):
    #print(mid)
    print("publicado")

#-------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------
#   Métodos para criação dos clintes mqqt da Nevoa

#   Cria instância de cliente para observar ids dos hidrometros
def create_client_to_se_how_many(id_nevoa):
    client = mqtt.Client(client_id=str(id_nevoa))
    #client.username_pw_set()
    client.on_message = on_message_nevoa_to_getClients
    #client.on_connect = mycallbacks.on_connect
    #client.on_publish = mycallbacks.on_publish
    return client

# Cria instância de cliente para observar topico de plubicação de dados
def create_default_client(id_nevoa):
    client = mqtt.Client(client_id=str(id_nevoa))
    #client.username_pw_set()
    client.on_message = on_message_nevoa
    client.on_connect = on_connect
    client.on_publish = on_publish
    return client

#-------------------------------------------------------------------------------------------------
def main():
    clientMQTT = nevoaCliente(randint(0,100))

    print( int(clientMQTT._client_id))
    connect_host = input("Digite o IP em que devemos nos conectar: ")
    connect_port = int(input("Digite a Porta em que devemos nos conectar: "))

    os.system('cls' if os.name == 'nt' else 'clear')

    #----------------------------------------------------
    try:
        Client_Connect(clientMQTT,connect_host,connect_port) #Conecta ao broker
    except Exception as err:
        print("Erro na conexão do hidrometro - " + err)
    print("Conexão finalzada!")
    clientMQTT = sub_to_getValues(clientMQTT)
    while True:
         time.sleep(3)

if __name__ == '__main__':
    main()