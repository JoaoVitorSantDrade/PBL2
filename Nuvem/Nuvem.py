import paho.mqtt.client as mqtt
import mycallbacks
import paho.mqtt.publish as publish
import config_nuvem

# Lista das médias de nevoas conectadas
media_nevoas_conectadas = []

# Quando uma nova conexão é feita com o brocker
def on_connect_nevoa(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# Quando é feita uma publicação no topico em que a Nuvem esta inscrita 
# Define o topico e atualiza os dados no dicionario
def on_message_nevoa(client,userdata,message,tmp=None):
    id_client = client.id
    topico = message.topic
    msg = message.payload
    # salvar valor no client especifico
    media_nevoas_conectadas[id_client][topico] =msg

# Quando uma nova publicação é feita pela Nuvem no brocker
def on_publish_nuvem(client,userdata,mid):
    print(mid)

# Cria instância de cliente para observar topico de plubicação de dados
def create_default_client(id_nevoa):
    client = mqtt.Client(client_id=str(id_nevoa))
    #client.username_pw_set()
    client.on_message = on_message_nevoa
    #client.on_connect = mycallbacks.on_connect
    #client.on_publish = mycallbacks.on_publish
    return client