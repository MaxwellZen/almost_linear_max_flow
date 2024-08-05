from collections import deque

class ESTree:
    def __init__(self, graph, source, threshold):
        self.graph = graph
        self.threshold = threshold
        self.source = source
        self.level = {source: 0}

        # BFS: initialize level (aka distance) of each node
        q = deque()
        q.append(source)
        while len(q) != 0:
            u = q.popleft()
            for nb in self.graph[u]:
                if nb not in self.level and self.level[u] < threshold:
                    self.level[nb] = self.level[u]+1
                    q.append(nb)

        # three types of edges:
        #     alpha: points to layer i-1
        #     beta: points to layer i
        #     gamma: points to layer i+1
        self.alpha = {}
        self.beta = {}
        self.gamma = {}
        for u in self.graph:
            self.alpha[u] = []
            self.beta[u] = []
            self.gamma[u] = []
            for nb in self.graph[u]:
                if self.level[nb] == self.level[u] - 1:
                    self.alpha[u].append(nb)
                elif self.level[nb] == self.level[u]:
                    self.beta[u].append(nb)
                else:
                    self.gamma[u].append(nb)

    def delete(self, u, v):
        self.graph[u].remove(v)
        self.graph[v].remove(u)
        if self.level[u] < self.level[v]:
            u,v = v,u 
        q = deque()
        if self.level[u] > self.level[v]:
            self.alpha[u].remove(v)
            self.gamma[v].remove(u)
            if len(self.alpha[u]) == 0:
                q.append(u)
        else:
            self.beta[u].remove(v)
            self.beta(v).remove(u)

        while len(q) != 0:
            node = q.popleft()
            self.level[node] += 1
            for nb in self.beta[node]:
                self.beta[nb].remove(node)
                self.gamma[nb].append(node)
            self.alpha[node] = self.beta[node]
            for nb in self.gamma[node]:
                self.alpha[nb].remove(node)
                self.beta[nb].append(node)
                if len(self.alpha[nb]) == 0:
                    q.append(nb)
            self.beta[node] = self.gamma[node]
            self.gamma[node] = []
            if len(self.alpha[node]) == 0:
                q.append(node)


    # def path_to_root(self, u):
    #     ans = [u]
    #     while u != self.source:
    #         u = self.alpha[u][0]
    #         ans.append(u)
    #     return ans

    def lca(self, u, v):
        if self.level[u] < self.level[v]:
            u, v = v, u
        while self.level[u] > self.level[v]:
            u = self.alpha[u][0]
        while u != v:
            u = self.alpha[u][0]
            v = self.alpha[v][0]
        return u

    def path(self, u, v):
        w = self.lca(u,v)
        patha = [u]
        pathb = []
        while u != w:
            u = self.alpha[u][0]
            patha.append(u)
        while v != w:
            pathb.append(v)
            v = self.alpha[v][0]
        return patha + pathb[::-1]
    

def main():
    graph = {0 : [1,2], 1 : [0,2], 2 : [0,1]}
    estree = ESTree(graph, 0, 5)
    print(estree.level)
    print(estree.path(1,2))
    estree.delete(0,2)
    print(estree.level)
    print(estree.path(1,2))

if __name__ == "__main__":
    main()