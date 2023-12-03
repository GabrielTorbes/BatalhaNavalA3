from navio import Navio
from jogador import Jogador
import socket
from threading import Thread
import pickle

# Configuração do servidor
socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "192.168.1.5"  # IP da máquina host para testar na faculdade
porta = 12397
socket_servidor.bind((host, porta))
socket_servidor.listen()
print("\nEsperando jogadores...")

# Mensagens
mensagem_de_espera = "Aguardando outro jogador..."
mensagem_inicio = "\nPreparem-se para a batalha, que Poseidon tenha piedade dos navios e dos marinheiros!"
mensagem_de_espera_navios = "Aguardando o outro jogador"
mensagem_navio_posicionado = '\nIniciando partida!'

# Constantes
jogador_um = 1
jogador_dois = 2
socketIdx = 0
addrIdx = 1
jogadorIdx = 2
ipIdx = 0
portaIdx = 1
navios_por_jogador = 3  # Para teste, deixar baixo o total de navios
tamanho_resposta = 8192 #aumentar no cliente tbm para testes
acertos_necessarios = 13

# Dicionário de jogadores
jogadores = {}

# Funções
def aguardar_conectar(idJogador): #aguarda conexão do jogador
    socket_jogador, addr_jogador = socket_servidor.accept()
    jogadores[idJogador] = (socket_jogador, addr_jogador, Jogador(idJogador))
    mensagem_para_jogador(idJogador, mensagem_de_espera)
    print('\nConexão recebida do IP: ' + jogadores[idJogador][addrIdx][ipIdx] + ':' + str(jogadores[idJogador][addrIdx][portaIdx]))

def criar_navios(idJogador): #aguarda a criação e posicionamento dos navios pelo jogador
    while len(jogadores[idJogador][jogadorIdx].navios) < navios_por_jogador:
        b = jogadores[idJogador][socketIdx].recv(tamanho_resposta)
        linha, coluna, navio = pickle.loads(b)
        posicao_valida = jogadores[idJogador][jogadorIdx].set_navio_em_campo(linha, coluna, navio.direcao, navio.tamanho) #trocas
        if posicao_valida:
            jogadores[idJogador][jogadorIdx].navios.append(navio)

        mensagem_para_jogador(idJogador, posicao_valida) #trocas

    mensagem_para_jogador(idJogador, mensagem_de_espera_navios)
    print("\nJogador " + str(idJogador) + " terminou de posicionar os navios.")

def mensagens_para_ambos(mensagem): #envia mensagem para ambos os jogadores
    if type(mensagem) is str:
        for j in jogadores.values():
            j[socketIdx].send(mensagem.encode('ascii'))
    else:
        for j in jogadores.values():
            msgBytes = pickle.dumps(mensagem)
            j[socketIdx].send(msgBytes)

def mensagem_para_jogador(idJogador, mensagem): #envia mensagem para um jogador
    if type(mensagem) is str:
        jogadores[idJogador][socketIdx].send(mensagem.encode('ascii'))
    else:
        msgBytes = pickle.dumps(mensagem)
        jogadores[idJogador][socketIdx].send(msgBytes)

def executar_rodada(idJogadorVez, idJogadorEsperando): #executa uma rodada do jogo
    mensagem_para_jogador(idJogadorVez, True)
    mensagem_para_jogador(idJogadorEsperando, False)
    envioJogador = jogadores[idJogadorVez][socketIdx].recv(tamanho_resposta)
    linha, coluna = pickle.loads(envioJogador)
    acertou = jogadores[idJogadorEsperando][jogadorIdx].verificar_tiro(linha, coluna)
    if acertou:
        mensagens_para_ambos((True, linha, coluna))
    else:
        mensagens_para_ambos((False, linha, coluna))

def aguardar_jogadores(idJogador): #aguarda ações dos jogadores
    envioJogador = jogadores[idJogador][socketIdx].recv(tamanho_resposta)

# Início do jogo
aguardar_conectar(jogador_um)
aguardar_conectar(jogador_dois)

print("\nPreparando para iniciar a partida")

mensagens_para_ambos(mensagem_inicio)

t1 = Thread(target=criar_navios, args=(jogador_um,))
t2 = Thread(target=criar_navios, args=(jogador_dois,))

t1.start()
t2.start()

t1.join()
t2.join()

print(mensagem_navio_posicionado)
mensagens_para_ambos(mensagem_navio_posicionado)

turno = jogador_um

while True:
    if turno == jogador_um:
        executar_rodada(jogador_um, jogador_dois)
        turno = jogador_dois
    else:
        executar_rodada(jogador_dois, jogador_um)
        turno = jogador_um

    # Verificar se há um vencedor
    if jogadores[jogador_um][jogadorIdx].partes_acertadas == acertos_necessarios:
        print("Acabou1")
        mensagem_jogador_um = (True, False)
        mensagem_jogador_dois = (True, True)

        mensagem_para_jogador(jogador_um, mensagem_jogador_um)
        mensagem_para_jogador(jogador_dois, mensagem_jogador_dois)
        break

    elif jogadores[jogador_dois][jogadorIdx].partes_acertadas == acertos_necessarios:
        print("Acabou2")
        mensagem_jogador_um = (True, True)
        mensagem_jogador_dois = (True, False)

        mensagem_para_jogador(jogador_um, mensagem_jogador_um)
        mensagem_para_jogador(jogador_dois, mensagem_jogador_dois)
        break
    else:
        mensagens_para_ambos((False, False))

        t1 = Thread(target=aguardar_jogadores, args=(jogador_um,))
        t2 = Thread(target=aguardar_jogadores, args=(jogador_dois,))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

# Fim da conexão
jogadores[jogador_um][socketIdx].close()
jogadores[jogador_dois][socketIdx].close()
