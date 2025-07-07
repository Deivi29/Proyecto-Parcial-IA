# Autor: Deivi Rodriguez Paulino
# Matrícula: 21-SISN-2-052
# Archivo: main.py
# Descripción: Juego base Tower Defense Retro con menú inicial

import pygame
import sys
import random
from scripts.game_ai import a_star

pygame.init()
pygame.mixer.init()

# Obtener tamaño completo de pantalla
ANCHO_VENTANA, ALTO_VENTANA = pygame.display.get_desktop_sizes()[0]
pantalla = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
pygame.display.set_caption("Tower Defense Retro")

torre_imagen = pygame.image.load("assets/images/torre.png").convert_alpha()
torre_imagen = pygame.transform.scale(torre_imagen, (50, 50))

disparo_imagen = pygame.image.load("assets/images/disparo.png").convert_alpha()
disparo_imagen = pygame.transform.scale(disparo_imagen, (15, 15))

explosion_imagen = pygame.image.load("assets/images/explosion.png").convert_alpha()
explosion_imagen = pygame.transform.scale(explosion_imagen, (50, 50))

enemigo_imagen = pygame.image.load("assets/images/enemigo.png").convert_alpha()
enemigo_imagen = pygame.transform.scale(enemigo_imagen, (50, 50))

COLOR_FONDO = (20, 20, 20)
COLOR_TEXTO = (255, 255, 255)

fuente = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

opciones = ["Iniciar Juego", "Salir"]
opcion_seleccionada = 0

