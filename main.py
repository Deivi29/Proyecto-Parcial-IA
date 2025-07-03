# Autor: Deivi Rodriguez Paulino
# Matrícula: 21-SISN-2-052
# Archivo: main.py
# Descripción: Juego base Tower Defense Retro con menú inicial

import pygame
import sys
import random
from scripts.game_ai import a_star
from scripts.behavior_tree import Selector, Sequence, Condition, Action

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# Pantalla completa
info = pygame.display.Info()
ANCHO_VENTANA = info.current_w
ALTO_VENTANA = info.current_h
pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.FULLSCREEN)
pygame.display.set_caption("Tower Defense Retro")

# Música y sonido
pygame.mixer.music.load("assets/music/blackground.ogg")
pygame.mixer.music.set_volume(0.3)
sonido_disparo = pygame.mixer.Sound("assets/sounds/shoot.wav")
sonido_disparo.set_volume(0.7)

# Sprite enemigo
enemigo_imagen = pygame.image.load("assets/images/enemigo.png").convert_alpha()
enemigo_imagen = pygame.transform.scale(enemigo_imagen, (40, 40))

# Colores
COLOR_FONDO = (10, 10, 10)
COLOR_GRID = (40, 40, 40)
COLOR_PATH = (80, 80, 80)
COLOR_TEXTO = (200, 200, 200)
COLOR_DISPARO = (255, 255, 0)

# Fuente
fuente = pygame.font.Font(None, 42)
fuente_grande = pygame.font.Font(None, 80)

# Opciones de menú
opciones = ["Iniciar Juego", "Salir"]
opcion_seleccionada = 0

# FPS
clock = pygame.time.Clock()

def dibujar_menu():
    pantalla.fill(COLOR_FONDO)
    for i, texto in enumerate(opciones):
        color = (255, 215, 0) if i == opcion_seleccionada else COLOR_TEXTO
        superficie = fuente.render(texto, True, color)
        rect = superficie.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 + i * 60))
        pantalla.blit(superficie, rect)
    pygame.display.flip()

