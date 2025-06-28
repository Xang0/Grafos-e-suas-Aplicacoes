import os
import time
import re

INPUT_DIR = 'instancias'
OUTPUT_DIR = 'solucoes'

class Graph:
    def __init__(self):
        self.vertices = set()
        self.edges = []
        self.depot = None

class Service:
    def __init__(self, sid, u, v, demand, cost):
        self.id = sid
        self.u = u
        self.v = v
        self.demand = demand
        self.cost = cost

def read_graph(filepath):
    graph = Graph()
    with open(filepath, 'r') as file:
        for line in file:
            if line.strip().lower().startswith('depot node:'):
                graph.depot = int(line.strip().split()[-1])
            elif re.match(r'\d+', line.strip()):
                tokens = re.split(r'\s+', line.strip())
                try:
                    u = int(tokens[0])
                    v = int(tokens[1])
                    graph.vertices.update([u, v])
                    graph.edges.append((u, v))
                except:
                    continue
    return graph

def parse_dat_file(filepath):
    edges = []
    services = []
    capacity = None
    sid = 1

    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if 'CAPACITY' in line.upper():
                parts = re.findall(r'\d+', line)
                if parts:
                    capacity = int(parts[0])
            if re.search(r'FROM|TO|COST|DEMAND|EDGE|ReE.|ReA.|ARC', line, re.IGNORECASE):
                continue
            try:
                tokens = re.split(r'\s+', line)
                values = [float(tok) if '.' in tok else int(tok) for tok in tokens]
                if len(values) >= 4:
                    u, v, cost, demand = values[:4]
                    services.append(Service(sid, int(u), int(v), int(demand), int(cost)))
                    sid += 1
                    edges.append((int(u), int(v), int(cost)))
            except ValueError:
                print(f"⚠️ Linha ignorada (não numérica): {line}")
                continue

    return services, capacity, edges

def floyd_warshall(graph, travel_segments):
    nodes = list(graph.vertices)
    n = len(nodes)
    index = {node: i for i, node in enumerate(nodes)}
    dist = [[float('inf')] * n for _ in range(n)]
    pred = [[None] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, cost in travel_segments:
        if u in index and v in index:
            i_u, i_v = index[u], index[v]
            if cost < dist[i_u][i_v]:
                dist[i_u][i_v] = cost
                pred[i_u][i_v] = i_u
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    pred[i][j] = pred[k][j]
    return dist, pred, index

def clarke_wright(graph, services, capacity, dist, idx):
    depot = graph.depot
    routes = []
    route_id_map = {}
    for s in services:
        route = {'ids': [s.id], 'demand': s.demand, 'start': s.u, 'end': s.v}
        route_id_map[s.id] = len(routes)
        routes.append(route)
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
    for _, i_id, j_id in savings:
        if i_id not in route_id_map or j_id not in route_id_map:
            continue
        ri = routes[route_id_map[i_id]]
        rj = routes[route_id_map[j_id]]
        if ri is rj:
            continue
        can_merge = False
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
    unique_indices = set(route_id_map.values())
    return [routes[i]['ids'] for i in unique_indices]

def format_solution(routes, start_clock, end_clock, dist, idx, services_map, graph):
    depot = graph.depot
    lines = []
    total_cost = 0
    formatted_routes = []
    for ids in routes:
        load = sum(services_map[i].demand for i in ids)
        segs = []
        current = depot
        segs.append((0, 'D', 0, depot, depot))
        for sid in ids:
            svc = services_map[sid]
            if current != svc.u:
                d = dist[idx[current]][idx[svc.u]]
                total_cost += d
                segs.append((d, 'D', 0, current, svc.u))
            total_cost += svc.cost
            segs.append((0, 'S', sid, svc.u, svc.v))
            current = svc.v
        if current != depot:
            d_back = dist[idx[current]][idx[depot]]
            total_cost += d_back
            segs.append((d_back, 'D', 0, current, depot))
        formatted_routes.append((load, segs))
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

def solve(instance_path):
    graph = read_graph(instance_path)
    services, capacity, travel_segments = parse_dat_file(instance_path)
    dist, pred, idx = floyd_warshall(graph, travel_segments)
    services_map = {s.id: s for s in services}
    start_clock = time.process_time()
    routes = clarke_wright(graph, services, capacity, dist, idx)
    end_clock = time.process_time()
    return format_solution(routes, start_clock, end_clock, dist, idx, services_map, graph)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename in os.listdir(INPUT_DIR):
        if not filename.lower().endswith('.dat'):
            continue
        instance_path = os.path.join(INPUT_DIR, filename)
        output_name = f"sol_{os.path.splitext(filename)[0]}.dat"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        try:
            print(f"\n🧪 Processando: {filename}")
            solution = solve(instance_path)
            with open(output_path, "w") as f:
                f.write(solution)
            print(f"✅ Custo salvo em {output_name}")
        except Exception as e:
            print(f"❌ Erro ao processar {filename}: {e}")

    print("\n✅ Todos os testes concluídos.")

if __name__ == "__main__":
    main()