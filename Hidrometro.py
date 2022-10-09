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
import paho.mqtt.publish as publish

class Hidrometro:
    
    def __init__(self,hidrante):   
        self.hidrante = hidrante
        self.clientMQTT = mqtt_client.Client(hidrante.id)
    
    def HidrometroClient(self,host_to_connect,port_to_connect,hidrometro_conectado): #Envia os dados para o servidor (Nuvem)
        while True: 
            print("Conexão iniciada")
            if(self.hidrante.fechado == False):
                self.hidrante.ContabilizarConsumo()
            else:
                print("Hidrometro fechado - consumo não contabilizado")

            try:
                mqtt_client.Client_Connect(self.clientMQTT,host_to_connect,port_to_connect)
            except Exception as err:
                print("Erro na conexão do hidrometro - " + err)
            print("Conexão finalzada!")
            
            #Pesca p/ topicos "mynevoaid/hidrometro/id_hidrometro/#"

            lista = hidrometro_conectado._getvalue()
            Json = json.loads(lista[0])
            msgs = [("nevoa_test/hidrometro/"+self.hidrante.id+"/consumo",Json["consumo"],0,False),
                    ("nevoa_test/hidrometro/"+self.hidrante.id+"/vazao",Json["vazao"],0,False),
                    ("nevoa_test/hidrometro/"+self.hidrante.id+"/vazamento",Json["vazamento"],0,False),
                    ("nevoa_test/hidrometro/"+self.hidrante.id+"/fechado",Json["fechado"],0,False),
                    ("nevoa_test/hidrometro/"+self.hidrante.id+"/vazamento_valor",Json["vazamento_valor"],0,False),
                    ("nevoa_test/hidrometro/"+self.hidrante.id+"/delay",Json["delay"],0,False)]

            publish.multiple()
            mqtt_client.Publish()


            self.hidrante.vazamento_valor = Json["vazamento_valor"]
            self.hidrante.consumo = Json["consumo"]
            self.hidrante.vazao = Json["vazao"]
            self.hidrante.vazamento = Json["vazamento"]
            self.hidrante.fechado = Json["fechado"]
            self.hidrante.delay = Json["delay"]

            print("Consumo Atual: %s | Vazão Atual: %s | Vazamento Atual: %s | Fechado: %s" % (str(self.hidrante.consumo),str(self.hidrante.vazao),str(self.hidrante.vazamento_valor),str(self.hidrante.fechado)))
            time.sleep(self.hidrante.delay)

def main():

    connect_host = input("Digite o IP em que devemos nos conectar: ")
    connect_port = int(input("Digite a Porta em que devemos nos conectar: "))

    os.system('cls' if os.name == 'nt' else 'clear')

    hidro = Hidrante.Hidrante(0,0,False,0.0,True,4)

    hidrometro = Hidrometro(hidro)

    print("O seu ID é: %s\n" % (str(hidro.id)))

    with Manager() as manager:
        try:
            hidrometro_conectado = manager.dict()
            hidrometro_conectado[0] = hidrometro.hidrante.getDadoJSON()
            server_process = Process(target=hidrometro.HidrometroClient, args=(connect_host,connect_port,hidrometro_conectado,))
            server_process.start()
        except KeyboardInterrupt:
            print("Fechando os processos")   
        finally:
            server_process.join()
            print("Fechando o programa")   


if __name__ == '__main__':
    main()