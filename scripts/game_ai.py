# Autor: Deivi Rodriguez Paulino 
# Matrícula: 21-SISN-2-052
# Archivo: game_ai.py
# Descripción: Algoritmo A* para pathfinding

def a_star(start, goal, grid):
    """
    Calcula el camino más corto usando A*
    start: (fila, columna)
    goal: (fila, columna)
    grid: matriz 2D donde 0 = libre, 1 = obstáculo/camino
    """
    from heapq import heappush, heappop

    # Movimientos permitidos: arriba, abajo, izquierda, derecha
    movimientos = [(-1,0), (1,0), (0,-1), (0,1)]
    filas = len(grid)
    columnas = len(grid[0])

    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}

    def heuristica(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    while open_set:
        _, actual = heappop(open_set)

        if actual == goal:
            # Reconstruir camino
            path = []
            while actual in came_from:
                path.append(actual)
                actual = came_from[actual]
            path.append(start)
            path.reverse()
            return path

        for movimiento in movimientos:
            vecino = (actual[0] + movimiento[0], actual[1] + movimiento[1])
            if (0 <= vecino[0] < filas) and (0 <= vecino[1] < columnas):
                if grid[vecino[0]][vecino[1]] == 1:
                    # Si es camino, permitimos movernos
                    tentative_g = g_score[actual] + 1
                    if vecino not in g_score or tentative_g < g_score[vecino]:
                        came_from[vecino] = actual
                        g_score[vecino] = tentative_g
                        f_score = tentative_g + heuristica(vecino, goal)
                        heappush(open_set, (f_score, vecino))
    return None
