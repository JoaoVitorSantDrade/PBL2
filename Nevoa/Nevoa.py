from numpy import Infinity
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from random import seed
from threading import Thread
from random import randint
import time
import os
import json
import operator
from collections import defaultdict
from math import floor


#consumo vazao vazamento fechado vazamento_valor delay

class Nevoa:

    def __init__(self,brocker,brocker_port,nuvem,nuvem_port,delay):
        self.id = randint(0,1000)
        self.Client = self.create_default_client(self.id)
        self.Client_Nuvem = self.create_cliente_nuvem(self.id)
        self.brocker = brocker
        self.brocker_port = brocker_port
        self.nuvem = nuvem
        self.nuvem_port = nuvem_port
        self.lista_clientes = defaultdict(dict)
        self.lista_ordenada = defaultdict(dict)
        self.delay = delay
        self.limite_consumo = Infinity

    def Client_Connect(self,client,host,port):
        client.connect(host,port=port,keepalive=60)
        client.loop_start()

    def on_connect_nuvem(self,client, userdata, flags, rc):
        print("Conectamos com a Nuvem")

    def on_publish(self,client,userdata,mid):
        #print("publicado")
        pass

    def on_publish_nevoa(self,client,userdata,mid):
        pass

    def on_message_nevoa(self,client,userdata,message,tmp=None):
        topico = message.topic
        msg = message.payload
        subtopicos = topico.split('/')
        id_client = str(subtopicos[1])

        # salvar valor no client especifico
        if topico == "hidrometro/"+id_client+"/consumo":
            consumo = float(msg)
            self.lista_clientes[id_client].update({"consumo":consumo})

        elif topico == "hidrometro/"+id_client+"/vazao":
            vazao = float(msg)
            self.lista_clientes[id_client].update({"vazao":vazao})

        elif topico == "hidrometro/"+id_client+"/vazamento":
            vazamento = bool("True" in str(msg))
            self.lista_clientes[id_client].update({"vazamento":vazamento})

        elif topico == "hidrometro/"+id_client+"/fechado":
            fechado = int(msg)
            self.lista_clientes[id_client].update({"fechado":fechado})

        elif topico == "hidrometro/"+id_client+"/vazamento_valor":
            vazamento_valor = float(msg)
            self.lista_clientes[id_client].update({"vazamento_valor":vazamento_valor})

        elif topico == "hidrometro/"+id_client+"/delay":
            delay = int(msg)
            self.lista_clientes[id_client].update({"delay":delay})

    def on_message_nuvem(self,client,userdata,message,tmp=None):
        topico = message.topic
        msg = message.payload.decode("utf-8")
        id = int(client._client_id)
        subtopicos = topico.split('/')

        #print("\nTopico: " + topico +"\nID: " + str(id) + "\nMenssagem: " + msg )

        #Pesca -> nuvem/nevoa/#/hidrometro/#/opcao
        if "nuvem" in topico:
            hid_id = str(subtopicos[4])
            if "hidrometro" in topico:
                if "fechado" in topico:
                    self.lista_clientes[hid_id].update({"fechado":int(msg)}) #Atualiza no dicionario
                    self.Client.publish("hidrometro/"+ hid_id +"/fechado", int(msg)) #Envia uma mensagem para o outro brocker

                elif "delay" in topico:
                    self.lista_clientes[hid_id].update({"delay":floor(float(msg))}) #Atualiza no dicionario
                    self.Client.publish("hidrometro/"+ hid_id + "/delay", floor(float(msg)))

        #Pesca -> nevoa/#/opcao
        elif "nevoa" in topico:
            if "hidrometro" not in topico:
                if "limite" in topico:
                    # atualiza valor maximo
                    self.limite_consumo = floor(float(msg)) 
                    print("novo limite de consumo: " + msg)

                elif "delay" in topico:
                    self.delay = floor(float(msg))
                    print("novo delay para a nevoa: " + msg)

    def on_connect(self,client, userdata, flags, rc):
        print("Conectamos com a Nevoa")

    def create_default_client(self,id_nevoa):
        client = mqtt.Client(client_id=str(id_nevoa))
        client.on_message = self.on_message_nevoa
        client.on_connect = self.on_connect
        client.on_publish = self.on_publish
        return client

    def create_cliente_nuvem(self,id_nevoa):
        client = mqtt.Client(client_id=str(id_nevoa))
        client.on_message = self.on_message_nuvem
        client.on_connect = self.on_connect_nuvem
        client.on_publish = self.on_publish
        return client

    def executar_conexao_nuvem_brocker(self):
        try:
            print("Nevoa ID: " + str(self.id))
            self.Client_Connect(self.Client_Nuvem,self.nuvem,self.nuvem_port) #Conecta ao broker da nuvem

            self.Client_Nuvem.subscribe("nuvem/nevoa/"+ str(self.id) + "/#") # Recebe comandos para modificar coisas nos hidrometros
            self.Client_Nuvem.subscribe("nevoa/"+ str(self.id) + "/#") # Recebe comandos para modificar coisas na propria nevoa

            while True:
                media = 0
                i = 0
                for key, value in self.lista_clientes.items():
                    #consumo vazao vazamento fechado vazamento_valor delay
                    media += value["consumo"]
                    i = i + 1
                    try:
                        x_json = {
                            'ID':str(key),
                            'consumo':value['consumo'],
                            'vazao':value['vazao'],
                            'vazamento':value['vazamento'],
                            'vazamento_valor':value['vazamento_valor'],
                            'fechado':value['fechado'],
                            'delay':value['delay']
                        }
                    except Exception:
                        print("Ainda não foram recebidos todos os dados do hidrometro")

                    #x_string = json.dumps(x_json)
                    #x_json = json.loads(x_string)
                    
                    #Envia dados do hidrometro para nuvem
                    self.Client_Nuvem.publish("nevoa/"+ str(self.id) + "/hidrometro/"+ x_json["ID"] +"/consumo", x_json["consumo"],qos=1)
                    self.Client_Nuvem.publish("nevoa/"+ str(self.id) + "/hidrometro/"+ x_json["ID"] +"/vazao", x_json["vazao"],qos=1)
                    self.Client_Nuvem.publish("nevoa/"+ str(self.id) + "/hidrometro/"+ x_json["ID"] +"/vazamento", x_json["vazamento"],qos=1)
                    self.Client_Nuvem.publish("nevoa/"+ str(self.id) + "/hidrometro/"+ x_json["ID"] +"/fechado", x_json["fechado"],qos=1)
                    self.Client_Nuvem.publish("nevoa/"+ str(self.id) + "/hidrometro/"+ x_json["ID"] +"/vazamento_valor", x_json["vazamento_valor"],qos=1)
                    self.Client_Nuvem.publish("nevoa/"+ str(self.id) + "/hidrometro/"+ x_json["ID"] +"/delay", x_json["delay"],qos=1)

                if i > 0:
                    media = media/i
                    self.Client_Nuvem.publish("nevoa/" + str(self.id) + "/media", media)

                time.sleep(self.delay)

        except Exception as err:
            print("Erro na conexão da Nevoa com a Nuvem - " + str(err))         

    def executar_conexao_nevoa_brocker(self):
        try:
            self.Client_Connect(self.Client,self.brocker,self.brocker_port) #Conecta ao broker da nevoa
            self.Client.subscribe("hidrometro/#") #Escuta todos os hidrometros conectados a essa nevoa
        except Exception as err:
            print("Erro na conexão da Nevoa com o Brocker - " + str(err))
            
    def sort_clients_by_consumo(self):
        while True:
            d = {}
            for key, value in self.lista_clientes.items():
                d[key] = int(value['consumo'])

            try:
                self.lista_ordenada = sorted(d.items(),key= operator.itemgetter(1))
            except Exception:
                pass
            finally:
                time.sleep(5)
    
def main():
    
    connect_host = input("Digite o IP do Brocker: ")
    connect_port = int(input("Digite a Porta do Brocker: "))
    nuvem_host = input("Digite o IP da Nuvem: ")
    nuvem_port = int(input("Digite a Porta da Nuvem: "))

    nevoa = Nevoa(connect_host,connect_port,nuvem_host,nuvem_port,2)

    os.system('cls' if os.name == 'nt' else 'clear')

    #----------------------------------------------------
    try:
        conectar_na_nuvem = Thread(target=nevoa.executar_conexao_nuvem_brocker)
        conectar_no_brocker = Thread(target=nevoa.executar_conexao_nevoa_brocker)
        ordenar_lista = Thread(target=nevoa.sort_clients_by_consumo)
    except KeyboardInterrupt:
        print("Fechando os processos")   
    finally:
        ordenar_lista.start()
        conectar_no_brocker.start()
        conectar_na_nuvem.start()

if __name__ == '__main__':
    main()