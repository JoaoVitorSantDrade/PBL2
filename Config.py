PORT = 3250 # Porta utilizada. Acima de 1024 e escolhida aleatoriamente
PORT_EXTERNA = 120 # Porta utilizada para as requisições
HOST = "localhost" # IP que iremos conectar o servidor e o cliente
HOST_EXTERNA = "localhost" # Endereço de IP para requisições externas
PAYLOAD_SIZE = 1024 # Multiplos de 8
TESTE = True # Indica se estamos debugando
SERVIDOR = False # Indica se iremos rodar um Servidor ou um Cliente
SERVER_LISTEN = 32 # Numero de conexões maxima pelo servidor
TIMEOUT = 600 # Tempo de timeout em segundos
TIMEOUT_EXTERNO = 600
PACKET_SIZE = 512 # Tamanho de cada pacote
TEST_MESSAGE = "Testando o envio de strings"
DELAY = 2
CONSUMO_DELAY = 10
TICKS_TO_GENERATE_PAYMENT = (30 / DELAY)

