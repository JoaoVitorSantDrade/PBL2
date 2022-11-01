import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from random import seed
from threading import Thread
from random import randint
import time
import os
import json
import operator

#consumo vazao vazamento fechado vazamento_valor delay
#   Valores fixos para bloqueio dos Hidrometros

class Nevoa:

    def __init__(self,brocker,brocker_port,nuvem,nuvem_port,delay):
        self.id = randint(0,1000)
        self.Client = self.create_default_client(self.id)
        self.Client_Nuvem = self.create_cliente_nuvem(self.id)
        self.brocker = brocker
        self.brocker_port = brocker_port
        self.nuvem = nuvem
        self.nuvem_port = nuvem_port
        self.lista_clientes = {}
        self.delay = delay

    def Client_Connect(self,client,host,port):
        client.connect(host,port=port,keepalive=60)
        client.loop_start()

    def on_connect_nuvem(self,client, userdata, flags, rc):
        print("Conectamos com a Nuvem")

    def on_publish(self,client,userdata,mid):
        print("publicado")

    def on_publish_nevoa(self,client,userdata,mid):
        print(mid)

    def on_message_nevoa(self,client,userdata,message,tmp=None):
        topico = message.topic
        msg = message.payload
        print(topico)
        subtopicos = topico.split('/')
        print(subtopicos[1])
        id_client = str(subtopicos[1])

        # salvar valor no client especifico
        if topico == "hidrometro/"+id_client+"/consumo":
            consumo = float(msg)
            self.lista_clientes[id_client].append({"consumo":consumo})

        elif topico == "hidrometro/"+id_client+"/vazao":
            vazao = float(msg)
            self.lista_clientes[id_client].append({"vazao":vazao})

        elif topico == "hidrometro/"+id_client+"/vazamento":
            vazamento = float(msg)
            self.lista_clientes[id_client].append({"vazamento":vazamento})

        elif topico == "hidrometro/"+id_client+"/fechado":
            fechado = int(msg)
            self.lista_clientes[id_client].append({"fechado":fechado})

        elif topico == "hidrometro/"+id_client+"/vazamento_valor":
            vazamento_valor = float(msg)
            self.lista_clientes[id_client].append({"vazamento_valor":vazamento_valor})

        elif topico == "hidrometro/"+id_client+"/delay":
            delay = float(msg)
            self.lista_clientes[id_client].append({"delay":delay})

    def on_message_nuvem(self,client,userdata,message,tmp=None):
        topico = message.topic
        msg = message.payload
        
        print(topico)
        subtopicos = topico.split('/')
        print(subtopicos[1])
        #id_client = str(subtopicos[1])

        #determina a operacao
        if topico == "nuvem/media":
            # atualiza a média
            nova_media = float(msg) 
            media = nova_media
            print("Nova média:"+str(media))
            pass
        elif topico == "nuvem/limite":
            # atualiza valor maximo
            limite = float(msg) 
            limite_consumo = limite
            print("novo limite de consumo:"+str(limite_consumo))
            pass
        elif topico == "nuvem/bloquear":
            # nuvem publica idHidrometro-tipoBloqueio
            dados = str(msg)
            dados = dados.split('-')
            #if lista_clients_conectados.count(dados[0]) > 1:
            
            #Publish(client,"nevoa/hidrometro/"+dados[0]+"/fechado",str(dados[1]))
        
        elif topico == "nuvem/solicitar_media":
            pass

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

    def sub_to_getValues(self,client):
        client.subscribe("hidrometro/#") # se inscreve no topico de publicações dos hidrometros
        return client

    def sub_to_getValues_nuvem(self,client):
        client.subscribe("nuvem/#") # se inscreve no topico de publicações dos hidrometros
        return client

    def create_default_client(self,id_nevoa):
        client = mqtt.Client(client_id=str(id_nevoa))
        client.on_message = self.on_message_nevoa
        client.on_connect = self.on_connect
        client.on_publish = self.on_publish
        return client

    def create_cliente_nuvem(self,id_nevoa):
        client = mqtt.Client(client_id=str(id_nevoa))
        client.on_message = self.on_message_nuvem
        client.on_connect = self.on_connect
        client.on_publish = self.on_publish
        return client

    def executar_conexao_nuvem_brocker(self):
        try:
            self.Client_Connect(self.Client_Nuvem,self.nuvem,self.nuvem_port) #Conecta ao broker da nuvem

            self.Client_Nuvem.subscribe("nevoa/"+ str(self.id) + "/hidrometro/#") # Recebe comandos para modificar coisas nos hidrometros

            while True:
                for key, value in self.lista_clientes:
                    #consumo vazao vazamento fechado vazamento_valor delay
                    x_json = {
                        "ID": key,
                        "consumo":value["consumo"],
                        "vazao":value["vazao"],
                        "vazamento":value["vazamento"],
                        "fechado":value["fechado"],
                        "vazamento_valor":value["vazamento_valor"],
                        "delay":value["delay"]
                    }

                    x_string = json.dumps(x_json)
                    x_json = json.loads(x_string)

                    #Envia dados do hidrometro para nuvem
                    self.Client_Nuvem.publish("nevoa/"+ str(self.id) + "/hidrometro/"+ x_json["ID"] +"/consumo/"+ x_json["consumo"])
                    self.Client_Nuvem.publish("nevoa/"+ str(self.id) + "/hidrometro/"+ x_json["ID"] +"/vazao/"+ x_json["vazao"])
                    self.Client_Nuvem.publish("nevoa/"+ str(self.id) + "/hidrometro/"+ x_json["ID"] +"/vazamento/"+ x_json["vazamento"])
                    self.Client_Nuvem.publish("nevoa/"+ str(self.id) + "/hidrometro/"+ x_json["ID"] +"/fechado/"+ x_json["fechado"])
                    self.Client_Nuvem.publish("nevoa/"+ str(self.id) + "/hidrometro/"+ x_json["ID"] +"/vazamento_valor/"+ x_json["vazamento_valor"])
                    self.Client_Nuvem.publish("nevoa/"+ str(self.id) + "/hidrometro/"+ x_json["ID"] +"/delay/"+ x_json["delay"])

                time.sleep(self.delay)

        except Exception as err:
            print("Erro na conexão da Nevoa com a Nuvem - " + str(err))         

    def executar_conexao_nevoa_brocker(self):
        try:
            self.Client_Connect(self.Client,self.brocker,self.brocker_port) #Conecta ao broker da nevoa
            self.Client.subscribe("hidrometro/#")
        except Exception as err:
            print("Erro na conexão da Nevoa com a Nuvem - " + str(err))
            
    def sort_clients_by_consumo(self):
        d = {}
        for key, value in self.lista_clientes:
            d[key] = int(value['consumo'])

        a = sorted(d.items(),key= operator.itemgetter(1))
        return a
    
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
    except KeyboardInterrupt:
        print("Fechando os processos")   
    finally:
        conectar_no_brocker.start()
        conectar_na_nuvem.start()

if __name__ == '__main__':
    main()