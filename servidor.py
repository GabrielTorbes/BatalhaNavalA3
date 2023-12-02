from navio import Navio 
from jogador import Jogador
import socket
from threading import Thread
import pickle

#config servidor
socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost" #ip maquina host para testar na faculdade
porta = 12397
socket_servidor.bind((host, porta))
socket_servidor.listen()
print("\nEsperando jogadores...")

#mensagens
msgAguardando = "Aguardando outro jogador..."
msgIniciando = "Iniciando partida!"
msgAguardandoNavios = "Aguardando o outro jogador terminar de posicionar seus navios"
msgNaviosPosicionados = '\nNavios posicionados, iniciando partida'

#constantes
jogadorUm = 1
jogadorDois = 2
socket = 0
addr = 1
jogador = 2
ip = 0
porta = 1
totalNaviosPorJogador = 3
tamanho_resposta = 8192
acertosNecessarios = 13

#dicionário de jogadores
jogadores = {}

#funções
def esperaConexao(idJogador):
    socket_jogador, addr_jogador = socket_servidor.accept()
    jogadores[idJogador] = (socket_jogador, addr_jogador, Jogador(idJogador))
    enviarMensagemParaJogador(idJogador, msgAguardando)
    print('\nConexão recebida do IP: ' + jogadores[idJogador][addr][ip] + ':' + str(jogadores[idJogador][addr][porta]))

def esperarCriacaoNavios(idJogador):
    while len(jogadores[idJogador][jogador].navios) < totalNaviosPorJogador:
        b = jogadores[idJogador][socket].recv(tamanho_resposta)
        linha, coluna, navio = pickle.loads(b)
        posicaoValida = jogadores[idJogador][jogador].set_navio_em_campo(linha, coluna, navio.direcao, navio.tamanho)
        if posicaoValida:
            jogadores[idJogador][jogador].navios.append(navio)

        enviarMensagemParaJogador(idJogador, posicaoValida)
    
    enviarMensagemParaJogador(idJogador, msgAguardandoNavios)
    print("\nJogador " + str(idJogador) + " terminou de posicionar os navios.")

def enviarMensagemParaAmbosJogadores(mensagem):
    if type(mensagem) is str:
        for j in jogadores.values():
            j[socket].send(mensagem.encode('ascii'))
    else:
        for j in jogadores.values():
            msgBytes = pickle.dumps(mensagem)
            j[socket].send(msgBytes)

def enviarMensagemParaJogador(idJogador, mensagem):
    if type(mensagem) is str:
        jogadores[idJogador][socket].send(mensagem.encode('ascii'))
    else:
        msgBytes = pickle.dumps(mensagem)
        jogadores[idJogador][socket].send(msgBytes)

def executarRodada(idJogadorVez, idJogadorEsperando):
    enviarMensagemParaJogador(idJogadorVez, True)
    enviarMensagemParaJogador(idJogadorEsperando, False)
    envioJogador = jogadores[idJogadorVez][socket].recv(tamanho_resposta)
    linha, coluna = pickle.loads(envioJogador)
    acertou = jogadores[idJogadorEsperando][jogador].verificar_tiro(linha, coluna)
    if acertou:
        enviarMensagemParaAmbosJogadores((True, linha, coluna))
    else:
        enviarMensagemParaAmbosJogadores((False, linha, coluna))

def esperaJogadores(idJogador):
    envioJogador = jogadores[idJogador][socket].recv(tamanho_resposta)

#início do jogo
esperaConexao(jogadorUm)
esperaConexao(jogadorDois)

print("\nPreparando para iniciar a partida")

enviarMensagemParaAmbosJogadores(msgIniciando)

t1 = Thread(target=esperarCriacaoNavios, args=(jogadorUm,))
t2 = Thread(target=esperarCriacaoNavios, args=(jogadorDois,))

t1.start()
t2.start()

t1.join()
t2.join()

print(msgNaviosPosicionados)
enviarMensagemParaAmbosJogadores(msgNaviosPosicionados)

turno = jogadorUm

while True:
    if turno == jogadorUm:
        executarRodada(jogadorUm, jogadorDois)
        turno = jogadorDois
    else:
        executarRodada(jogadorDois, jogadorUm)
        turno = jogadorUm

    #verificar se há um vencedor
    if jogadores[jogadorUm][jogador].partesAbatidas == acertosNecessarios:
        print("Acabou1")
        mensagemJogadorUm = (True, False)
        mensagemJogadorDois = (True, True)
        
        enviarMensagemParaJogador(jogadorUm, mensagemJogadorUm)
        enviarMensagemParaJogador(jogadorDois, mensagemJogadorDois)
        break

    elif jogadores[jogadorDois][jogador].partesAbatidas == acertosNecessarios:
        print("Acabou2")
        mensagemJogadorUm = (True, True)
        mensagemJogadorDois = (True, False)
        
        enviarMensagemParaJogador(jogadorUm, mensagemJogadorUm)
        enviarMensagemParaJogador(jogadorDois, mensagemJogadorDois)
        break
    else:
        enviarMensagemParaAmbosJogadores((False, False))

        t1 = Thread(target=esperaJogadores, args=(jogadorUm,))
        t2 = Thread(target=esperaJogadores, args=(jogadorDois,))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

#fim da conexão
jogadores[jogadorUm][socket].close()
jogadores[jogadorDois][socket].close()
