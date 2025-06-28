
import random
from copy import deepcopy

def calculate_route_cost(route_ids, services_map, dist, idx, depot):
    total_cost = 0
    current = depot
    for sid in route_ids:
        svc = services_map[sid]
        if current != svc.u:
            total_cost += dist[idx[current]][idx[svc.u]]
        total_cost += svc.cost
        current = svc.v
    if current != depot:
        total_cost += dist[idx[current]][idx[depot]]
    return total_cost

def two_opt(route_ids, services_map, dist, idx, depot):
    best = route_ids[:]
    best_cost = calculate_route_cost(best, services_map, dist, idx, depot)
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 1):
            for j in range(i + 1, len(best)):
                new_route = best[:i] + best[i:j+1][::-1] + best[j+1:]
                new_cost = calculate_route_cost(new_route, services_map, dist, idx, depot)
                if new_cost < best_cost:
                    best = new_route
                    best_cost = new_cost
                    improved = True
                    break
            if improved:
                break
    return best, best_cost

def relocate(routes, services_map, capacity, dist, idx, depot):
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j:
                    continue
                for sid in routes[i]:
                    demand = services_map[sid].demand
                    if sum(services_map[s].demand for s in routes[j]) + demand <= capacity:
                        new_route_i = routes[i][:]
                        new_route_j = routes[j][:]
                        new_route_i.remove(sid)
                        new_route_j.append(sid)
                        if not new_route_i:
                            continue
                        old_cost = calculate_route_cost(routes[i], services_map, dist, idx, depot) +                                    calculate_route_cost(routes[j], services_map, dist, idx, depot)
                        new_cost = calculate_route_cost(new_route_i, services_map, dist, idx, depot) +                                    calculate_route_cost(new_route_j, services_map, dist, idx, depot)
                        if new_cost < old_cost:
                            routes[i] = new_route_i
                            routes[j] = new_route_j
                            improved = True
                            break
                if improved:
                    break
            if improved:
                break
    return routes