# Inicializar joystick si hay
pygame.joystick.init()
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Gamepad detectado:", joystick.get_name())

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
    filas, columnas = 10, 10
    tamano_celda = 60
    margen = 2

    ancho_grilla = columnas * (tamano_celda + margen)
    alto_grilla = filas * (tamano_celda + margen)
    offset_x = (ANCHO_VENTANA - ancho_grilla) // 2
    offset_y = (ALTO_VENTANA - alto_grilla) // 2

    grilla = [[0]*columnas for _ in range(filas)]
    torre_pos_x = ANCHO_VENTANA // 2 - 25
    torre_pos_y = offset_y + alto_grilla + 20

    enemigos = []
    spawn_timer = pygame.time.get_ticks()
    spawn_delay = 800

    disparos = []
    explosiones = []

    enemigos_que_pasaron = 0
    puntos = 0
    velocidad_enemigos = 2

    pygame.mixer.music.load("assets/music/blackground.ogg")
    pygame.mixer.music.play(-1)
    sonido_disparo = pygame.mixer.Sound("assets/sounds/shoot.wav")

    boton_disparo_presionado = False

    

    while en_juego:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    en_juego = False
                if evento.key == pygame.K_SPACE:
                    sonido_disparo.play()
                    disparos.append(pygame.Rect(
                        torre_pos_x + 20,
                        torre_pos_y,
                        15,
                        15
                    ))

        # Movimiento con teclado
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] and torre_pos_x > 0:
            torre_pos_x -= 5
        if teclas[pygame.K_RIGHT] and torre_pos_x < ANCHO_VENTANA - 50:
            torre_pos_x += 5

        # Movimiento con joystick
        if joystick:
            axis_x = joystick.get_axis(0)
            if abs(axis_x) > 0.2:
                torre_pos_x += axis_x * 7
                torre_pos_x = max(0, min(torre_pos_x, ANCHO_VENTANA - 50))
            # Disparo con botón A (un disparo por pulsación)
            if joystick.get_button(0):
                if not boton_disparo_presionado:
                    sonido_disparo.play()
                    disparos.append(pygame.Rect(
                        torre_pos_x + 20,
                        torre_pos_y,
                        15,
                        15
                    ))
                boton_disparo_presionado = True
            else:
                boton_disparo_presionado = False

        if pygame.time.get_ticks() - spawn_timer > spawn_delay:
            cantidad_spawn = random.randint(1, 2)
            for _ in range(cantidad_spawn):
                fila = 0
                columna = random.randint(0, columnas-1)
                columna_destino = random.randint(0, columnas-1)
                camino = a_star((fila, columna), (filas - 1, columna_destino), grilla)
                if camino:
                    enemigos.append({
                        "camino": camino,
                        "index": 0,
                        "progress": 0.0,
                        "vida": 3
                    })
            spawn_timer = pygame.time.get_ticks()

        pantalla.fill(COLOR_FONDO)

        for fila in range(filas):
            for columna in range(columnas):
                pygame.draw.rect(
                    pantalla,
                    (30,30,30),
                    [
                        offset_x + (margen + tamano_celda)*columna,
                        offset_y + (margen + tamano_celda)*fila,
                        tamano_celda,
                        tamano_celda
                    ]
                )

        nuevos_enemigos = []
        for enemigo in enemigos:
            camino = enemigo["camino"]
            idx = enemigo["index"]

            if idx < len(camino) - 1:
                actual = camino[idx]
                siguiente = camino[idx + 1]

                ax = offset_x + (margen + tamano_celda)*actual[1]
                ay = offset_y + (margen + tamano_celda)*actual[0]
                bx = offset_x + (margen + tamano_celda)*siguiente[1]
                by = offset_y + (margen + tamano_celda)*siguiente[0]

                enemigo["progress"] += velocidad_enemigos / 50.0
                if enemigo["progress"] >= 1.0:
                    enemigo["progress"] = 0.0
                    enemigo["index"] += 1

            if enemigo["index"] >= len(camino)-1:
                enemigos_que_pasaron += 1
                continue
            else:
                actual = camino[enemigo["index"]]
                siguiente = camino[enemigo["index"] + 1]
                ax = offset_x + (margen + tamano_celda)*actual[1]
                ay = offset_y + (margen + tamano_celda)*actual[0]
                bx = offset_x + (margen + tamano_celda)*siguiente[1]
                by = offset_y + (margen + tamano_celda)*siguiente[0]
                x = ax + (bx - ax)*enemigo["progress"]
                y = ay + (by - ay)*enemigo["progress"]

                enemigo["pos_rect"] = pygame.Rect(x, y, 50, 50)
                pantalla.blit(enemigo_imagen, (x, y))
                nuevos_enemigos.append(enemigo)

        enemigos = nuevos_enemigos

        nuevos_disparos = []
        for disparo in disparos:
            disparo.y -=10
            pantalla.blit(disparo_imagen, (disparo.x, disparo.y))
            impactado = False
            for enemigo in enemigos:
                if enemigo.get("pos_rect") and disparo.colliderect(enemigo["pos_rect"]):
                    enemigo["vida"] -=1
                    if enemigo["vida"] <=0:
                        puntos +=1
                        explosiones.append({"pos": enemigo["pos_rect"].topleft, "timer":20})
                        enemigos.remove(enemigo)
                        if puntos % 5 == 0:
                            velocidad_enemigos += 0.3
                    impactado = True
                    break
            if not impactado and disparo.y > 0:
                nuevos_disparos.append(disparo)
        disparos = nuevos_disparos

        nuevas_explosiones = []
        for ex in explosiones:
            pantalla.blit(explosion_imagen, ex["pos"])
            ex["timer"] -=1
            if ex["timer"] >0:
                nuevas_explosiones.append(ex)
        explosiones = nuevas_explosiones

        pantalla.blit(torre_imagen, (torre_pos_x, torre_pos_y))
        text = fuente.render(f"Puntos: {puntos}  Enemigos que pasaron: {enemigos_que_pasaron}/3", True, COLOR_TEXTO)
        pantalla.blit(text, (10,10))

        if enemigos_que_pasaron >=3:
            game_over = True
            while game_over:
                pantalla.fill(COLOR_FONDO)
                text = fuente.render("GAME OVER", True, (255,0,0))
                pantalla.blit(text,(ANCHO_VENTANA//2 -100,ALTO_VENTANA//2))
                text2 = fuente.render("Presiona ESC para volver al menú", True, (255,255,255))
                pantalla.blit(text2,(ANCHO_VENTANA//2 -200,ALTO_VENTANA//2 +50))
                pygame.display.flip()
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_ESCAPE:
                            return

        pygame.display.flip()
        clock.tick(60)

def main():
    global opcion_seleccionada
    ejecutando = True

    joystick_timer = 0  # Para evitar scroll rápido al mantener el eje

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    opcion_seleccionada = (opcion_seleccionada -1)%len(opciones)
                elif evento.key == pygame.K_DOWN:
                    opcion_seleccionada = (opcion_seleccionada +1)%len(opciones)
                elif evento.key == pygame.K_RETURN:
                    if opciones[opcion_seleccionada]=="Iniciar Juego":
                        bucle_juego()
                    elif opciones[opcion_seleccionada]=="Salir":
                        pygame.quit()
                        sys.exit()

        # Si hay joystick
        if joystick:
            axis_y = joystick.get_axis(1)
            if abs(axis_y) > 0.4 and pygame.time.get_ticks() - joystick_timer > 250:
                if axis_y < 0:
                    opcion_seleccionada = (opcion_seleccionada -1)%len(opciones)
                elif axis_y > 0:
                    opcion_seleccionada = (opcion_seleccionada +1)%len(opciones)
                joystick_timer = pygame.time.get_ticks()

            # Botón 0 como "Enter"
            if joystick.get_button(0):
                if opciones[opcion_seleccionada]=="Iniciar Juego":
                    bucle_juego()
                elif opciones[opcion_seleccionada]=="Salir":
                    pygame.quit()
                    sys.exit()

        dibujar_menu()
        clock.tick(60)

if __name__=="__main__":
    main()



