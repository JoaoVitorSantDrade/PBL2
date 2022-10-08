import json
import Config
from multiprocessing import Process
from random import seed
from random import randint
import time

class Hidrante:
    
    def __init__(self,consumo,vazao,vazamento,vazamento_valor,fechado,delay):
        self.mes = 9
        self.ano = 2022
        self.consumo = consumo
        self.vazao = vazao
        self.vazamento = vazamento
        self.vazamento_valor = vazamento_valor
        self.fechado = fechado
        self.delay = delay
        seed(time.time())
        self.id = randint(0,100000)
        self.tendencia = 1

    def ContabilizarConsumo(self): #Contabiliza o consumo do hidrometro
            #Contabiliza o consumo baseado na tendencia
            if(self.tendencia == 1): #Tendencia Porco ( não toma banho)
                self.consumo +=  ( ( self.vazao - self.vazamento_valor ) * randint(1,2) ) * self.delay
            elif(self.tendencia ==2 ): #Tendencia normal
                self.consumo +=  ( ( self.vazao - self.vazamento_valor ) * randint(3,5) ) * self.delay + 1.1
            elif(self.tendencia ==3 ): #Tendencia rapida
                self.consumo +=  ( ( self.vazao - self.vazamento_valor ) * randint(5,6) ) * self.delay + 2.2
            elif(self.tendencia ==4 ): #Tendencia Dono da embasa
                self.consumo +=  ( ( self.vazao - self.vazamento_valor ) * randint(6,12) ) * self.delay + 5
            # Deteca a existencia de  um vazamento
            if(self.vazamento_valor > 0):
                self.vazamento = True
            else:
                self.vazamento = False

    def GerarBoleto(self): # Gera o boleto do hidrometro
        valor = self.consumo * 10.69
        valor_consumo = (valor,self.consumo)
        if(self.mes == 12):
            self.mes = 0
            self.ano = self.ano + 1
        self.mes = self.mes + 1
        return valor_consumo
           
    def getDadoJSON(self): #Pega os dados do hidrometro e os transforma num Json
        x = {
            "ID": self.id,
            "consumo": self.consumo,
            "vazao": self.vazao,
            "vazamento": self.vazamento,
            "vazamento_valor": self.vazamento_valor,
            "fechado": self.fechado,
            "delay": self.delay,
            "mes": self.mes,
            "ano": self.ano,
        }
        x = json.dumps(x)
        return x

if __name__ == '__main__':
    hidro = Hidrante(0,25,False,False)
    hidro.run(Config.CONSUMO_DELAY)