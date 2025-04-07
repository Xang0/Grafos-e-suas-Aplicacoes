class Graph:
    def __init__(self):
        self.vertices = set()               # Armazena os vértices (nós) do grafo.
        self.edges = []                     # Lista de arestas bidirecionais (tuplas).
        self.arcs = []                      # Lista de arcos unidirecionais (tuplas).
        self.required_vertices = set()      # Vértices que exigem serviços.
        self.required_edges = []            # Arestas que exigem serviços.
        self.required_arcs = []             # Arcos que exigem serviços.


def read_graph(filename):
    graph = Graph()
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if parts[0] == 'VERTICE':
                graph.vertices.add(parts[1])
            elif parts[0] == 'ARESTA':
                u, v = parts[1], parts[2]
                graph.edges.append((u, v))
            elif parts[0] == 'ARCO':
                u, v = parts[1], parts[2]
                graph.arcs.append((u, v))
            elif parts[0] == 'REQUERIDO_V':
                graph.required_vertices.add(parts[1])
            elif parts[0] == 'REQUERIDO_E':
                u, v = parts[1], parts[2]
                graph.required_edges.append((u, v))
            elif parts[0] == 'REQUERIDO_A':
                u, v = parts[1], parts[2]
                graph.required_arcs.append((u, v))
    return graph