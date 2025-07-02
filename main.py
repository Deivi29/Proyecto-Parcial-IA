# Autor: Deivi Rodriguez Paulino
# Matrícula: 21-SISN-2-052
# Archivo: main.py
# Descripción: Juego base Tower Defense Retro con menú inicial

import pygame
import sys
from scripts.game_ai import a_star
from scripts.behavior_tree import Selector, Sequence, Condition, Action 

# Inicializar Pygame
pygame.init()
pygame.joystick.init()
pygame.mixer.init()

pygame.mixer.music.load("assets/music/blackground.ogg")
pygame.mixer.music.set_volume(0.5)  # Volumen de la música
sonido_disparo = pygame.mixer.Sound("assets/sounds/shoot.wav")
sonido_disparo.set_volume(0.7)  # Volumen del disparo

# Configuración de la ventana
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Tower Defense Retro")

# Cargar sprite del enemigo DESPUÉS de inicializar la pantalla
enemigo_imagen = pygame.image.load("assets/images/enemigo.png").convert_alpha()
enemigo_imagen = pygame.transform.scale(enemigo_imagen, (50, 50))

# Colores
COLOR_FONDO = (30, 30, 30)
COLOR_TEXTO = (255, 255, 255)
COLOR_SELECCION = (255, 215, 0)

# Fuente
fuente = pygame.font.Font(None, 48)

# Opciones de menú
opciones = ["Iniciar Juego", "Reiniciar", "Salir"]
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
    print("Entrando en el juego...")

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
    pygame.mixer.music.play(-1)  # -1 significa que se repite indefinidamente


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

            pantalla.blit(
                 enemigo_imagen,
                (
                     (margen + tamano_celda) * columna + margen,
                    (margen + tamano_celda) * fila + margen
                )
            )

        # Ejecutar el árbol de comportamiento
        arbol.run(context)

        # Dibujar el disparo si corresponde
        if context["disparo"]:
            sonido_disparo.play()
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

    opcion_seleccionada = 0

    # Inicializar joystick si existe
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print("Gamepad detectado:", joystick.get_name())
    else:
        joystick = None

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                print("Tecla presionada:", evento.key)
                if evento.key == pygame.K_UP:
                    opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones)
                    print("Opción seleccionada:", opcion_seleccionada)
                elif evento.key == pygame.K_DOWN:
                    print("Opción seleccionada:", opcion_seleccionada)
                    opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones)

                elif evento.key == pygame.K_RETURN:
                    if opciones[opcion_seleccionada] == "Iniciar Juego":
                        bucle_juego()
                    elif opciones[opcion_seleccionada] == "Reiniciar":
                        bucle_juego()
                    elif opciones[opcion_seleccionada] == "Salir":
                        pygame.quit()
                        sys.exit()

        # Leer joystick si está conectado
        if joystick:
            eje_y = joystick.get_axis(1)

            if eje_y < -0.5:
                opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones)
            elif eje_y > 0.5:
                opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones)

            if joystick.get_button(0):
                if opciones[opcion_seleccionada] == "Iniciar Juego":
                    bucle_juego()
                elif opciones[opcion_seleccionada] == "Reiniciar":
                    bucle_juego()
                elif opciones[opcion_seleccionada] == "Salir":
                    pygame.quit()
                    sys.exit()

        dibujar_menu()
        clock.tick(60)


if __name__ == "__main__":
    main()

