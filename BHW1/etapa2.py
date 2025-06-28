import time
from grafo import read_graph

# Classe que representa um serviço (aresta, arco ou nó que precisa ser visitado)
class Service:
    def __init__(self, sid, u, v, demand, cost):
        self.id = sid        # ID do serviço
        self.u = u           # Nó de origem
        self.v = v           # Nó de destino
        self.demand = demand  # Demanda do serviço
        self.cost = cost      # Custo de executar o serviço

# Lê os serviços obrigatórios e segmentos de viagem da instância
def parse_services(filename):
    services = []
    travel_segments = []  # trechos entre nós com custos de viagem (para Floyd-Warshall)
    capacity = None       # capacidade dos veículos
    current_section = None
    skip_header = False
    with open(filename) as f:
        for line in f:
            parts = line.strip().split()
            if not parts or parts[0].startswith('#') or parts[0].startswith('the'):
                continue
            if skip_header:
                skip_header = False
                continue

            # Identifica a seção atual do arquivo
            if parts[0].upper() == 'EDGE':
                current_section = 'edges'
                skip_header = True
                continue
            if parts[0].upper() == 'ARC':
                current_section = 'arcs'
                skip_header = True
                continue

            # Arestas não obrigatórias (bidirecionais)
            if current_section == 'edges':
                u, v, cost = parts[1], parts[2], int(parts[3])
                travel_segments.append((u, v, cost))
                travel_segments.append((v, u, cost))
                continue

            # Arcos não obrigatórios (unidirecionais)
            if current_section == 'arcs':
                u, v, cost = parts[1], parts[2], int(parts[3])
                travel_segments.append((u, v, cost))
                continue

            # Capacidade do veículo
            if parts[0] == 'Capacity:':
                capacity = int(parts[1])
                continue

            # Serviços obrigatórios: nós, arestas e arcos
            if parts[0][0] in ('N', 'E', 'A') and parts[0][1:].isdigit():
                kind = parts[0][0]  # tipo do serviço
                sid = int(parts[0][1:])
                if kind == 'N':
                    u = v = parts[1]
                    demand = int(parts[2])
                    cost = int(parts[3]) if len(parts) > 3 else 0
                else:
                    u, v = parts[1], parts[2]
                    demand = int(parts[4])
                    cost = int(parts[5])
                    travel_segments.append((u, v, cost))
                    if kind == 'E':
                        travel_segments.append((v, u, cost))
                services.append(Service(sid, u, v, demand, cost))
                continue

    return services, capacity, travel_segments

# Algoritmo de Floyd-Warshall para caminhos mínimos entre todos os pares
def floyd_warshall(graph, travel_segments):
    nodes = list(graph.vertices)
    n = len(nodes)
    index = {node: i for i, node in enumerate(nodes)}  # mapeamento nó → índice
    dist = [[float('inf')] * n for _ in range(n)]
    pred = [[None] * n for _ in range(n)]

    # Distância para si mesmo é 0
    for i in range(n):
        dist[i][i] = 0

    # Carrega os segmentos de viagem
    for u, v, cost in travel_segments:
        if u in index and v in index:
            i_u = index[u]
            i_v = index[v]
            if cost < dist[i_u][i_v]:
                dist[i_u][i_v] = cost
                pred[i_u][i_v] = i_u

    # Atualiza distâncias via vértices intermediários
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    pred[i][j] = pred[k][j]

    return dist, pred, index

