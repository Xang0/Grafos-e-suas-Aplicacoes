
import time
from grafo import read_graph
from etapa2_refatorado import parse_services, floyd_warshall, clarke_wright, format_solution
from melhoria import two_opt, relocate

def solve_with_improvement(instance_path):
    graph = read_graph(instance_path)
    with open(instance_path) as f:
        for line in f:
            if line.startswith('Depot Node:'):
                graph.depot = line.split()[-1]
                break
    graph.required_vertices.discard(graph.depot)

    services, capacity, travel_segments = parse_services(instance_path)
    dist, pred, idx = floyd_warshall(graph, travel_segments)
    services_map = {s.id: s for s in services}

    # Solução inicial (Clarke & Wright)
    routes = clarke_wright(graph, services, capacity, dist, idx)

    # Aplicação de melhorias
    # 1. 2-opt dentro de cada rota
    for i in range(len(routes)):
        improved_route, _ = two_opt(routes[i], services_map, dist, idx, graph.depot)
        routes[i] = improved_route

    # 2. Realocação entre rotas
    routes = relocate(routes, services_map, capacity, dist, idx, graph.depot)

    start_clock = time.process_time()
    end_clock = time.process_time()  # Só marca o tempo das melhorias aqui
    return format_solution(routes, start_clock, end_clock, dist, idx, services_map, graph)

def main():
    instance_path = "BHW1.dat"
    output_path = "sol-BHW1-melhorado.dat"
    solution = solve_with_improvement(instance_path)
    with open(output_path, "w") as f:
        f.write(solution)

if __name__ == "__main__":
    main()
