import pickle
import socket
from navio import Navio

#config da conexão
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 12397)) #ip maquina host para testar na faculdade

#inicialização de variáveis
tiros = {}
matriz = [[0 for x in range(10)] for y in range(10)]
tamanho_resposta = 8192

mensagem_minha_vez = "\nSua vez de jogar"
mensagem_aguardar = "\nAguarde sua rodada"

#config dos navios
navios = {
    0: Navio('Submarino', 2, None),
    1: Navio('Submarino', 2, None),
    2: Navio('Submarino', 2, None),
    3: Navio('Submarino', 2, None)
}

#funções
def exibir_tabuleiro():
    print("   ", " ".join([str(a) for a in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]))
    print("   ", "_".join(["_"] * 10))
    x = 0
    for linha in matriz:
        print(x, "|", ' '.join([str(a) for a in linha]))
        x += 1

def verifica_entrada(entrada):
    return 0 <= entrada <= 9

def executar_tiro():
    while True:
        try:
            linha = int(input('\nInsira a linha que deseja atirar: '))
            coluna = int(input('\nInsira a coluna que deseja atirar: '))

            if verifica_entrada(linha) and verifica_entrada(coluna):
                if (linha, coluna) not in tiros:
                    tiros[linha] = [coluna]
                    break
                else:
                    print("Tiro já realizado, tente novamente")
            else:
                print("\nTiro inválido, entre com o valor novamente.")
        except ValueError:
            print("Entrada inválida, tente novamente.")

    return linha, coluna

def validar_tamanho(entrada, tamanho):
    return (entrada + tamanho) <= 9

def posicionar_navio(navio):
    print(f"\nPosicione o {navio.nome} no campo de batalha.")

    navio.direcao = input("Entre com a direção do barco (v-Vertical, h-Horizontal): ")
    while navio.direcao not in ['v', 'h']:
        print('Entrada incorreta, tente novamente.')
        navio.direcao = input("Entre com a direção do barco (v-Vertical, h-Horizontal): ")

    while True:
        try:
            linha = int(input("Insira a linha para o posicionamento do barco [0 - 9]: "))
            coluna = int(input("Insira a coluna para o posicionamento do barco [0 - 10]: "))
        except ValueError:
            linha = coluna = 99

        if verifica_entrada(linha) and verifica_entrada(coluna) and (navio.direcao == 'h' or (navio.direcao == 'v' and validar_tamanho(linha, navio.tamanho))):
            break
        else:
            print('Entrada incorreta, tente novamente.')

    return linha, coluna, navio

def receber_e_imprimir(): #possivel erro no online
    msg = s.recv(tamanho_resposta)
    print(msg)
    #print(msg.decode('ascii')) teste tbm
    print(msg.decode('UTF-8'))

#início do jogo
receber_e_imprimir()
receber_e_imprimir()

#posicionamento dos navios
for i in range(3):
    while True:
        posicao = posicionar_navio(navios[i])
        s.send(pickle.dumps(posicao))

        posicaoValida = pickle.loads(s.recv(tamanho_resposta))

        if posicaoValida:
            break
        else:
            print(f"Já existe um barco posicionado aqui, linha {posicao[0]} e coluna {posicao[1]}")

receber_e_imprimir() #erro aqui tbm, sendo que os dois receber_e_imprimir() funcionam com para cada jogador 
receber_e_imprimir()

#parte principal do jogo, verificar mudanças dps
while True: #aterado
    resposta = s.recv(tamanho_resposta)
    minha_vez = pickle.loads(resposta)

    if minha_vez:
        print(mensagem_minha_vez)
        tupla = executar_tiro()
        s.send(pickle.dumps(tupla))

        resposta = s.recv(tamanho_resposta)
        acertou, linha, coluna = pickle.loads(resposta)

        if acertou:
            matriz[linha][coluna] = 'X'
            print("\nAcertou!\n")
        else:
            matriz[linha][coluna] = '~'
            print("\nErrou!\n")

        exibir_tabuleiro()
    else:
        print(mensagem_aguardar)
        resposta = s.recv(tamanho_resposta)
        acertou, linha, coluna = pickle.loads(resposta)

        if acertou:
            print(f'\nSeu adversário acertou seu navio na posição: {linha}, {coluna}')
        else:
            print(f'\nSeu adversário disparou na água')

    resposta = s.recv(tamanho_resposta)
    estado_jogo, ganhador = pickle.loads(resposta)

    if estado_jogo:
        if ganhador:
            print("Você ganhou!")
        else:
            print("Seu adversário ganhou a partida!")
        break
    else:
        s.send("continuar?".encode('ascii'))

# Fim da conexão
s.close()
