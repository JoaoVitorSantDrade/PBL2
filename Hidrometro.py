from pickle import TRUE
from shutil import ExecError
from threading import local
import Hidrante
from multiprocessing import Process, Manager
import time
import os
import json
from time import localtime, sleep, strftime

class Hidrometro:
    
    def __init__(self,hidrante):   
        self.hidrante = hidrante
        self.mes = 9
        self.ano = 2022
        self.Server = None

def main():

    os.system('cls' if os.name == 'nt' else 'clear')
    vazao = input("Informe a vazao:")

    hidro = Hidrante.Hidrante(0,vazao,False,0.0,False,4)

    hidrometro = Hidrometro(hidro)

    print("O seu ID é: %s\n" % (str(hidro.id)))

    while TRUE:
        hidro.ContabilizarConsumo()
        print(hidro.consumo)
        time.sleep(5)
    
if __name__ == '__main__':
    main()