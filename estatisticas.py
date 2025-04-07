from collections import defaultdict, deque

def floyd_warshall(graph):
    nodes = list(graph.vertices)
    n = len(nodes)
    index = {node: i for i, node in enumerate(nodes)}
    dist = [[float('inf')] * n for _ in range(n)]
    pred = [[None] * n for _ in range(n)]
    
    for i in range(n):
        dist[i][i] = 0
    
    for u, v in graph.edges:
        i_u, i_v = index[u], index[v]
        if dist[i_u][i_v] > 1:
            dist[i_u][i_v] = 1
            pred[i_u][i_v] = i_u
        if dist[i_v][i_u] > 1:
            dist[i_v][i_u] = 1
            pred[i_v][i_u] = i_v
    
    for u, v in graph.arcs:
        i_u, i_v = index[u], index[v]
        if dist[i_u][i_v] > 1:
            dist[i_u][i_v] = 1
            pred[i_u][i_v] = i_u
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    pred[i][j] = pred[k][j]
    
    return dist, pred, index


def connected_components(graph):
    adjacency = defaultdict(list)
    for u, v in graph.edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    for u, v in graph.arcs:
        adjacency[u].append(v)
        adjacency[v].append(u)
    visited = set()
    components = []
    for node in graph.vertices:
        if node not in visited:
            queue = deque([node])
            visited.add(node)
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
    edge_counts = defaultdict(int)
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    for u, v in graph.edges:
        edge_counts[u] += 1
        edge_counts[v] += 1
    for u, v in graph.arcs:
        out_degree[u] += 1
        in_degree[v] += 1
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
    index_node = {v: k for k, v in index.items()}
    n = len(nodes)
    for s in range(n):
        for t in range(n):
            if s == t or dist[s][t] == float('inf'):
                continue
            current = t
            path = []
            while current != s:
                path.append(index_node[current])
                current = pred[s][current]
                if current is None:
                    break
            path.append(index_node[s])
            path = path[::-1]
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
