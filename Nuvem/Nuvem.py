import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import config_nuvem

# Lista das médias das nevoas conectadas
dados_nevoa = {'media_consumo':'0','total_hidrometros':'0'} # Oq cada nevoa retorna
media_nevoas_conectadas = { 'id':dados_nevoa }


#_______________________________________________________________________________________________________________

#_______________________________________________________________________________________________________________
#   Métodos relacionados ao registro dos dados publicados nos canais em que 
#   A nuvem é inscrita

# Quando uma nova conexão é feita com o brocker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


# Quando é feita uma publicação no topico em que a Nuvem esta inscrita 
# Define o topico e atualiza os dados no dicionario
def on_message_From_nevoa(client,userdata,message,tmp=None):
    id_client = client.id
    topico = message.topic
    msg = message.payload
    # salvar valor no client especifico
    dic = {id_client:msg}
    if topico == "":
        media_nevoas_conectadas['id'] = dic

# Inscreve nuvem no topico do brocker para receber Ids das nevoas
def sub_to_getNevoas(client):
    client.subscribe("Nevoas/#") # Nuvem se inscreve nos topicos das nevoas, recebendo todos os seus dados
    return client

# Cria instância de cliente para observar topico de plubicação de dados de média parcial e quantidade de hidrometros por nevoa
def create_default_client(id_nevoa):
    client = mqtt.Client(client_id=str(id_nevoa))
    client.on_message = on_message_From_nevoa
    return client

#_______________________________________________________________________________________________________________
#   Métodos relacionados a publicação de dados pela Nuvem

# Quando uma nova publicação é feita pela Nuvem no brocker
def on_publish_nuvem(client,userdata,mid):
    print(mid)

if __name__ == '__main__':
    #Nuvem tem um brocker
    #Nevoas devem enviar p/ o brocker da Nuvem
    clt = create_default_client(45)
    sub_to_getNevoas(clt)
