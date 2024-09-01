import heapq
import math
import random
from lct import LinkCutTree


def get_induced_subgraph(graph, A):
    cur_graph = {}
    for u in A:
        cur_graph[u] = []
        for v in graph[u]:
            if v in A:
                cur_graph[u].append(v)
            else:
                cur_graph[u].append(u)
    return cur_graph

def count_edges(graph):
    m = 0
    encountered = set()
    for u in graph:
        encountered.add(u)
        for v in graph[u]:
            if v in encountered:
                m += 1
    return m

'''
graph - adjacency list representation of undirected graph
D - delta, specifies source flow into each node
T - specifies sink capacity of each node (leave empty for T[u] = deg[u])
U - capacity of all edges in the graph
h - maximum label in the push-relabel framework
f - specifies initial flow on each edge (leave empty for 0 flow)
l - specifies initial level of each node (leave empty for level 0)
'''
def unit_flow(graph, D, T, U, h, f, l):
    h = int(math.floor(h))
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
        if u not in T:
            T[u] = len(graph[u])

        fnode[u] = D[u]
        for v in graph[u]:
            if v in f and u in f[v]:
                fnode[u] += f[v][u]

        current[u] = 0
        if l[u] < h and fnode[u] > T[u]:
            heapq.heappush(Q, (l[u], u))
    
    while len(Q) != 0:
        _lvl, v = Q[0]
        u, lchange = push_relabel(v, graph, current, fnode, T, U, f, l)
        if u != None:
            if fnode[v] <= T[v]:
                heapq.heappop(Q)
            if fnode[u] > T[u]:
                heapq.heappush(Q, (l[u], u))
        elif lchange == 1:
            heapq.heappop(Q)
            if l[v] < h:
                heapq.heappush(Q, (l[v], v))
 
def push_relabel(v, graph, current, fnode, T, U, f, l):
    if len(graph[v]) == 0:
        current[v] = 0
        l[v] += 1
        return None, 1
    u = graph[v][current[v]]
    if U - f[v][u] > 0 and l[v] == l[u]+1:
        psi = min(fnode[v] - T[v], U-f[v][u], len(graph[u]))
        f[v][u] += psi
        f[u][v] -= psi 
        fnode[u] += psi 
        fnode[v] -= psi
        return u, 0
    elif current[v]+1 < len(graph[v]):
        current[v] += 1
        return None, 0
    else:
        current[v] = 0
        l[v] += 1
        return None, 1

def retrieve_trim(graph, U, h, f, l):
    h2 = int(math.floor(h))
    B = [[] for _ in range(h2+1)]
    for u in graph:
        B[l[u]].append(u)
    # print("B", B)
    if len(B[h2]) == 0 or len(B[0]) == 0:
        return []
    m = count_edges(graph)
    c = 5 * math.log(m) / h 
    vol = 0
    S = []
    for k in range(h2, -1, -1):
        S.extend(B[k])
        cnt = 0
        for u in B[k]:
            vol += len(graph[u])
            for v in graph[u]:
                if l[v] == k-1 and f[u][v] < U:
                    cnt += 1
        if cnt <= c * vol:
            return S

