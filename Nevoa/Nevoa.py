import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from random import seed
from threading import Thread
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
#   Valores fixos para bloqueio dos Hidrometros
media = 1.0
limite_consumo = 1.0

#cria objeto nevoa
def nevoaCliente():
    id = randint(0,100)
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

def on_publish(client,userdata,mid):
    #print(mid)
    print("publicado")

#-------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------
#   Método para publicação em topicos
def Publish(client,topic,message):
    client.publish("IDENTIFIER/" + str(client._client_id),"1")
    return client.publish(topic,message)

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
        consumo = float(msg)
        lista_consumo_clients[id_client] = consumo
        print(lista_consumo_clients[id_client])
    elif topico == "hidrometro/"+id_client+"/vazao":
        vazao =float(msg)
        lista_vazao_clients[id_client] = vazao
        print(lista_vazao_clients[id_client])
    elif topico == "hidrometro/"+id_client+"/vazamento":
        vazamento = float(msg)
        lista_vazamento_clients[id_client] =vazamento
        print(lista_vazamento_clients[id_client])
    elif topico == "hidrometro/"+id_client+"/fechado":
        fechado = int(msg)
        print(fechado)
        lista_fechado_clients[id_client] = fechado
        print(lista_fechado_clients[id_client])
    elif topico == "hidrometro/"+id_client+"/vazamento_valor":
        vazamento_valor = float(msg)
        lista_vazamento_valor_clients[id_client] = vazamento_valor
        print(lista_vazamento_valor_clients[id_client])
    elif topico == "hidrometro/"+id_client+"/delay":
        delay = float(msg)
        lista_vazamento_valor_clients[id_client] = delay
        print(lista_vazamento_valor_clients[id_client])

# Quando é feita uma publicação no topico de ids de hidrometros
# Insere o id na Lista
def on_message_nevoa_to_getClients(client, userdata, message,tmp=None):
    msg =message.payload
    print("Novo cliente"+str(msg))
    lista_clients_conectados.append(client._client_id)

#   Quando é feita uma publicação na Nuvem para a Nevoa
def on_message_nuvem(client,userdata,message,tmp=None):
    #print(dir(client))
    topico = message.topic
    msg = message.payload
    
    subtopicos = topico.split('/')
    print(subtopicos[1])
    #id_client = str(subtopicos[1])

    #determina a operacao
    if topico == "nuvem/media":
        # atualiza a média
        nova_media = float(msg) 
        media = nova_media
        print("Nova média:"+str(media))
        pass
    elif topico == "nuvem/limite":
        # atualiza valor maximo
        limite = float(msg) 
        limite_consumo = limite
        print("novo limite de consumo:"+str(limite_consumo))
        pass
    elif topico == "nuvem/bloquear":
        # nuvem publica idHidrometro-tipoBloqueio
        dados = str(msg)
        dados = dados.split('-')
        #if lista_clients_conectados.count(dados[0]) > 1:
        Publish(client,"nevoa/hidrometro/"+dados[0]+"/fechado",str(dados[1]))
       
    elif topico == "nuvem/solicitar_media":
        pass

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")
#-------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------
#   Métodos de inscrição de topicos para o cliente
def sub_to_getClients(client):
    client.subscribe("ID/#")
    return client

def sub_to_getValues(client):
    client.subscribe("hidrometro/#") # se inscreve no topico de publicações dos hidrometros
    return client

def sub_to_getValues_nuvem(client):
    client.subscribe("nuvem/#") # se inscreve no topico de publicações dos hidrometros
    return client
#-------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------
#   Métodos para criação dos clintes mqqt da Nevoa

#   Cria instância de cliente para observar ids dos hidrometros
def create_client_to_se_how_many(id_nevoa):
    client = mqtt.Client(client_id=str(id_nevoa))
    #client.username_pw_set()
    client.on_message = on_message_nevoa_to_getClients
    client.on_connect = on_connect
    client.on_publish = on_publish
    return client

# Cria instância de cliente para observar topico de plubicação de dados
def create_default_client(id_nevoa):
    client = mqtt.Client(client_id=str(id_nevoa))
    #client.username_pw_set()
    client.on_message = on_message_nevoa
    client.on_connect = on_connect
    client.on_publish = on_publish
    return client

def create_cliente_nuvem(id_nevoa):
    client = mqtt.Client(client_id=str(id_nevoa))
    #client.username_pw_set()
    client.on_message = on_message_nuvem
    client.on_connect = on_connect
    client.on_publish = on_publish
    return client
#-------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------
#   Métodos de Execução das funcionalidades

#   Executa a operação de receber dados publicados na névoa e inserir nas listas
def executar_Leitura(host_to_connect,port_to_connect):
    clientMQTT = nevoaCliente()
    try:
        Client_Connect(clientMQTT,host_to_connect,port_to_connect) #Conecta ao broker
    except Exception as err:
        print("Erro na conexão do hidrometro - " + err)
    print("Conexão finalzada!")
    clientMQTT = sub_to_getValues(clientMQTT)
    while True:
        time.sleep(3)

#   executa a publicação de dados
def executar_Publicacao(host_to_connect,port_to_connect):
   pass

#   Executa a Leitura e realiza operações solicitadas pela nuvem
def executar_Leitura_Nuvem(host_to_connect,port_to_connect):
    clientMQTT = create_cliente_nuvem(id)
    try:
        Client_Connect(clientMQTT,host_to_connect,port_to_connect) #Conecta ao broker
    except Exception as err:
        print("Erro na conexão do hidrometro - " + err)
    print("Conexão finalzada!")

    clientMQTT = sub_to_getValues_nuvem(clientMQTT)
    while True:
        time.sleep(3)

#   Executa o registro dos hidrometros clientes na nevoa
def executar_registro(host_to_connect,port_to_connect):
    clientMQTT = create_client_to_se_how_many(10)
    try:
        Client_Connect(clientMQTT,host_to_connect,port_to_connect) #Conecta ao broker
    except Exception as err:
        print("Erro na conexão do hidrometro - " + err)
    print("Conexão finalzada!")
    clientMQTT = sub_to_getClients(clientMQTT)

    while True:
        time.sleep(3)

def main():
    
    #print( int(clientMQTT._client_id))
    connect_host = input("Digite o IP em que devemos nos conectar: ")
    connect_port = int(input("Digite a Porta em que devemos nos conectar: "))

    os.system('cls' if os.name == 'nt' else 'clear')

    #----------------------------------------------------
    try:
        leitura = Thread(target=executar_Leitura , args=(connect_host,connect_port))
        leitura_nuvem = Thread(target=executar_Leitura_Nuvem,args=(connect_host,connect_port))
        registro_clientes = Thread(target= executar_registro, args=(connect_host,connect_port))
    except KeyboardInterrupt:
        print("Fechando os processos")   
    finally:
        leitura.start()
        leitura_nuvem.start()
        registro_clientes.start()
        print("Fechando o programa") 

if __name__ == '__main__':
    main()