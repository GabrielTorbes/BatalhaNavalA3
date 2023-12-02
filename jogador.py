class Jogador:
    
    def __init__(self, id):
        self.id = id
        self.navios = []  #armazena os navios
        self.campo = [[0 for x in range(10)] for y in range(10)]  #campo de batalha
        self.tiros = []  #armazena os tiros do jogador
        self.naviosAbatidos = []
        self.partesAbatidas = 0

    def verificar_tiro(self, linha, coluna): #verifica se tem um navio na posição especificada pelos parâmetros linha e coluna
        if(self.campo[linha][coluna] == 1):
            self.partesAbatidas += 1  #incrementa o contador de partes abatidas se houver um navio na posição
            return True
        else:
            return False

    def set_navio_em_campo(self, linha, coluna, direcao, tamanho): #posiciona um navio no campo de batalha do jogador
        if(direcao == 'h'):  #se a direção for horizontal
            if(coluna + tamanho > 9):  #verifica se o navio cabe no campo na direção
                return False
            while tamanho > 0:
                if self.campo[linha][coluna] == 1:  #verifica se tem sobreposição com outro navio
                    return False
                self.campo[linha][coluna] = 1  #marca a posição do navio no campo
                tamanho = tamanho - 1
                coluna = coluna + 1
        else:  # Se a direção for vertical
            if(linha + tamanho > 9):
                return False
            while tamanho > 0:
                if self.campo[linha][coluna] == 1:
                    return False
                self.campo[linha][coluna] = 1
                linha = linha + 1
                tamanho = tamanho - 1
        return True  # Retorna True se o navio foi posicionado com sucesso