import pickle
import socket
from navio import Navio

#config da conexão
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("0.0.0.0", 12397)) #ip maquina host para testar na faculdade

#inicialização de variáveis
tiros = {}
matriz = [[0 for x in range(10)] for y in range(10)]
tamanhoResposta = 1024

msgSuaVez = "Sua vez de jogar"
msgAguardeVez = "Aguarde sua rodada"

#config dos navios
navios = {
    0: Navio('Porta-Avião', 5, None),
    1: Navio('Navio-Tanque', 4, None),
    2: Navio('Navio-Tanque', 4, None),
    3: Navio('Contra Torpedeiro', 3, None),
    4: Navio('Contra Torpedeiro', 3, None),
    5: Navio('Contra Torpedeiro', 3, None),
    6: Navio('Submarino', 2, None),
    7: Navio('Submarino', 2, None),
    8: Navio('Submarino', 2, None),
    9: Navio('Submarino', 2, None)
}

#funções
def desenharMatriz():
    print("   ", " ".join([str(a) for a in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]))
    print("   ", "_".join(["_"] * 10))
    x = 0
    for linha in matriz:
        print(x, "|", ' '.join([str(a) for a in linha]))
        x += 1

def validarEntrada(entrada):
    return 0 <= entrada <= 9

def executarTiro():
    while True:
        linha = -1
        coluna = -1
        while True:
            try:
                linha = int(input('Insira a linha que deseja atirar: '))
            except ValueError:
                linha = 99
            if validarEntrada(linha):
                break
            else:
                print("Tiro inválido, entre com o valor novamente.")

        while True:
            try:
                coluna = int(input('Insira a coluna da linha para realizar o tiro: '))
            except ValueError:
                coluna = 99
            if validarEntrada(coluna):
                break
            else:
                print("Tiro inválido, entre com o valor novamente")

        if linha in tiros.keys() and coluna in tiros[linha]:
            print("Tiro já realizado, tente novamente")
        else:
            if linha not in tiros.keys():
                tiros[linha] = []
            tiros[linha] = tiros[linha] + [coluna]
            break
    return linha, coluna

def validarTamanho(entrada, tamanho):
    return (entrada + tamanho) <= 9

def executarPosicionarBarco(navio):
    print(f"O barco {navio.nome} de tamanho {navio.tamanho} deve ser posicionado no campo de batalha")
    while True:
        navio.direcao = input("Entre com a direção do barco (v-Vertical, h-Horizontal): ")
        if navio.direcao in ['v', 'h']:
            break
        else:
            print('Entrada incorreta, tente novamente.')
    while True:
        try:
            linha = int(input("Insira a linha para o posicionamento do barco [0 - 9]: "))
        except ValueError:
            linha = 99
        if validarEntrada(linha) and (navio.direcao == 'h' or (navio.direcao == 'v' and validarTamanho(linha, navio.tamanho))):
            break
        else:
            print('Entrada incorreta, tente novamente.')
    while True:
        try:
            coluna = int(input("Insira a coluna para o posicionamento do barco [0 - 10]: "))
        except ValueError:
            coluna = 99        
        if validarEntrada(coluna) and (navio.direcao == 'v' or (navio.direcao == 'h' and validarTamanho(coluna, navio.tamanho))):
            break
        else:
            print('Entrada incorreta, tente novamente.')
    return linha, coluna, navio

def ReceberEPrintarMensagem():
    msg = s.recv(tamanhoResposta)
    print(msg)
    print(msg.decode('ascii'))

#início do jogo
ReceberEPrintarMensagem()
ReceberEPrintarMensagem()

#posicionamento dos navios
for i in range(3):
    while True:
        posicao = executarPosicionarBarco(navios[i])
        b = pickle.dumps(posicao)
        s.send(b)
        resposta = s.recv(tamanhoResposta)
        posicaoValida = pickle.loads(resposta)
        if posicaoValida:
            break
        else:
            print(f"Já existe um barco posicionado na posição: {posicao[0]}, {posicao[1]}")

ReceberEPrintarMensagem()
ReceberEPrintarMensagem()

#parte principal do jogo
while True:
    resposta = s.recv(tamanhoResposta)
    minhaVez = pickle.loads(resposta)    
    if minhaVez:
        print(msgSuaVez)
        tupla = executarTiro()
        envio = pickle.dumps(tupla)
        s.send(envio)
        resposta = s.recv(tamanhoResposta)
        acertou, linha, coluna = pickle.loads(resposta)
        if acertou:
            matriz[linha][coluna] = 'X'
            print("Acertou!")
        else:
            matriz[linha][coluna] = '~'
            print("Errou!")

        desenharMatriz()
    else:
        print(msgAguardeVez)
        resposta = s.recv(tamanhoResposta)
        acertou, linha, coluna = pickle.loads(resposta)
        if acertou:
            print(f'Seu adversário acertou seu navio na posição: {linha}, {coluna}')
        else:
            print(f'Seu adversário disparou na água na posição: {linha}, {coluna}')

    resposta = s.recv(tamanhoResposta)    
    estadoJogo, ganhador = pickle.loads(resposta)

    if estadoJogo:
        if ganhador:
            print("Você ganhou!")
            break
        else:
            print("Seu adversário ganhou a partida!")
            break
    else:
        s.send("continuar?".encode('ascii'))

#fim da conexão
s.close()
