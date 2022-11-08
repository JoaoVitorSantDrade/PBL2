from shutil import ExecError
from threading import local
from threading import Thread
import Hidrante as Hidrante
from threading import Thread
import time
import os
from time import localtime, strftime
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

class Hidrometro:
    
    def __init__(self,hidrante):  

        self.hidrante = hidrante 

        #cria cliente mqqt para conexao ao broker
        cliente = mqtt.Client(client_id=str(hidrante.id)) 

        cliente.on_connect = self.on_connect
        cliente.on_message = self.on_message
        cliente.on_publish = self.on_publish

        self.clientMQTT = cliente
        
    # método que executa a publicação de dados
    def HidrometroClient(self,host_to_connect,port_to_connect): #Envia os dados para o servidor (Nuvem)
        
        try:
            self.clientMQTT.connect(host=host_to_connect,port=port_to_connect) #Conecta ao broker
            self.clientMQTT.loop_start()
        except Exception as err:
            print("Erro na conexão do hidrometro - " + err)
        print("Conexão finalzada!")

        hid_id = str(self.hidrante.id)

        self.clientMQTT.publish("hidrometro/"+ hid_id + "/delay",str(self.hidrante.delay), 1)
        self.clientMQTT.publish("hidrometro/"+ hid_id + "/fechado",str(self.hidrante.fechado), 1)
        self.clientMQTT.publish("hidrometro/"+ hid_id + "/tendencia", str(self.hidrante.tendencia), 1)

        self.clientMQTT.subscribe("hidrometro/"+ hid_id +"/fechado", 1)
        self.clientMQTT.subscribe("hidrometro/"+ hid_id +"/delay", 1)
        self.clientMQTT.subscribe("hidrometro/"+ hid_id + "/tendencia", 1)

        while True: 
            print("Conexão iniciada")
            if(self.hidrante.fechado == 0):
                self.hidrante.ContabilizarConsumo()
            else:
                print("Hidrometro fechado - consumo não contabilizado")
            #Pesca p/ topicos "hidrometro/id_hidrometro/#"

            self.clientMQTT.publish("hidrometro/"+ hid_id + "/vazao",str(self.hidrante.vazao))
            self.clientMQTT.publish("hidrometro/"+ hid_id + "/consumo",str(self.hidrante.consumo))
            self.clientMQTT.publish("hidrometro/"+ hid_id + "/vazamento",str(self.hidrante.vazamento))
            self.clientMQTT.publish("hidrometro/"+ hid_id + "/vazamento_valor",str(self.hidrante.vazamento_valor))

            print("Consumo Atual: %s | Vazão Atual: %s | Vazamento Atual: %s | Fechado: %s" % (str(self.hidrante.consumo),str(self.hidrante.vazao),str(self.hidrante.vazamento_valor),str(self.hidrante.fechado)))
            time.sleep(self.hidrante.delay)

    def on_message(self,client, userdata, message,tmp=None):
        topico = message.topic
        msg = message.payload

        if topico == "hidrometro/"+ str(self.hidrante.id) +"/fechado":
            self.hidrante.fechado = int(msg)
            print("Mensagem recebida no topico 'fechado'")

        elif topico == "hidrometro/"+ str(self.hidrante.id) + "/delay":
            self.hidrante.delay = int(msg)
            print("Mensagem recebida no topico 'delay'")

        elif topico == "hidrometro/"+ str(self.hidrante.id) + "/tendencia":
            self.hidrante.tendencia = int(msg)
            print("Mensagem recebida no topico 'tendencia'")


    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

    def on_publish(self,client,userdata,mid):
        #print(userdata)
        pass
        
def main():

    connect_host = input("Digite o IP da Nevoa: ")
    connect_port = int(input("Digite a Porta da Nevoa: "))

    os.system('cls' if os.name == 'nt' else 'clear')

    hidro = Hidrante.Hidrante(0,False,0,0,1,3)

    hidrometro = Hidrometro(hidro) #ip do broker, porta do brocker

    print("O seu ID é: %s\n" % (str(hidro.id)))

    try:
        hid_client = Thread(target=hidrometro.HidrometroClient, args=(connect_host,connect_port))
    except KeyboardInterrupt:
        print("Fechando os processos")   
    finally:
        hid_client.start()
        hid_client.join()
        print("Fechando o programa")   


if __name__ == '__main__':
    main()