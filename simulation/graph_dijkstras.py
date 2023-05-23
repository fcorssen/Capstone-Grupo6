import itertools

class Graph():
 
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0 for column in range(vertices)]
                      for row in range(vertices)]
        self.coords = [(0,0) for i in range(vertices)]
 
    def printSolution(self, dist):
        print(self.graph)
        print("Vertex \t Distance from Source")
        for node in range(self.V):
            print(node, "\t\t", dist[node])
    
    def minDistance(self, dist, sptSet):
        min = 1e7

        for v in range(self.V):
            if dist[v] < min and sptSet[v] == False:
                min = dist[v]
                min_index = v
 
        return min_index

    def calculate_distance(self, path):
        distance = 0
        for i in range(len(path)-1):
            distance += self.distance(self.coords[path[i]], self.coords[path[i+1]])
        return distance
    
    def distance(self, coord1, coord2):
        return ((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)**0.5
    
    def dijkstra(self, src, nodes):
        # generar todas las permutaciones de los nodos
        permutations = list(itertools.permutations(nodes))
        min_distance = 1e7
        min_path = []

        # para cada permutación
        for perm in permutations:
            # agregar el nodo origen al inicio y al final de la permutación
            path = [src] + list(perm) + [src]
            # calcular la distancia total de la permutación
            distance = self.calculate_distance(path)
            # actualizar la distancia mínima y la permutación mínima
            if distance < min_distance:
                min_distance = distance
                min_path = path

        # imprimir la distancia mínima y la permutación mínima
        print("Distancia mínima:", min_distance)
        print("Permutación mínima:", min_path)