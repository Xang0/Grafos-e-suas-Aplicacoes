from collections import defaultdict, deque

def floyd_warshall(graph):
    nodes = list(graph.vertices)
    n = len(nodes)
    index = {node: i for i, node in enumerate(nodes)}  # Mapeia vértices para índices numéricos
    dist = [[float('inf')] * n for _ in range(n)]      # Matriz de distâncias
    pred = [[None] * n for _ in range(n)]              # Matriz de predecessores
    
    # Inicialização da diagonal (distância para si mesmo é 0)
    for i in range(n):
        dist[i][i] = 0
    
    # Arestas bidirecionais (atualiza ambas as direções)
    for u, v in graph.edges:
        i_u, i_v = index[u], index[v]
        dist[i_u][i_v] = 1
        dist[i_v][i_u] = 1  # Bidirecional
        pred[i_u][i_v] = i_u
        pred[i_v][i_u] = i_v
    
    # Arcos unidirecionais (apenas uma direção)
    for u, v in graph.arcs:
        i_u, i_v = index[u], index[v]
        dist[i_u][i_v] = 1
        pred[i_u][i_v] = i_u
    
    # Atualização das distâncias via vértices intermediários
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]  # Atualiza distância
                    pred[i][j] = pred[k][j]                # Atualiza predecessor
    
    return dist, pred, index


def connected_components(graph):
    adjacency = defaultdict(list)
    
    # Trata arcos como bidirecionais (erro!)
    for u, v in graph.edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    for u, v in graph.arcs:
        adjacency[u].append(v)
        adjacency[v].append(u)  # Incorreto para arcos!
    
    # BFS para encontrar componentes
    visited = set()
    components = []
    for node in graph.vertices:
        if node not in visited:
            queue = deque([node])
            component = []
            while queue:
                current = queue.popleft()
                component.append(current)
                for neighbor in adjacency[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            components.append(component)
    
    return len(components)


def calculate_degrees(graph):
    edge_counts = defaultdict(int)  # Grau por arestas
    in_degree = defaultdict(int)    # Grau de entrada (arcos)
    out_degree = defaultdict(int)   # Grau de saída (arcos)

    # Arestas: incrementa grau de ambos os vértices
    for u, v in graph.edges:
        edge_counts[u] += 1
        edge_counts[v] += 1

    # Arcos: atualiza graus de entrada/saída
    for u, v in graph.arcs:
        out_degree[u] += 1
        in_degree[v] += 1
    
    # Soma graus totais
    degrees = {}
    for node in graph.vertices:
        e_deg = edge_counts.get(node, 0)
        i_deg = in_degree.get(node, 0)
        o_deg = out_degree.get(node, 0)
        degrees[node] = e_deg + i_deg + o_deg

    min_deg = min(degrees.values()) if degrees else 0
    max_deg = max(degrees.values()) if degrees else 0

    return min_deg, max_deg


def betweenness_centrality(graph, dist, pred, index):
    betweenness = defaultdict(int)
    nodes = list(graph.vertices)
    index_node = {v: k for k, v in index.items()}  # Mapeia índices para nomes
    
    for s in range(len(nodes)):
        for t in range(len(nodes)):
            if s == t or dist[s][t] == float('inf'):
                continue
            
            # Reconstrói o caminho mais curto
            current = t
            path = []
            while current != s:
                path.append(index_node[current])
                current = pred[s][current]  # Usa matriz de predecessores
                if current is None:
                    break
            path.append(index_node[s])
            path = path[::-1]  # Inverte o caminho
            
            # Contabiliza nós intermediários
            for node in path[1:-1]:
                betweenness[node] += 1
    
    return betweenness


def average_path_length(dist, n):
    total = 0
    count = 0
    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] != float('inf'):
                total += dist[i][j]
                count += 1
    return total / count if count else 0


def diameter(dist, n):
    max_dist = 0
    for i in range(n):
        for j in range(n):
            if dist[i][j] != float('inf'):
                max_dist = max(max_dist, dist[i][j])
    return max_dist


def compute_statistics(graph):
    dist, pred, index = floyd_warshall(graph)
    n = len(graph.vertices)
    stats = {
        'vertices': len(graph.vertices),
        'edges': len(graph.edges),
        'arcs': len(graph.arcs),
        'required_vertices': len(graph.required_vertices),
        'required_edges': len(graph.required_edges),
        'required_arcs': len(graph.required_arcs),
        'density': (len(graph.edges) + len(graph.arcs)) / (len(graph.vertices) * (len(graph.vertices) - 1)) if len(graph.vertices) > 1 else 0,
        'connected_components': connected_components(graph),
        'min_degree': calculate_degrees(graph)[0],
        'max_degree': calculate_degrees(graph)[1],
        'average_path_length': average_path_length(dist, n),
        'diameter': diameter(dist, n)
    }
    betweenness = betweenness_centrality(graph, dist, pred, index)
    stats['betweenness'] = betweenness
    return stats
