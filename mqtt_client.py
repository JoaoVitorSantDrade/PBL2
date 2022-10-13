import paho.mqtt.client as mqtt
import mycallbacks
import paho.mqtt.publish as publish

def Client(id):
    client = mqtt.Client(client_id=str(id))
    #client.username_pw_set()
    client.on_message = mycallbacks.on_message
    client.on_connect = mycallbacks.on_connect
    client.on_publish = mycallbacks.on_publish
    return client

def Client_Connect(client,broker,port):
    client.connect(broker,port=port,keepalive=60)
    client.loop_start()

def Publish(client,topic,message):
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