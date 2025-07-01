# Autor: Deivi Rodriguez Paulino 
# Matrícula: 21-SISN-2-052
# Archivo: behavior_tree.py
# Descripción: Árbol de comportamiento completo para torre

class Node:
    """Nodo base de comportamiento"""
    def run(self, context):
        raise NotImplementedError("Método run() no implementado en Node base.")

class Selector(Node):
    """
    Intenta cada hijo en orden.
    Retorna SUCCESS en el primero que funciona.
    Si ninguno funciona, retorna FAILURE.
    """
    def __init__(self, children):
        self.children = children

    def run(self, context):
        for child in self.children:
            result = child.run(context)
            if result == "SUCCESS":
                return "SUCCESS"
        return "FAILURE"

class Sequence(Node):
    """
    Ejecuta todos los hijos en orden.
    Si alguno falla, la secuencia falla.
    Si todos tienen éxito, retorna SUCCESS.
    """
    def __init__(self, children):
        self.children = children

    def run(self, context):
        for child in self.children:
            result = child.run(context)
            if result == "FAILURE":
                return "FAILURE"
        return "SUCCESS"

class Condition(Node):
    """
    Nodo que evalúa una función booleana.
    Si la función retorna True, SUCCESS.
    Si False, FAILURE.
    """
    def __init__(self, condition_fn):
        self.condition_fn = condition_fn

    def run(self, context):
        if self.condition_fn(context):
            return "SUCCESS"
        return "FAILURE"

class Action(Node):
    """
    Nodo que ejecuta una acción (función).
    Siempre retorna SUCCESS.
    """
    def __init__(self, action_fn):
        self.action_fn = action_fn

    def run(self, context):
        self.action_fn(context)
        return "SUCCESS"