def trimming(graph, m, A, phi):
    cur_A = A.copy()
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
        cur_graph = get_induced_subgraph(graph, cur_A)
        
        unit_flow(cur_graph, cur_D, dict(), 2/phi, 40 * math.log(2*m) / phi, cur_f, cur_l)
        S = retrieve_trim(cur_graph, 2/phi, 40 * math.log(2*m) / phi, cur_f, cur_l)
        if len(S) == 0:
            return cur_A
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
    L = sorted(L, key = lambda e : u[e])
    R = sorted(R, key = lambda e : u[e])
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
            R2 = sorted(R2, key = lambda e : u[e])
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
            L2 = sorted(L2, key = lambda e : u[e])
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
    lct = LinkCutTree(keys, True)
    for u in A_L:
        lct.link(-1, u, 1)
    
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
                lct.link(v, u, f[v][u])
                if u in A_R:
                    x_e = lct.next_on_path(-1, u)
                    matching.append((x_e, u))
                    lct.update_path(u, -1, -1)
                    root = -1 
                    while lct.path(root, u) == 0:
                        cut1, cut2 = lct.get_mincost_edge(root, u)
                        lct.cut(cut1, cut2)
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
    R = set()
    vol_R = 0
    T = max(1, 3 * math.log(m) ** 2)
    t = 1
    c = 1 / (phi * T)
    # generate random unit vector orthogonal to [1,...,1]
    r = [0] * m
    for i in range(m-1):
        r[i] = random.uniform(-1,1)
    r[m-1] = -sum(r)
    norm = math.sqrt(sum([x ** 2 for x in r]))
    # print(m, r, norm)
    if norm != 0:
        r = [x / norm for x in r]

    u = {}
    for i in range(m):
        u[X_E[i]] = r[i]

    while vol_R < m / (10 * T) and t <= T:
        t += 1
        eta, A_L, A_R = calculate_partition(A, X_E, u)
        
        h = 1 / (phi * max(1, math.log(m)))
        sink = dict()
        D = dict()
        G_A = dict()
        for e in A:
            sink[e] = 0
            D[e] = 0
            G_A[e] = [v for v in G_E[e] if v in A]
        for e in A_L:
            D[e] = 1
        for e in A_R:
            sink[e] = 1
        f = dict()
        l = dict()
        unit_flow(G_A, D, sink, c, h, f, l)
        S = retrieve_trim(G_A, c, h, f, l)
        A_Lset = set(A_L)
        for e in S:
            A.remove(e)
            R.add(e)
            vol_R += len(G_E[e])
            if e in A_Lset:
                A_Lset.remove(e)
        A_L = list(A_Lset)

        M = decompose_flow(G_A, f, A_L, A_R)
        for (e1, e2) in M:
            avg = (u[e1] + u[e2]) / 2
            u[e1] = avg 
            u[e2] = avg 

    for u in X_E:
        if u in A:
            A.remove(u)
        if u in R:
            R.remove(u)
    
    if len(R) == 0:
        return A, R, 1
    elif vol_R >= m / (10 * T):
        return A, R, 2
    else:
        return A, R, 3

def decomp(graph, phi):
    m = count_edges(graph)
    if m <= 1 or phi > 1 / (math.log(m) ** 2):
        return [[u] for u in graph]
    A, R, case = cut_matching(graph, m, phi)
    if case == 1:
        return [list(A)]
    elif case == 2:
        G_A = get_induced_subgraph(graph, A)
        G_R = get_induced_subgraph(graph, R)
        return decomp(G_A, phi) + decomp(G_R, phi)
    else:
        A2 = trimming(graph, m, A, phi)
        R2 = set([u for u in graph if u not in A2])
        G_R = get_induced_subgraph(graph, R2)
        return [list(A2)] + decomp(G_R, phi)

def unit_flow_test():
    trials = 100
    for trial in range(trials):
        n = 100
        m = 200
        keys = [i for i in range(n)]
        graph = dict()
        for key in keys:
            graph[key] = [] 
        edges = set()
        for _edge in range(m):
            while True:
                u = random.randint(0, n-1)
                v = random.randint(0, n-1)
                if u == v or (u,v) in edges:
                    continue 
                graph[u].append(v)
                graph[v].append(u)
                edges.add((u,v))
                edges.add((v,u))
                break
        D = dict()
        T = dict()
        remain = 300
        for key in keys:
            delta = min(remain, random.randint(1,10))
            D[key] = delta
            remain -= delta 
            T[key] = len(graph[key])
        phi = 0.04
        U = 2 / phi 
        h = 40 * math.log(2*m) / phi 
        f = dict() 
        l = dict() 
        unit_flow(graph, D, T, U, h, f, l)
        S = retrieve_trim(graph, U, h, f, l)
        print(S)
        if len(S) == 0:
            for u in graph:
                total = D[u]
                for v in graph[u]:
                    total += f[v][u]
                    if abs(f[v][u]) > U:
                        print("ERROR: too much flow from", v, "to", u)
                        return False
                if total > T[u]:
                    print("ERROR: too much flow at node", u)
                    return False
        else:
            S = set(S)
            vol_S = 0
            for u in S:
                vol_S += len(graph[u])
            total = 0
            for u in S:
                for v in graph[u]:
                    if v not in S and f[u][v] < U:
                        total += 1
            if total > 5 * vol_S * math.log(2*m) / h:
                print("ERROR: too many unsaturated edges leaving S")
                return False
        print("trial", trial, "successful!")

