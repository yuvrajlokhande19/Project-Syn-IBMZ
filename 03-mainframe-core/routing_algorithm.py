import heapq
import json

class NagpurHospitalRouter:
    """
    Deterministic routing algorithm (Dijkstra's) to find the safest 
    ambulance corridor when an anomaly (like a flood) is detected.
    """
    def __init__(self):
        # Weighted Graph representing distance/time between hospital nodes
        self.graph = {
            "GMC_Nagpur": {"Mayo_Hospital": 5, "AIIMS_Nagpur": 12, "Wockhardt_Hospital": 7},
            "Mayo_Hospital": {"GMC_Nagpur": 5, "Wockhardt_Hospital": 4, "Lata_Mangeshkar_Hospital": 15},
            "AIIMS_Nagpur": {"GMC_Nagpur": 12, "Lata_Mangeshkar_Hospital": 10},
            "Lata_Mangeshkar_Hospital": {"Mayo_Hospital": 15, "AIIMS_Nagpur": 10, "Wockhardt_Hospital": 8},
            "Wockhardt_Hospital": {"GMC_Nagpur": 7, "Mayo_Hospital": 4, "Lata_Mangeshkar_Hospital": 8}
        }

    def update_weights(self, flooded_location: str, penalty: int = 999):
        """Massively increases the weight of routes connected to a flooded location."""
        print(f"[ALGORITHM] Applying flood penalty ({penalty}) to routes near {flooded_location}")
        for node in self.graph:
            if flooded_location in self.graph[node]:
                self.graph[node][flooded_location] += penalty
        
        # Also penalize outgoing routes from the flood
        if flooded_location in self.graph:
            for neighbor in self.graph[flooded_location]:
                self.graph[flooded_location][neighbor] += penalty

    def dijkstra(self, start: str, target: str):
        """Standard Dijkstra's Shortest Path Algorithm"""
        distances = {node: float('infinity') for node in self.graph}
        distances[start] = 0
        priority_queue = [(0, start)]
        previous_nodes = {node: None for node in self.graph}

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.graph[current_node].items():
                distance = current_distance + weight

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))

        # Reconstruct path
        path, current_node = [], target
        while current_node is not None:
            path.append(current_node)
            current_node = previous_nodes[current_node]
        path.reverse()

        return path, distances[target]

if __name__ == "__main__":
    router = NagpurHospitalRouter()
    print("Normal Routing (AIIMS to Mayo):")
    path, cost = router.dijkstra("AIIMS_Nagpur", "Mayo_Hospital")
    print(f"Path: {' -> '.join(path)}, Cost: {cost}")
    
    print("\nSimulating Flood at GMC_Nagpur...")
    router.update_weights("GMC_Nagpur")
    
    print("Rerouting (AIIMS to Mayo) avoiding Flood:")
    path, cost = router.dijkstra("AIIMS_Nagpur", "Mayo_Hospital")
    print(f"Path: {' -> '.join(path)}, Cost: {cost}")
