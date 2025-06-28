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
    current_section = None
    skip_header = False  # Controla se a próxima linha deve ser ignorada (cabeçalho)
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('the'):
                continue
            
            # Identificar seções e pular cabeçalhos
            if line.startswith('ReN.'):
                current_section = 'required_nodes'
                skip_header = True  # A próxima linha é o cabeçalho "DEMAND S. COST"
                continue
            elif line.startswith('ReE.'):
                current_section = 'required_edges'
                skip_header = True  # A próxima linha é o cabeçalho
                continue
            elif line.startswith('ReA.'):
                current_section = 'required_arcs'
                skip_header = True  # A próxima linha é o cabeçalho
                continue
            elif line.startswith('EDGE'):
                current_section = 'edges'
                skip_header = True  # A próxima linha é o cabeçalho
                continue
            elif line.startswith('ARC'):
                current_section = 'arcs'
                skip_header = True  # A próxima linha é o cabeçalho
                continue
            
            # Pular linha de cabeçalho após identificar a seção
            if skip_header:
                skip_header = False
                continue
            
            parts = line.split('\t')  # Divide por tabulação (ajuste crítico)
            
            # Processar metadados
            if line.startswith('Depot Node:'):
                depot = parts[1].strip()
                graph.depot = depot
                graph.vertices.add(depot)
            
            # Processar seções
            elif current_section == 'required_nodes':
                node_id = parts[0].strip().lstrip('N')  # Remove o 'N' (ex: 'N4' → '4')
                graph.required_vertices.add(node_id)
                graph.vertices.add(node_id)
                
            elif current_section == 'required_edges':
                from_node = parts[1].strip()
                to_node = parts[2].strip()
                graph.required_edges.append((from_node, to_node))
                graph.edges.append((from_node, to_node))  # Assume bidirecional
                graph.vertices.update([from_node, to_node])
                
            elif current_section == 'required_arcs':
                from_node = parts[1].strip()
                to_node = parts[2].strip()
                graph.required_arcs.append((from_node, to_node))
                graph.arcs.append((from_node, to_node))  # Unidirecional
                graph.vertices.update([from_node, to_node])
                
            elif current_section == 'edges':
                from_node = parts[1].strip()
                to_node = parts[2].strip()
                graph.edges.append((from_node, to_node))
                graph.vertices.update([from_node, to_node])
                
            elif current_section == 'arcs':
                from_node = parts[1].strip()
                to_node = parts[2].strip()
                graph.arcs.append((from_node, to_node))
                graph.vertices.update([from_node, to_node])

    return graph