# Heurística de Clarke & Wright (Savings) para construção de rotas
def clarke_wright(graph, services, capacity, dist, idx):
    depot = graph.depot
    routes = []
    route_id_map = {}

    # Inicializa cada serviço como uma rota individual
    for s in services:
        route = {'ids': [s.id], 'demand': s.demand, 'start': s.u, 'end': s.v}
        route_id_map[s.id] = len(routes)
        routes.append(route)

    # Calcula a "economia" ao juntar dois serviços
    savings = []
    for i in services:
        for j in services:
            if i.id >= j.id:
                continue
            d0i = dist[idx[depot]][idx[i.u]]
            d0j = dist[idx[depot]][idx[j.u]]
            dij = dist[idx[i.u]][idx[j.u]]
            s_val = d0i + d0j - dij
            savings.append((s_val, i.id, j.id))
    savings.sort(reverse=True)

    # Tenta combinar rotas com base nas maiores economias
    for _, i_id, j_id in savings:
        if i_id not in route_id_map or j_id not in route_id_map:
            continue
        ri = routes[route_id_map[i_id]]
        rj = routes[route_id_map[j_id]]
        if ri is rj:
            continue
        can_merge = False
        # Verifica orientações possíveis de fusão
        if ri['end'] == rj['start']:
            new_ids = ri['ids'] + rj['ids']
            new_start, new_end = ri['start'], rj['end']
            can_merge = True
        elif rj['end'] == ri['start']:
            new_ids = rj['ids'] + ri['ids']
            new_start, new_end = rj['start'], ri['end']
            can_merge = True
        elif ri['end'] == rj['end']:
            new_ids = ri['ids'] + rj['ids'][::-1]
            new_start, new_end = ri['start'], rj['start']
            can_merge = True
        elif ri['start'] == rj['start']:
            new_ids = ri['ids'][::-1] + rj['ids']
            new_start, new_end = ri['end'], rj['end']
            can_merge = True

        # Só combina se respeitar capacidade
        if can_merge and ri['demand'] + rj['demand'] <= capacity:
            new_route = {
                'ids': new_ids,
                'demand': ri['demand'] + rj['demand'],
                'start': new_start,
                'end': new_end
            }
            new_index = len(routes)
            routes.append(new_route)
            for sid in ri['ids'] + rj['ids']:
                route_id_map[sid] = new_index

    # Remove rotas duplicadas
    unique_indices = set(route_id_map.values())
    return [routes[i]['ids'] for i in unique_indices]

# Formata a solução final em texto, no padrão exigido
def format_solution(routes, start_clock, end_clock, dist, idx, services_map, graph):
    depot = graph.depot
    total_cost = 0
    formatted_routes = []

    # Monta cada rota com segmentos e custos
    for ids in routes:
        load = sum(services_map[i].demand for i in ids)
        segs = []
        current = depot
        segs.append((0, 'D', 0, depot, depot))  # partida do depósito
        for sid in ids:
            svc = services_map[sid]
            if current != svc.u:
                d = dist[idx[current]][idx[svc.u]]
                total_cost += d
                segs.append((d, 'D', 0, current, svc.u))  # deslocamento
            total_cost += svc.cost
            segs.append((0, 'S', sid, svc.u, svc.v))  # execução do serviço
            current = svc.v
        if current != depot:
            d_back = dist[idx[current]][idx[depot]]
            total_cost += d_back
            segs.append((d_back, 'D', 0, current, depot))  # retorno ao depósito
        formatted_routes.append((load, segs))

    # Constrói a saída no formato esperado
    out = [str(total_cost), str(len(formatted_routes)), str(start_clock), str(end_clock), '']
    for idx_r, (load, segs) in enumerate(formatted_routes, start=1):
        visits = len(segs)
        route_cost = sum(
            (d if t == 'D' else 0) + (services_map[s].cost if t == 'S' else 0)
            for d, t, s, _, _ in segs
        )
        trip = ' '.join(
            f"({'D' if t == 'D' else 'S'} {s},{u},{v})"
            for d, t, s, u, v in segs
        )
        out.append(f"0 1 {idx_r} {load} {route_cost} {visits} {trip}")

    return '\n'.join(out)

# Função principal de resolução
def solve(instance_path):
    graph = read_graph(instance_path)
    # Extrai o depósito da instância
    with open(instance_path) as f:
        for line in f:
            if line.startswith('Depot Node:'):
                graph.depot = line.split()[-1]
                break
    graph.required_vertices.discard(graph.depot)

    # Resolve a instância
    services, capacity, travel_segments = parse_services(instance_path)
    dist, pred, idx = floyd_warshall(graph, travel_segments)
    services_map = {s.id: s for s in services}
    start_clock = time.process_time()
    routes = clarke_wright(graph, services, capacity, dist, idx)
    end_clock = time.process_time()

    # Retorna a solução formatada
    return format_solution(routes, start_clock, end_clock, dist, idx, services_map, graph)

# Função main (entrada do script)
def main():
    instance_path = "BHW1.dat"
    output_path = "sol_BHW1.dat"
    solution = solve(instance_path)
    with open(output_path, "w") as f:
        f.write(solution)

# Executa se for chamado diretamente
if __name__ == "__main__":
    main()
