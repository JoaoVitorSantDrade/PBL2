import paho.mqtt.client as mqtt
import mycallbacks
import paho.mqtt.publish as publish

# Lista dos ids de clientes conectados
lista_clients_conectados = []
# Dicionario com dados do clientes conectados
lista_clients = {}

# Quando uma nova conexão é feita com o brocker
def on_connect_nuvem(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# Quando uma nova publicação é feita pela névoa no brocker
def on_publish_nevoa(client,userdata,mid):
    print(mid)

# Quando é feita uma publicação no topico em que a névoa esta inscrita 
# Define o topico e atualiza os dados no dicionario
def on_message_nevoa(client,userdata,message,tmp=None):
    id_client = client.id
    topico = message.topic
    msg = message.payload
    # salvar valor no client especifico
    lista_clients[id_client]= msg 

# Quando é feita uma publicação no topico de ids de hidrometros
# Insere o id na Lista
def on_message_nevoa_to_getClients(client, userdata, message,tmp=None):
    lista_clients_conectados.append(client.id)


def sub_to_getClients(client):
    client.subscribe("IDENTIFIER/#")
    return client


def sub_to_getValues(client):
    client.subscribe("hidrometros/"+client.id+"/#")


# Cria instância de cliente para observar ids dos hidrometros
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
    #client.on_connect = mycallbacks.on_connect
    #client.on_publish = mycallbacks.on_publish
    return client