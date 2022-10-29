from cgi import print_form
import paho.mqtt.client as mqtt
from Hidrante import Hidrante
import paho.mqtt.publish as publish
import Hidrometro


def Client(id):
    client = mqtt.Client(client_id=str(id))
    #client.username_pw_set()
    client.on_message = Hidrometro.on_message
    client.on_connect = Hidrometro.on_connect
    client.on_publish = Hidrometro.on_publish
    return client

def Client_Connect(client,host,port):
    client.connect(host,port=port,keepalive=60)
    client.loop_start()

def Publish(client,topic,message):
    client.publish("IDENTIFIER/" + str(client._client_id),"1")
    return client.publish(topic,message)

def Subscribe(client,topic):
    client.subscribe(topic)
    return client
    
def Multiple(client_id,host,port,msg):
    publish.multiple(msg, hostname=host,port=port,client_id=client_id)
      

if __name__ == "__main__":
    cliente = Client(5)
    Client_Connect(cliente,"localhost",1883)
    Publish(cliente,"temperatura/test","teste")
    print("rodou")

