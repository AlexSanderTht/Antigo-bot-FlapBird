import pygame
import os
import random
import neat

pygame.font.init()

TELA_LARGURA = 500
TELA_ALTURA = 800

IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', f'bird{i}.png')))
    for i in range(1, 4)
]
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
FONTE_PONTOS = pygame.font.SysFont('arial', 50)


class Passaro:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = IMAGENS_PASSARO[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2
        self.y += deslocamento
        if deslocamento < 0 or self.y < (self.altura + 50):
            self.angulo = min(25, self.angulo + 20)
        else:
            self.angulo = max(-90, self.angulo - 20)

    def desenhar(self, tela):
        self.contagem_imagem += 1
        self.imagem = IMAGENS_PASSARO[(self.contagem_imagem // 5) % 3]
        if self.angulo <= -80:
            self.imagem = IMAGENS_PASSARO[1]
        tela.blit(pygame.transform.rotate(self.imagem, self.angulo), (self.x, self.y))


class Cano:
    DISTANCIA = 200
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(IMAGEM_CANO, (self.x, self.altura - IMAGEM_CANO.get_height()))
        tela.blit(pygame.transform.flip(IMAGEM_CANO, False, True), (self.x, self.altura + self.DISTANCIA))

    def colidir(self, passaro):
        passaro_mask = pygame.mask.from_surface(passaro.imagem)
        topo_mask = pygame.mask.from_surface(IMAGEM_CANO)
        base_mask = pygame.mask.from_surface(pygame.transform.flip(IMAGEM_CANO, False, True))

        distancia_topo = (self.x - passaro.x, self.altura - round(passaro.y))
        distancia_base = (self.x - passaro.x, (self.altura + self.DISTANCIA) - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        return bool(base_ponto or topo_ponto)


class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE
        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(IMAGEM_CHAO, (self.x1, self.y))
        tela.blit(IMAGEM_CHAO, (self.x2, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)
    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    pygame.display.update()


def main(genomas, config):
    passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()
    rodando = True

    while rodando:
        relogio.tick(30)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()

        for passaro in passaros:
            passaro.mover()
        chao.mover()

        remover_canos = []
        adicionar_cano = False
        for cano in canos:
            for passaro in passaros:
                if cano.colidir(passaro):
                    passaros.remove(passaro)
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + IMAGEM_CANO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))
        for cano in remover_canos:
            canos.remove(cano)

        for passaro in passaros:
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.remove(passaro)

        desenhar_tela(tela, passaros, canos, chao, pontos)


def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config)
    populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())
    populacao.run(main, 50)


if __name__ == '__main__':
    caminho = os.path.dirname(__file__)
    caminho_config = os.path.join(caminho, 'config.txt')
    rodar(caminho_config)
