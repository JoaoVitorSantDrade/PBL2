from shutil import ExecError
from threading import local
import Hidrante
import mqtt_client
import Config
from multiprocessing import Process, Manager
import time
import os
import json
from time import localtime, strftime

class Hidrometro:
    
    def __init__(self,hidrante,host,port):   
        self.hidrante = hidrante
        self.clientMQTT = mqtt_client.Client(hidrante.id)

    def HidrometroServerMQTT():
        pass
    
    def HidrometroClient(self,host_to_connect,port_to_connect): #Envia os dados para o servidor (Nuvem)
        while True: 
            print("Conexão iniciada")
            if(self.hidrante.fechado == False):
                self.hidrante.ContabilizarConsumo()
            else:
                print("Hidrometro fechado - consumo não contabilizado")

            try:
                mqtt_client.Client_Connect(self.clientMQTT,host_to_connect,port_to_connect) #Conecta ao broker
            except Exception as err:
                print("Erro na conexão do hidrometro - " + err)
            print("Conexão finalzada!")
            
            #Pesca p/ topicos "mynevoaid/hidrometro/id_hidrometro/#"
            hid_id = str(self.hidrante.id)
            #pega os dados e envia p/ broker
            msgs = [("nevoa_test/hidrometro/"+hid_id+"/consumo",str(self.hidrante.consumo),0,False),
                    ("nevoa_test/hidrometro/"+hid_id+"/vazao",str(self.hidrante.vazao),0,False),
                    ("nevoa_test/hidrometro/"+hid_id+"/vazamento",str(self.hidrante.vazamento),0,False),
                    ("nevoa_test/hidrometro/"+hid_id+"/fechado",str(self.hidrante.fechado),0,False),
                    ("nevoa_test/hidrometro/"+hid_id+"/vazamento_valor",str(self.hidrante.vazamento_valor),0,False),
                    ("nevoa_test/hidrometro/"+hid_id+"/delay",str(self.hidrante.delay),0,False)]

            mqtt_client.Multiple(self.hidrante.id,host_to_connect,port_to_connect,msgs)

            print("Consumo Atual: %s | Vazão Atual: %s | Vazamento Atual: %s | Fechado: %s" % (str(self.hidrante.consumo),str(self.hidrante.vazao),str(self.hidrante.vazamento_valor),str(self.hidrante.fechado)))
            time.sleep(self.hidrante.delay)

def main():

    connect_host = input("Digite o IP em que devemos nos conectar: ")
    connect_port = int(input("Digite a Porta em que devemos nos conectar: "))

    os.system('cls' if os.name == 'nt' else 'clear')

    hidro = Hidrante.Hidrante(0,0,False,0.0,True,4)

    hidrometro = Hidrometro(hidro)

    print("O seu ID é: %s\n" % (str(hidro.id)))

    hidrometro.clientMQTT.subscribe("nevoa_test/hidrometro/"+str(hidrometro.hidrante.id)+"/consumo")
    hidrometro.clientMQTT.subscribe("nevoa_test/hidrometro/"+str(hidrometro.hidrante.id)+"/vazao")
    hidrometro.clientMQTT.subscribe("nevoa_test/hidrometro/"+str(hidrometro.hidrante.id)+"/vazamento")
    hidrometro.clientMQTT.subscribe("nevoa_test/hidrometro/"+str(hidrometro.hidrante.id)+"/fechado")
    hidrometro.clientMQTT.subscribe("nevoa_test/hidrometro/"+str(hidrometro.hidrante.id)+"/vazamento_valor")
    hidrometro.clientMQTT.subscribe("nevoa_test/hidrometro/"+str(hidrometro.hidrante.id)+"/delay")

    try:
        server_process = Process(target=hidrometro.HidrometroClient, args=(connect_host,connect_port,))
        server_process.start()
    except KeyboardInterrupt:
        print("Fechando os processos")   
    finally:
        server_process.join()
        print("Fechando o programa")   


if __name__ == '__main__':
    main()