def bucle_juego():
    en_juego = True

    # Grilla
    filas = 10
    columnas = 16
    tamano_celda = 70
    margen = 1

    # Crear grilla con camino central por defecto
    grilla = []
    for fila in range(filas):
        grilla.append([])
        for columna in range(columnas):
            grilla[fila].append(0)

    # Torre
    torre_col = columnas // 2
    torre_fila = filas - 1

    # Enemigos
    enemigos = []
    spawn_delay = 2000
    ultimo_spawn = pygame.time.get_ticks()
    velocidad_base = 0.03

    # Vidas y puntaje
    vidas = 3
    puntaje = 0
    record = 0
    enemigos_muertos = 0
    nivel = 1

    # Disparos
    disparos = []

    # Música
    pygame.mixer.music.play(-1)

    juego_terminado = False
    resultado_texto = ""

    while en_juego:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    en_juego = False
                if evento.key == pygame.K_LEFT and torre_col > 0:
                    torre_col -= 1
                if evento.key == pygame.K_RIGHT and torre_col < columnas - 1:
                    torre_col += 1
                if evento.key == pygame.K_SPACE and not juego_terminado:
                    sonido_disparo.play()
                    disparos.append({
                        "pos": [
                            (margen + tamano_celda) * torre_col + tamano_celda // 2 - 5,
                            (margen + tamano_celda) * torre_fila
                        ]
                    })

        pantalla.fill(COLOR_FONDO)

        # Spawn enemigos
        now = pygame.time.get_ticks()
        if not juego_terminado and now - ultimo_spawn > spawn_delay:
            spawn_col = random.randint(0, columnas - 1)
            goal_col = random.randint(0, columnas - 1)
            start = (0, spawn_col)
            goal = (filas - 1, goal_col)
            camino = a_star(start, goal, grilla)

            if camino:
                enemigos.append({
                    "camino": camino,
                    "paso": 0,
                    "vivo": True,
                    "hp": 3,
                    "velocidad": velocidad_base
                })
            ultimo_spawn = now

        # Dibujar grilla
        for fila in range(filas):
            for columna in range(columnas):
                pygame.draw.rect(
                    pantalla,
                    COLOR_GRID,
                    [
                        (margen + tamano_celda) * columna,
                        (margen + tamano_celda) * fila,
                        tamano_celda,
                        tamano_celda
                    ]
                )

        enemigos_vivos = 0

        for enemigo in enemigos:
            if not enemigo["vivo"]:
                continue
            enemigo["paso"] += enemigo["velocidad"] if not juego_terminado else 0

            if enemigo["paso"] >= len(enemigo["camino"]):
                vidas -= 1
                enemigo["vivo"] = False
                if vidas <= 0:
                    juego_terminado = True
                    resultado_texto = "¡PERDISTE!"
                continue

            if enemigo["paso"] >= 0:
                fila, columna = enemigo["camino"][int(enemigo["paso"])]
                enemigo_rect = pygame.Rect(
                    (margen + tamano_celda) * columna,
                    (margen + tamano_celda) * fila,
                    tamano_celda,
                    tamano_celda
                )
                pantalla.blit(enemigo_imagen, enemigo_rect.topleft)
                enemigo["rect"] = enemigo_rect
                enemigos_vivos += 1

        # Mover disparos
        nuevos_disparos = []
        for disparo in disparos:
            disparo["pos"][1] -= 15
            disparo_rect = pygame.Rect(disparo["pos"][0], disparo["pos"][1], 10, 10)
            pygame.draw.rect(pantalla, COLOR_DISPARO, disparo_rect)

            impactado = False
            for enemigo in enemigos:
                if enemigo.get("rect") and enemigo["vivo"] and disparo_rect.colliderect(enemigo["rect"]):
                    enemigo["hp"] -= 1
                    impactado = True
                    if enemigo["hp"] <= 0:
                        enemigo["vivo"] = False
                        puntaje += 100
                        enemigos_muertos += 1
                        if enemigos_muertos > record:
                            record = enemigos_muertos
                        if enemigos_muertos % 10 == 0:
                            velocidad_base += 0.01
                    break
            if not impactado and disparo["pos"][1] > 0:
                nuevos_disparos.append(disparo)
        disparos = nuevos_disparos

        # Dibujar torre
        torre_rect = pygame.Rect(
            (margen + tamano_celda) * torre_col,
            (margen + tamano_celda) * torre_fila,
            tamano_celda,
            tamano_celda
        )
        pygame.draw.rect(pantalla, (0, 255, 0), torre_rect)

        # Panel lateral
        panel_x = (margen + tamano_celda) * columnas + 40
        y = 40
        info = [
            f"Vidas: {vidas}",
            f"Puntaje: {puntaje}",
            f"Record: {record}",
            f"Enemigos vivos: {enemigos_vivos}",
            f"Nivel velocidad: {round(velocidad_base, 2)}"
        ]
        for line in info:
            txt = fuente.render(line, True, COLOR_TEXTO)
            pantalla.blit(txt, (panel_x, y))
            y += 50

        if juego_terminado:
            txt = fuente_grande.render(resultado_texto, True, (255, 0, 0))
            rect = txt.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2))
            pantalla.blit(txt, rect)

        pygame.display.flip()
        clock.tick(60)

def main():
    global opcion_seleccionada
    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones)
                elif evento.key == pygame.K_DOWN:
                    opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones)
                elif evento.key == pygame.K_RETURN:
                    if opciones[opcion_seleccionada] == "Iniciar Juego":
                        bucle_juego()
                    elif opciones[opcion_seleccionada] == "Salir":
                        pygame.quit()
                        sys.exit()
        dibujar_menu()
        clock.tick(60)

if __name__ == "__main__":
    main()



