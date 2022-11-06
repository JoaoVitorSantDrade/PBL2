from flask import Flask, request
import paho.mqtt.client as mqtt
from random import randint
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import config_nuvem
from collections import defaultdict

# Lista das médias das nevoas conectadas

class Nuvem:

    def __init__(self,host,port):
        self.id = randint(1,10)
        self.host = host
        self.port = port
        self.cliente_nuvem_brocker = self.create_default_client(self.id)
        self.list_of_nevoa = defaultdict(dict)

    # Quando uma nova conexão é feita com o brocker
    def on_connect(self,client, userdata, flags, rc):
        print("Conectamos no brocker da nuvem")

    def on_message_From_nevoa(self,client,userdata,message,tmp=None):
        #id_client = client._client_id
        topico = str(message.topic)
        msg = message.payload.decode("utf-8")
        topico = topico.split('/')
        # nuvem/nevoa/#/hidrometro/#/opcao
        # nevoa/#/media
        if "nevoa" in topico:
            nevoa_id = topico[1]
            self.list_of_nevoa[nevoa_id] = nevoa_id
            if "media" in topico:
                pass

    def Client_Connect(self,client,host,port):
            client.connect(host,port=port,keepalive=60)
            client.loop_start()

    def create_default_client(self,id):
        client = mqtt.Client(client_id=str(id))
        client.on_message = self.on_message_From_nevoa
        return client

    def connect_to_brocker(self,brocker,port):
        try:
            self.Client_Connect(self.cliente_nuvem_brocker,self.host,self.port) #Conecta ao broker da nuvem
            self.cliente_nuvem_brocker.subscribe("nevoa/#")
            pass
        except Exception:
            pass

app = Flask(__name__)
@app.route('/api/hidrometro/top', methods=['GET'])
def see_hidrometro():
    args = request.args
    args = args.to_dict()
    #pedir para a nuvem que pesquise tal ID do hidrometro
    
    num_to_see = args.get("total")
    try:
        cliente = None #Terminar
    except Exception:
        pass



if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)
    host = input("Digite o IP do brocker: ")
    host_port = int(input("Digite a Porta do brocker: "))
    nuvem = Nuvem(host,host_port)
