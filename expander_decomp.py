import heapq
import math
import random
from lct import LinkCutTree

'''
graph - adjacency list representation of undirected graph
m - number of edges in graph
D - delta, specifies source flow into each node
sink - specifies sink capacity of each node (leave empty for sink[u] = deg[u])
U - capacity of all edges in the graph
h - maximum label in the push-relabel framework
f - specifies initial flow on each edge (leave empty for 0 flow)
l - specifies initial level of each node (leave empty for level 0)
'''
def unit_flow(graph, m, D, sink, U, h, f, l):

    current = {}
    fnode = {}
    Q = []
    for u in graph:
        if u not in f:
            f[u] = {}
            for v in graph[u]:
                f[u][v] = 0
        if u not in l:
            l[u] = 0
        if u not in S:
            sink[u] = len(graph[u])

        fnode[u] = D[u]
        for v in graph[u]:
            if v in f and u in f[v]:
                fnode[u] += f[v][u]

        current[u] = 0
        if l[u] < h and fnode[u] > S[u]:
            heapq.heappush(Q, (l[u], u))
    
    while len(Q) != 0:
        _lvl, v = Q[0]
        u, lchange = push_relabel(v, graph, current, fnode, sink, U, f, l)
        if u != None:
            if D[v] <= sink[v]:
                heapq.heappop(Q)
            if D[u] > sink[u]:
                heapq.heappush(Q, (l[u], u))
        elif lchange == 1:
            heapq.heappop(Q)
            if l[v] < h:
                heapq.heappush(Q, (l[v], v))

    B = [[] for i in range(h+1)]
    for u in graph:
        B[l[u]].append(u)
    if len(B[h]) == 0 or len(B[0]) == 0:
        return []
    c = 5 * math.log(m) / h 
    vol = 0
    S = []
    for k in range(h, -1, -1):
        S.extend(B[k])
        cnt = 0
        for u in B[k]:
            vol += S[u]
            for v in graph[u]:
                if l[v] == k-1 and f[u][v] < U:
                    cnt += 1
        if cnt <= c * vol:
            return S
 
def push_relabel(v, graph, current, fnode, sink, U, f, l):
    u = graph[v][current[v]]
    if U - f[v][u] > 0 and l[v] == l[u]+1:
        psi = min(fnode[v] - sink[v], U-f[v][u], sink[u])
        f[v][u] += psi
        f[u][v] -= psi 
        fnode[u] += psi 
        fnode[v] -= psi
        return u, 0
    elif current[v]+1 < sink[v]:
        current[v] += 1
        return None, 0
    else:
        current[v] = 0
        l[v] += 1
        return None, 1

def trimming(graph, m, A, phi):
    cur_A = set(A)
    cur_D = {}
    cur_f = {}
    cur_l = {}

    #initialize cur_D
    for u in cur_A:
        cur_D[u] = 0
        for v in graph[u]:
            if v not in cur_A:
                cur_D[u] += 2 / phi 
    
    while True:
        cur_graph = {}
        for u in cur_A:
            cur_graph[u] = []
            for v in graph[u]:
                if v in cur_A:
                    cur_graph[u].append(v)
                else:
                    cur_graph[u].append(u)
        S = unit_flow(cur_graph, m, cur_D, dict(), 2/phi, 40 * math.log(2*m) / phi, cur_f, cur_l)
        if len(S) == 0:
            return list(cur_A)
        for u in S:
            cur_A.remove(u)
        for u in S:
            cur_f.pop(u)
            cur_l.pop(u)
            for v in cur_graph[u]:
                if v in cur_A:
                    cur_f[v].pop(u)
        
