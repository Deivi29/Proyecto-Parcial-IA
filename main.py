# Autor: Deivi Rodriguez Paulino
# Matrícula: 21-SISN-2-052
# Archivo: main.py
# Descripción: Juego base Tower Defense Retro con menú inicial

from scripts.game_ai import a_star
from scripts.behavior_tree import Selector, Sequence, Condition, Action


import pygame
import sys

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Tower Defense Retro")

# Colores
COLOR_FONDO = (30, 30, 30)
COLOR_TEXTO = (255, 255, 255)
COLOR_SELECCION = (255, 215, 0)

# Fuente
fuente = pygame.font.Font(None, 48)

# Opciones de menú
opciones = ["Iniciar Juego", "Salir"]
opcion_seleccionada = 0

# Control de FPS
clock = pygame.time.Clock()

def dibujar_menu():
    pantalla.fill(COLOR_FONDO)
    for i, texto in enumerate(opciones):
        if i == opcion_seleccionada:
            color = COLOR_SELECCION
        else:
            color = COLOR_TEXTO
        superficie_texto = fuente.render(texto, True, color)
        rect_texto = superficie_texto.get_rect(center=(ANCHO_VENTANA // 2, 200 + i * 60))
        pantalla.blit(superficie_texto, rect_texto)
    pygame.display.flip()

def hay_enemigo_en_rango(context):
    """Devuelve True si el enemigo está cerca de la torre"""
    enemigo_pos = context["enemigo_pos"]
    torre_pos = context["torre_pos"]
    rango = context["rango"]

    dist_fila = abs(enemigo_pos[0] - torre_pos[0])
    dist_columna = abs(enemigo_pos[1] - torre_pos[1])

    return dist_fila <= rango and dist_columna <= rango

def disparar(context):
    """Marca en el contexto que la torre disparó"""
    context["disparo"] = True

def bucle_juego():
    """Lógica principal del juego"""
    en_juego = True

    # Configuración de grilla (10x10 celdas)
    filas = 10
    columnas = 10
    tamano_celda = 50
    margen = 2

    # Crear una grilla: 0 = terreno, 1 = camino
    grilla = []
    for fila in range(filas):
        grilla.append([])
        for columna in range(columnas):
            if columna == 4:  # columna 4 es el camino
                grilla[fila].append(1)
            else:
                grilla[fila].append(0)

    # Definir punto inicial y final
    start = (0, 4)
    goal = (9, 4)

    # Calcular camino con A*
    camino = a_star(start, goal, grilla)

    # Posición fija de la torre
    torre_pos = (5, 2)

    # Crear el árbol de comportamiento
    arbol = Selector([
        Sequence([
            Condition(hay_enemigo_en_rango),
            Action(disparar)
        ])
    ])

    # Preparar el contexto
    context = {
        "torre_pos": torre_pos,
        "enemigo_pos": start,
        "rango": 2,
        "disparo": False
    }

    # Índice de la posición actual del enemigo
    paso_actual = 0

    # Tiempo entre pasos (en milisegundos)
    tiempo_entre_pasos = 500
    ultimo_movimiento = pygame.time.get_ticks()

    while en_juego:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    en_juego = False

        pantalla.fill((50, 50, 50))

        # Dibujar la grilla
        for fila in range(filas):
            for columna in range(columnas):
                color = (0, 100, 0)  # terreno
                if grilla[fila][columna] == 1:
                    color = (100, 100, 100)  # camino
                pygame.draw.rect(
                    pantalla,
                    color,
                    [
                        (margen + tamano_celda) * columna + margen,
                        (margen + tamano_celda) * fila + margen,
                        tamano_celda,
                        tamano_celda,
                    ]
                )

        # Mover el enemigo paso a paso
        if camino and paso_actual < len(camino):
            now = pygame.time.get_ticks()
            if now - ultimo_movimiento > tiempo_entre_pasos:
                paso_actual += 1
                ultimo_movimiento = now

        # Dibujar el enemigo en la posición actual y actualizar contexto
        if camino and paso_actual < len(camino):
            fila, columna = camino[paso_actual]
            context["enemigo_pos"] = (fila, columna)

            pygame.draw.rect(
                pantalla,
                (200, 0, 0),  # color rojo
                [
                    (margen + tamano_celda) * columna + margen,
                    (margen + tamano_celda) * fila + margen,
                    tamano_celda,
                    tamano_celda,
                ]
            )

        # Ejecutar el árbol de comportamiento
        arbol.run(context)

        # Dibujar el disparo si corresponde
        if context["disparo"]:
            pygame.draw.rect(
                pantalla,
                (255, 255, 0),  # amarillo
                [
                    (margen + tamano_celda) * columna + margen,
                    (margen + tamano_celda) * fila + margen,
                    tamano_celda,
                    tamano_celda,
                ]
            )
            # Reiniciar disparo
            context["disparo"] = False

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

