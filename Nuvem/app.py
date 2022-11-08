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
from math import floor

# Lista das médias das nevoas conectadas

list_of_consumo = defaultdict(dict)
lista_ordenada = defaultdict(dict)
lista_nevoa = defaultdict(dict)


fila_de_comandos = defaultdict(dict)
pos_fila = 0

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
                lista_nevoa[nevoa_id].update({"media":float(msg)})

            elif "hidrometro" in topico:
                if "consumo" in topico:
                    hidrometro = topico[3]
                    identifier = nevoa_id + "-" + hidrometro
                    list_of_consumo[identifier].update({"consumo":float(msg)})
                    #pesca -> nevoa/"+ str(self.id) + "/hidrometro/"+ str(i) +"/consumo/" + str(key)

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
            self.cliente_nuvem_brocker.subscribe("nevoa/+/media")
            pass
        except Exception:
            pass

    def execute_comand_queue(self):
        while True:
            try:
                for key,value in fila_de_comandos.items():
                    global pos_fila
                    #executar o comando e retira da fila 
                    if "bloqueio" in value:
                        comando = value["bloqueio"]
                        pub = self.cliente_nuvem_brocker
                        pub.publish("nuvem/nevoa/"+ str(value["ID"]) +"/hidrometro/" + str(value["ID_hid"]) +"/fechado",comando, qos=1)

                    elif "delay" in value:
                        comando = value["delay"]
                        pub = self.cliente_nuvem_brocker
                        try:
                            pub.publish("nuvem/nevoa/"+ str(value["ID"]) +"/hidrometro/" + str(value["ID_hid"]) +"/delay",comando, qos=1)
                        except Exception as excp:
                            pub.publish("nevoa/"+ str(value["ID"]) + "/delay",comando, qos=1)

                    elif "tendencia" in value:
                        comando = value["tendencia"]
                        pub = self.cliente_nuvem_brocker
                        pub.publish("nuvem/nevoa/"+ str(value["ID"]) +"/hidrometro/" + str(value["ID_hid"]) +"/tendencia",comando, qos=1)
                     
                    elif "limite" in value:
                        comando = value["limite"]
                        pub = self.cliente_nuvem_brocker
                        pub.publish("nevoa/"+ str(value["ID"]) + "/limite",comando, qos=1)   

                for it in list(fila_de_comandos):
                    fila_de_comandos.pop(it)
                    pos_fila = pos_fila - 1


            except Exception as exp:
                print(exp)
            
            time.sleep(2)

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


@app.route('/api/media', methods=['GET'])
def api_media():

    i = 1
    x = 0
    for key, value in lista_nevoa.items():
        x = x + float(value["media"])
        i + 1
    try:
        x = (floor(x))/i
        return {"media":x,"qtd_nevoa":i}
    except Exception as exp:
        print(exp)
        return "Não existe nevoas conectadas"



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
def api_hid():
    args = request.args
    args = args.to_dict()
    if "hidrometro" in args:
        if args["hidrometro"] != "":
            hidrometro = str(args['hidrometro'])
            js = defaultdict(dict)
            for key, value in list_of_consumo.items():
                key = key.split("-")
                if hidrometro == key[1]:
                    x = {
                        "ID": key,
                    }
                    js.update(x)
                    return js

    elif "bloqueio" in args:
        if args["bloqueio"] != "":
            bloqueio = int(args["bloqueio"])
            try:
                if "id" in args:
                    id = int(args['id'])
                    id_hid = int(args['id_hid'])
                    global pos_fila
                    fila_de_comandos[pos_fila].update({"ID":id,"ID_hid":id_hid,"bloqueio":bloqueio})
                    pos_fila = pos_fila + 1
                    print(fila_de_comandos)
                    return "Comando colocado na fila com sucesso"
            except Exception:
                    return "Não foi possivel colocar o comando na fila"
    elif "tendencia" in args:
            if args["tendencia"] != "":
                tendencia = int(args["tendencia"])
                try:
                    if "id" in args:
                        id = int(args['id'])
                        id_hid = int(args['id_hid'])
                        fila_de_comandos[pos_fila].update({"ID":id,"ID_hid":id_hid,"tendencia":tendencia})
                        pos_fila = pos_fila + 1
                        print(fila_de_comandos)
                        return "Comando colocado na fila com sucesso"
                except Exception:
                        return "Não foi possivel colocar o comando na fila"
    elif "delay" in args:
            if args["delay"] != "":
                delay = int(args["delay"])
                try:
                    if "id" in args:
                        id = int(args['id'])
                        id_hid = int(args['id_hid'])
                        fila_de_comandos[pos_fila].update({"ID":id,"ID_hid":id_hid,"delay":delay})
                        pos_fila = pos_fila + 1
                        print(fila_de_comandos)
                        return "Comando colocado na fila com sucesso"
                except Exception:
                        return "Não foi possivel colocar o comando na fila"
    else:
        js = defaultdict(dict)
        i = 0
        try:
            for key in list_of_consumo.items():
                x = {
                    "ID": key,
                } 
                js[str(i)].update(x)
                i = i + 1
            return js
        except Exception:
            return "Error in Database"
    
    return "Not Found" 

@app.route('/api/nevoa', methods=['GET'])
def api_nevoa():

    args = request.args
    args = args.to_dict()

    if "limite" in args:
        if args["limite"] != "":
            limite = int(args["limite"])
            try:
                if "id" in args:
                    global pos_fila
                    id = int(args["id"])
                    fila_de_comandos[pos_fila].update({"ID":id,"limite":limite})
                    pos_fila = pos_fila + 1
                    print(fila_de_comandos)
                    return "Comando colocado na fila com sucesso"
            except Exception:
                return "Não foi possivel colocar o comando na fila"

    elif "delay" in args:
        if args["delay"] != "":
            delay = int(args["delay"])
            try:
                if "id" in args:
                    id = int(args['id'])
                    fila_de_comandos[pos_fila].update({"ID":id,"delay":delay})
                    pos_fila = pos_fila + 1
                    print(fila_de_comandos)
                    return "Comando colocado na fila com sucesso"
            except Exception:
                    return "Não foi possivel colocar o comando na fila"
    else:
        js = defaultdict(dict)
        i = 0
        try:
            for key in lista_nevoa.items():
                x = {
                    "ID": key,
                } 
                js[str(i)].update(x)
                i = i + 1
            return js
        except Exception:
            return "Error in Database"

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
        executar_fila = Thread(target=nuvem.execute_comand_queue)
        api = Thread(target=app.run)
        organizar_info.start()
        conectar_no_brocker.start()
        executar_fila.start()
        api.start()

    except KeyboardInterrupt:
        print("Fechando os processos")   
    finally:
        organizar_info.join()
        conectar_no_brocker.join()
        executar_fila.join()
        api.join()