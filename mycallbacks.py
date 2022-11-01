def on_message(client, userdata, message,tmp=None):
    #print(" Received message " + str(message.payload)+ " on topic '" + message.topic+ "' with QoS " + str(message.qos))
    id_client = client.id
    topico = message.topic
    msg = message.payload
    
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")

def on_publish(client,userdata,mid):
    #print(mid)
    print("publicado")
