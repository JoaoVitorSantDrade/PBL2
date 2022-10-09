import paho.mqtt.client as mqtt
import mycallbacks

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

if __name__ == "__main__":
    cliente = Client()
    Client_Connect(cliente,"localhost",1883)
    Publish(cliente,"$SYS/","teste")
    print("rodou")