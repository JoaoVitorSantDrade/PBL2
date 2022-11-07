from flask import Flask, request
import paho.mqtt.client as mqtt
from random import randint
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import config_nuvem
from collections import defaultdict
import os
import operator
import time
from threading import Thread
import codecs
from bs4 import BeautifulSoup

# Lista das médias das nevoas conectadas

list_of_nevoa = defaultdict(dict)
list_of_consumo = defaultdict(dict)

class Nuvem:

    def __init__(self,host,port):
        self.id = randint(1,10)
        self.host = host
        self.port = port
        self.cliente_nuvem_brocker = self.create_default_client(self.id)

    # Quando uma nova conexão é feita com o brocker
    def on_connect(self,client, userdata, flags, rc):
        print("Conectamos no brocker da nuvem")

    def on_message_From_nevoa(self,client,userdata,message,tmp=None):
        #id_client = client._client_id
        topico = str(message.topic)
        msg = message.payload.decode("utf-8")
        topico = topico.split('/')
        print(topico)
        # nuvem/nevoa/#/hidrometro/#/opcao
        # nevoa/#/media
        if "nevoa" in topico:
            nevoa_id = topico[1]
            list_of_nevoa[nevoa_id] = nevoa_id
            if "media" in topico:
                pass
            elif "hidrometro" in topico:
                if "consumo" in topico:
                    hidrometro = topico[3]
                    identifier = nevoa_id + "-" + hidrometro
                    list_of_consumo[nevoa_id].update({"identificador":identifier,"consumo":float(msg)})
                    print(list_of_consumo.items())
                    #pesca -> nevoa/"+ str(self.id) + "/hidrometro/"+ str(i) +"/consumo/" + str(key)
                    pass

    def Client_Connect(self,client,host,port):
            client.connect(host,port=port,keepalive=60)
            client.loop_start()

    def create_default_client(self,id):
        client = mqtt.Client(client_id=str(id))
        client.on_message = self.on_message_From_nevoa
        return client

    def connect_to_brocker(self):
        try:
            self.Client_Connect(self.cliente_nuvem_brocker,self.host,self.port) #Conecta ao broker da nuvem
            #self.cliente_nuvem_brocker.subscribe("nevoa/#")
            self.cliente_nuvem_brocker.subscribe("nevoa/+/hidrometro/+/consumo/#")
            pass
        except Exception:
            pass

    def sort_clients_by_consumo(self):
        while True:
            d = {}
            for key, value in list_of_consumo.items():
                d[key] = int(value['consumo'])
            try:
                self.lista_ordenada = sorted(d.items(),key= operator.itemgetter(1))
            except Exception:
                pass
            finally:
                time.sleep(2)

def main():
    # run app in debug mode on port 5000
    host = input("Digite o IP do brocker: ")
    host_port = int(input("Digite a Porta do brocker: "))
    nuvem = Nuvem(host,host_port)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    try:
        conectar_no_brocker = Thread(target=nuvem.connect_to_brocker)
        organizar_info = Thread(target=nuvem.sort_clients_by_consumo)
        organizar_info.start()
        conectar_no_brocker.start()

    except KeyboardInterrupt:
        print("Fechando os processos")   
    finally:
        organizar_info.join()
        conectar_no_brocker.join()


app = Flask(__name__)
@app.route('/', methods=['GET'])
def see_hidrometro():
    args = request.args
    args = args.to_dict()
    f=codecs.open("Nuvem/form.html", 'r', 'utf-8')
    html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    soup.find_all("div", class_="container")
    print(list_of_consumo.items())
    return html



if __name__ == '__main__':

    # run app in debug mode on port 5000
    host = input("Digite o IP do brocker: ")
    host_port = int(input("Digite a Porta do brocker: "))
    nuvem = Nuvem(host,host_port)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    try:
        conectar_no_brocker = Thread(target=nuvem.connect_to_brocker)
        organizar_info = Thread(target=nuvem.sort_clients_by_consumo)
        api = Thread(target=app.run)
        organizar_info.start()
        conectar_no_brocker.start()
        api.start()

    except KeyboardInterrupt:
        print("Fechando os processos")   
    finally:
        organizar_info.join()
        conectar_no_brocker.join()
        api.join()