def generate_subsets(keys):
    if len(keys) == 0:
        return [[]]
    res = generate_subsets(keys[1:])
    ans = res.copy()
    for subset in res:
        ans.append(subset + [keys[0]])
    return ans

def calculate_phi(graph):
    subsets = generate_subsets([u for u in graph])
    ans = 1
    for subset in subsets:
        subset = set(subset)
        vol = min(sum([len(graph[u]) for u in graph if u in subset]), sum([len(graph[u]) for u in graph if u not in subset]))
        cut = sum([sum([1 for v in graph[u] if v not in subset]) for u in subset])
        if vol != 0:
            ans = min(ans, cut / vol)
    return ans

def expander_decomp_test():
    trials = 100
    errors = 0
    successes = 0
    for trial in range(trials):
        n = 300
        m = 600
        keys = [i for i in range(n)]
        graph = dict()
        for key in keys:
            graph[key] = [] 
        edges = set()
        for _edge in range(m):
            while True:
                u = random.randint(0, n-1)
                v = random.randint(0, n-1)
                if u == v or (u,v) in edges:
                    continue 
                graph[u].append(v)
                graph[v].append(u)
                edges.add((u,v))
                edges.add((v,u))
                break
        phi = 0.02
        V = decomp(graph, phi)
        label = dict()
        k = len(V)
        for i in range(k):
            for u in V[i]:
                label[u] = i
        cut = 0
        for u in graph:
            for v in graph[u]:
                if label[u] != label[v]:
                    cut += 1
        print(phi * m * (math.log(m)**3), cut)
        for i in range(k):
            V_i = set(V[i])
            graph_i = get_induced_subgraph(graph, V_i)
            m_i = count_edges(graph_i)
            success = False 
            for _ in range(20):
                A, R, case = cut_matching(graph_i, m_i, phi)
                if case == 1:
                    success = True 
                    break 
            if not success:
                print("ERROR")
                errors += 1
                print(V_i)
                # print(graph_i)
                # A, R, case = cut_matching(graph_i, m_i, phi)
                # print(A, R, case)
            else:
                successes += 1
    print("Tests conclude with", errors, "errors and", successes, "successes")
        

def main():
    # random.seed(0)
    unit_flow_test()
    expander_decomp_test()
    # keys = [1, 2, 3, 4, 5, 6]
    # graph = dict()
    # f = dict()
    # D = dict()
    # T = dict()
    # for key in keys:
    #     graph[key] = []
    #     f[key] = dict()
    #     D[key] = 0
    #     T[key] = 0

    # def add(u, v, x):
    #     graph[u].append(v)
    #     graph[v].append(u)
    #     f[u][v] = x
    #     f[v][u] = -x
        
    # add(1,3,1)
    # add(2,3,1)
    # add(3,4,2)
    # add(4,5,1)
    # add(4,6,1)
    # D[1] = 1
    # D[2] = 1
    # T[5] = 1
    # T[6] = 1
    # print(graph)

    # print(decomp(graph, 0.3))

    # A_L = {2}
    # A_R = {5,6}
    # print(decompose_flow(graph, f, A_L, A_R))

if __name__ == "__main__":
    main()