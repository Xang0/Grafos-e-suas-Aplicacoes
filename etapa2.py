import sys
import time
from grafo import read_graph

class Service:
    def __init__(self, sid, u, v, demand, cost):
        self.id = sid
        self.u = u
        self.v = v
        self.demand = demand
        self.cost = cost


def parse_services(filename):
    services = []
    travel_segments = []      # List to collect (u,v,cost) for all edges/arcs
    capacity = None
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
            # Section headers for non-required edges/arcs:
            if parts[0].upper() == 'EDGE':
                current_section = 'edges'
                skip_header = True
                continue
            if parts[0].upper() == 'ARC':
                current_section = 'arcs'
                skip_header = True
                continue
            # Parse non-required edges (bidirectional) costs:
            if current_section == 'edges':
                u = parts[1]; v = parts[2]; cost = int(parts[3])
                travel_segments.append((u, v, cost))
                travel_segments.append((v, u, cost))
                continue
            # Parse non-required arcs (one-way) costs:
            if current_section == 'arcs':
                u = parts[1]; v = parts[2]; cost = int(parts[3])
                travel_segments.append((u, v, cost))
                continue
            # Parse capacity line:
            if parts[0] == 'Capacity:':
                capacity = int(parts[1])
                continue
            # Parse service lines (ReN, ReE, ReA):
            if parts[0][0] in ('N', 'E', 'A') and parts[0][1:].isdigit():
                kind = parts[0][0]
                sid = int(parts[0][1:])
                if kind == 'N': 
                    # Required node service (no travel cost to itself)
                    u = v = parts[1]
                    demand = int(parts[2])
                    cost = int(parts[3]) if len(parts) > 3 else 0
                else:
                    # Required edge or arc service
                    u, v = parts[1], parts[2]
                    demand = int(parts[4])
                    cost = int(parts[5])
                    # Add travel segments for this required service
                    travel_segments.append((u, v, cost))
                    if kind == 'E':
                        # If it's an edge, also allow travel in reverse direction
                        travel_segments.append((v, u, cost))
                services.append(Service(sid, u, v, demand, cost))
                continue
    return services, capacity, travel_segments


def clarke_wright(graph, services, capacity, dist, idx):
    depot = graph.depot
    routes = []
    route_id_map = {}  # Map service ID → index in routes list

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
        # try four merge orientations
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
            i_u = index[u]
            i_v = index[v]
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


def format_solution(routes, start_clock, end_clock, dist, idx, services_map, graph):
    depot = graph.depot
    lines = []
    total_cost = 0
    formatted_routes = []

    for ids in routes:
        load = sum(services_map[i].demand for i in ids)
        segs = []

        current = depot
        # Start at depot
        segs.append((0, 'D', 0, depot, depot))

        for sid in ids:
            svc = services_map[sid]

            # Deadhead to the start of the service
            if current != svc.u:
                d = dist[idx[current]][idx[svc.u]]
                total_cost += d
                segs.append((d, 'D', 0, current, svc.u))

            # Service execution
            total_cost += svc.cost
            segs.append((0, 'S', sid, svc.u, svc.v))

            current = svc.v

        # Return to depot
        if current != depot:
            d_back = dist[idx[current]][idx[depot]]
            total_cost += d_back
            segs.append((d_back, 'D', 0, current, depot))

        formatted_routes.append((load, segs))

    # Header
    out = [str(total_cost), str(len(formatted_routes)), str(start_clock), str(end_clock), '']

    # Body
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

if __name__ == '__main__':
    graph = read_graph('BHW1.dat')
    # Explicitly set depot and remove it from required vertices
    with open('BHW1.dat') as f:
        for line in f:
            if line.startswith('Depot Node:'):
                graph.depot = line.split()[-1]
                break
    graph.required_vertices.discard(graph.depot)
    services, capacity, travel_segments = parse_services('BHW1.dat')
    dist, pred, idx = floyd_warshall(graph, travel_segments)
    services_map = {s.id: s for s in services}
    start_clock = time.process_time()
    routes = clarke_wright(graph, services, capacity, dist, idx)
    end_clock = time.process_time()
    
    arquivo = open("sol_BHW1.dat", "w")
    arquivo.write(format_solution(routes, start_clock, end_clock, dist, idx, services_map, graph))
    arquivo.close()
