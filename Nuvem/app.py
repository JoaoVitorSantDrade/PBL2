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
import json

# Lista das médias das nevoas conectadas

list_of_consumo = defaultdict(dict)
lista_ordenada = defaultdict(dict)

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
        # nuvem/nevoa/#/hidrometro/#/opcao
        # nevoa/#/media
        if "nevoa" in topico:
            nevoa_id = topico[1]
            if "media" in topico:
                pass
            elif "hidrometro" in topico:
                if "consumo" in topico:
                    hidrometro = topico[3]
                    identifier = nevoa_id + "-" + hidrometro
                    list_of_consumo[identifier].update({"consumo":float(msg)})
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
            
            self.cliente_nuvem_brocker.subscribe("nevoa/+/hidrometro/#")
            pass
        except Exception:
            pass

def sort_clients_by_consumo():
    while True:
        d = {}
        for key, value in list_of_consumo.items():
            d[key] = int(value['consumo'])
        try:
            lista = sorted(d.items(),key= operator.itemgetter(1), reverse=True)
            for key, value in lista:
                lista_ordenada[str(key)].update({"consumo":str(value)})
        except Exception as ext:
            print(ext)
        finally:
            time.sleep(2)

app = Flask(__name__)
@app.route('/top', methods=['GET'])
def top():

    args = request.args
    args = args.to_dict()

    f=codecs.open("Nuvem/form.html", 'r', 'utf-8')
    html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    
    container_tag = soup.find("div", class_="container")

    if "top-consumo" in args:
        if args["top-consumo"] != "":
            consumo = int(args['top-consumo'])
            i = 0
            for key, value in lista_ordenada.items():
                if i < consumo:
                    p_tag = soup.new_tag('p')
                    p_tag.string = str(i + 1) + "º -> " + key + " - " + str(value["consumo"]) + " m³/s"

                    div_tag = soup.new_tag('div')
                    div_tag['class'] = "show"
                    div_tag.insert(0,p_tag)

                    container_tag.insert_before(div_tag)
                    i = i + 1
            return soup.prettify()
    return "Not Found"

@app.route('/api/top', methods=['GET'])
def api_top():

    args = request.args
    args = args.to_dict()

    if "top-consumo" in args:
        if args["top-consumo"] != "":
            consumo = int(args['top-consumo'])
            i = 0
            js = defaultdict(dict)
            for key, value in lista_ordenada.items():
                if i < consumo:
                    x = {
                        "ID": key,
                        "consumo": value["consumo"],
                    }
                    js[str(i)].update(x)
                    i = i + 1
            return js
    return "Not Found"
    
@app.route('/api/hidrometro', methods=['GET'])
def api_hid_only():

    args = request.args
    args = args.to_dict()
    if "hidrometro" in args:
        if args["hidrometro"] != "":
            hidrometro = str(args['hidrometro'])
            js = defaultdict(dict)
            for key, value in lista_ordenada.items():
                if hidrometro in key:
                    x = {
                        "ID": key,
                    }
                    js.update(x)
                    return js

    return "Not Found"   

if __name__ == '__main__':

    # run app in debug mode on port 5000
    host = input("Digite o IP da Nuvem: ")
    host_port = int(input("Digite a Porta da Nuvem: "))
    nuvem = Nuvem(host,host_port)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    try:
        conectar_no_brocker = Thread(target=nuvem.connect_to_brocker)
        organizar_info = Thread(target=sort_clients_by_consumo)
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