def calculate_partition(A, X_E, u):

    A_E = [e for e in X_E if e in A]
    mu = sum([u[e] for e in A_E]) / len(A_E)
    eta, A_L, A_R = -1, [], []
    L = [e for e in A_E if u[e] < mu]
    R = [e for e in A_E if u[e] >= mu]
    L = sorted(L, cmp=lambda i1, i2: u[i1] - u[i2])
    R = sorted(R, cmp=lambda i1, i2: u[i1] - u[i2])
    P_L = sum([(u[e] - mu) ** 2 for e in L])
    P_R = sum([(u[e] - mu) ** 2 for e in R])
    P_A = sum([(u[e] - mu) ** 2 for e in A_E])
    ell = sum([abs(u[e]-e) for e in L])

    if len(L) <= len(R):
        if P_L >= P_A / 20:
            eta = mu 
            A_R = R
            A_L = L[:len(A_E) // 8]
        else:
            eta = mu + 4*ell / len(A_E)
            A_R = [e for e in A_E if u[e] <= eta]
            R2 = [e for e in A_E if u[e] >= mu + 6*ell/len(A_E)]
            R2 = sorted(R2, cmp=lambda e1, e2: u[e1] - u[e2])
            A_L = R2[-(len(A_E)//8):]
    else:
        if P_R >= P_A / 20:
            eta = mu 
            A_R = L
            A_L = R[-(len(A_E)//8):]
        else:
            eta = mu - 4*ell / len(A_E)
            A_R = [e for e in A_E if u[e] >= eta]
            L2 = [e for e in A_E if u[e] <= mu - 6*ell/len(A_E)]
            L2 = sorted(L2, cmp=lambda e1, e2: u[e1] - u[e2])
            A_L = L2[:len(A_E)//8]
    
    return eta, A_L, A_R

def topo_sort(u, graph, f, vis, ord):
    if u in vis:
        return 
    vis.add(u)
    for v in graph[u]:
        if f[u][v] > 0:
            topo_sort(v, graph, f, vis, ord)
    ord.append(u)

def decompose_flow(graph, f, A_L, A_R):
    vis = set()
    ord = []
    for u in A_L:
        topo_sort(u, graph, f, vis, ord)
    ord.reverse()
    topo_index = dict()
    for i in range(len(ord)):
        topo_index[ord[i]] = i

    keys = [u for u in graph] + [-1]
    lct = LinkCutTree(keys)
    for u in A_L:
        lct.link_edge(-1, u, 1)
    
    queue = []
    current = dict()
    for u in graph:
        current[u] = 0
    for i in range(len(ord)):
        if ord[i] not in A_L:
            heapq.heappush(queue, (i, ord[i]))
            current[ord[i]] = 0
    
    matching = []
    while len(queue) > 0:
        (i,u) = queue[0]
        heapq.heappop(queue)
        
        while current[u] < len(graph[u]):
            v = graph[u][current[u]]
            current[u] += 1
            if f[v][u] > 0 and lct.connected(v, -1):
                lct.link_edge(v, u, f[v][u])
                if u in A_R:
                    x_e = lct.next_on_path(-1, u, lct.next_on_path(-1, u, -1))
                    matching.append((x_e, u))
                    lct.update_path(u, -1, -1)
                    root = -1 
                    while lct.mincost(root, u) == 0:
                        cut1, cut2 = lct.get_mincost_edge(root, u)
                        lct.cut_edge(cut1, cut2)
                        if lct.connected(root, cut2):
                            cut1, cut2 = cut2, cut1 
                        heapq.heappush(queue, (topo_index[cut2], cut2))
                        root = cut2
                break
    return matching

def cut_matching(graph, m, phi):
    V = [u for u in graph]
    X_E = []
    edge_index = dict()
    G_E = {}
    key = 0
    while key in graph:
        key += 1
    for u in graph:
        G_E[u] = []
        for v in graph[u]:
            if v in G_E:
                X_E.append(key)
                edge_index[key] = len(X_E) - 1
                G_E[u].append(key)
                G_E[v].append(key)
                G_E[key] = [u, v]
                key += 1
                while key in graph:
                    key += 1
    A = set(V + X_E)
    R = []
    vol_R = 0
    T = math.log(m) ** 2
    t = 1
    c = 1 / (phi * T)
    # generate random unit vector orthogonal to [1,...,1]
    r = [0] * m
    for i in range(m-1):
        r[i] = random.uniform(0,1)
    r[m-1] = -sum(r)
    norm = math.sqrt(sum([x ** 2 for x in r]))
    r = [x / norm for x in r]

    u = {}
    for i in range(m):
        u[X_E[i]] = r[i]

    while vol_R < m / (10 * T) and t <= T:
        eta, A_L, A_R = calculate_partition(A, X_E, u)
        
        h = 1 / (phi * math.log(m))
        sink = dict()
        D = dict()
        G_A = dict()
        for u in A:
            sink[u] = 0
            D[u] = 0
            G_A[u] = [v for v in graph[u] if v in A]
        for u in A_L:
            D[u] = 1
        for u in A_R:
            sink[u] = 1
        f = dict()
        l = dict()
        S = unit_flow(G_A, m, D, sink, c, h, f, l)
        M = decompose_flow(G_A, f, A_L, A_R)
        for (e1, e2) in M:
            avg = (u[e1] + u[e2]) / 2
            u[e1] = avg 
            u[e2] = avg 


def decomp(graph, phi):
    pass


def main():
    keys = [1, 2, 3, 4, 5, 6]
    graph = dict()
    f = dict()
    for key in keys:
        graph[key] = []
        f[key] = dict()

    def add(u, v, x):
        graph[u].append(v)
        graph[v].append(u)
        f[u][v] = x
        f[v][u] = -x
        
    add(1,3,1)
    add(2,3,1)
    add(3,4,2)
    add(4,5,1)
    add(4,6,1)

    A_L = {1,2}
    A_R = {5,6}
    print(decompose_flow(graph, f, A_L, A_R))

if __name__ == "__main__":
    main()