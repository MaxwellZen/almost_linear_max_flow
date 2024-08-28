from collections import deque
import random

'''
Guidance taken from C++ implementations by https://usaco.guide/adv/link-cut-tree?lang=cpp and https://codeforces.com/blog/entry/75885
Note: This dynamic tree implements path minimum queries with addition along a path
      Another dynamic tree with different operations can be implemented by using a different Node class for the LinkCutTree structure
      However, get_mincost_node and get_mincost_edge only work correctly for minimum queries, and can be reimplemented for other trees
'''
class Node:
    # intialize with key
    def __init__(self, key):
        self.key = key
        self.left = None 
        self.right = None 
        self.parent = None 
        self.reverse = False 
        self.val = None 
        self.path = None 
        self.update = 0
    
    # propagation of tree reversal to children
    def push(self):
        # push reversal down
        if self.reverse:
            self.reverse = False 
            self.left, self.right = self.right, self.left 
            if self.left != None: self.left.reverse = not self.left.reverse 
            if self.right != None: self.right.reverse = not self.right.reverse
        # push updates down
        if self.update != 0:
            if self.val != None: self.val += self.update 
            if self.path != None: self.path += self.update 
            if self.left != None: self.left.update += self.update 
            if self.right != None: self.right.update += self.update 
            self.update = 0
    
    # currently set to calculate minimum along a path (can be changed to maximum, or something similar)
    def comb(self, a, b):
        if a == None: return b 
        if b == None: return a
        return min(a, b)

    # recalculates path value at current node
    def pull(self):
        self.path = self.val
        if self.left != None: 
            self.left.push()
            self.path = self.comb(self.path, self.left.path)
        if self.right != None: 
            self.right.push()
            self.path = self.comb(self.path, self.right.path)
    
    # whether this node is the root of its tree
    def is_root(self):
        return self.parent == None or (self.parent.left != self and self.parent.right != self)
    
    # used for debugging
    def output(self):
        out = str(self.key) + " "
        if self.left != None: out += "left: " + str(self.left.key) + " "
        else: out += "left: None "

        if self.right != None: out += "right: " + str(self.right.key) + " "
        else: out += "right: None "

        if self.parent != None: out += "parent: " + str(self.parent.key) + " "
        else: out += "parent: None "

        out += "rev, val, path, update: " + str(self.reverse) + " " + str(self.val) + " " + str(self.path) + " " + str(self.update)

        print(out)
    

'''
LinkCutTree operations:
    - LinkCutTree(keys, edgevals): initializes a dynamic tree with the given keys as nodes (keys can be a list or a set)
        - edgevals is True if edges will be assigned values, else False if nodes will be assigned values
    - link(u, v, x = None): creates an edge between u and v with value x if u and v are not already connected
        - x only gets used if edges are assigned values, else it gets ignored
        - returns True if the operation is successful, False otherwise
    - cut(u,v): cuts the edge between u and v if there is already an edge between them
        - returns True if the operation is successful, False otherwise
    - connected(u, v): returns True if u and v are connected, False otherwise
    - path(u,v): returns the minimum along the path from u to v
        - returns None if u and v aren't connected or if there are no initialized values along the path
    - set_node(u,x): sets the value on node u to x
        - returns True if the operation is successful, False otherwise
    - set_edge(u,v,x): sets the value on the u-v edge to x
        - returns True if the operation is successful, False otherwise
    - update_path(u,v,x): adds x to all nodes on the path from u to v
        - returns True if the operation is successful, False otherwise
    - next_on_path(u,v): returns the node after u on the path from u to v
        - returns None if u and v aren't connected
    - get_mincost_node(u,v) / get_mincost_edge(u,v): returns the node/edge closest to u with the minimum value on the path from u to v
        - returns None if u and v aren't connected, or if there are no values on the path from u to v
'''
class LinkCutTree:
    # initialize with labels of all nodes involved
    # edgevals: whether nodes or edges are assigned values
    def __init__(self, keys, edgevals):
        self.nodes = {}
        for key in keys:
            self.nodes[key] = Node(key)
        self.nxt_key = 0
        while self.nxt_key in self.nodes:
            self.nxt_key += 1
        self.edge_nodes = {}
        self.edges = {}
        self.edgevals = edgevals

    # rotate node c up in the tree
    def rot(self, c):
        p = c.parent
        g = p.parent

        if not p.is_root():
            if g.right == p:
                g.right = c
            else:
                g.left = c 

        p.push()
        c.push()

        if p.left == c:
            p.left = c.right
            c.right = p
            if p.left != None:
                p.left.parent = p
        else:
            p.right = c.left
            c.left = p
            if p.right != None:
                p.right.parent = p 
        
        p.parent = c
        c.parent = g
        p.pull()
        c.pull()

    # brings node c to the top of its tree (must be done after accessing node c)
    def splay(self, c):
        while not c.is_root():
            p = c.parent 
            g = p.parent 
            if not p.is_root():
                if (g.right == p) == (p.right == c):
                    self.rot(p)
                else:
                    self.rot(c)
            self.rot(c)
        c.push()

    # finds minimum in subtree rooted at node c, then splays it to the top
    def head(self, c):
        p = c 
        p.push()
        while p.left != None:
            p = p.left
            p.push()
        self.splay(p)
        return p 
    
    # finds maximum in subtree rooted at node c, then splays it to the top
    def tail(self, c):
        p = c 
        p.push()
        while p.right != None:
            p = p.right
            p.push()
        self.splay(p)
        return p 
    
    # create a chain from v to the root of its tree, then splay v to the top
    # returns the lowest node that is both on the original root chain, and on the path from root to v
    def expose(self, v):
        last = None 
        c = self.nodes[v]
        p = c 
        while p != None:
            self.splay(p)
            p.right = last 
            p.pull()
            last = p 
            p = p.parent 
        self.splay(c) 
        return last
    
    # return lowest common ancestor of u and v
    def lca(self, u, v):
        self.expose(u)
        return self.expose(v).key
    
    # make v the root of the tree
    def evert(self, v):
        self.expose(v)
        c = self.nodes[v]
        if c.left != None:
            c.left.reverse = not c.left.reverse
            c.left = None 
            c.pull()
    
    # assumes u and v are in separate trees
    # makes v the root of its tree, then makes u the parent of v
    def link(self, u, v, x = None):
        if u not in self.nodes or v not in self.nodes or self.connected(u,v):
            return False
        if self.edgevals:
            key = self.nxt_key 

            c = Node(key)
            c.val = x 
            c.path = x
            self.edge_nodes[(u,v)] = key 
            self.edge_nodes[(v,u)] = key
            self.edges[key] = (u,v)
            self.nodes[key] = c
            while self.nxt_key in self.nodes:
                self.nxt_key += 1
            
            self.evert(u)
            self.nodes[u].parent = c
            self.evert(v)
            self.nodes[v].parent = c 
        else:
            self.edge_nodes[(u,v)] = True 
            self.edge_nodes[(v,u)] = True 

            self.evert(v)
            c = self.nodes[v]
            c.parent = self.nodes[u]
        return True

    # cuts the edge between u and v
    def cut(self, u, v):
        if (u,v) not in self.edge_nodes:
            return False
        
        if self.edgevals:
            key = self.edge_nodes[(u,v)]

            self.evert(key)

            self.expose(u)
            c = self.nodes[u]
            c.left.parent = None 
            c.left = None 
            c.pull()

            self.expose(v)
            c = self.nodes[v]
            c.left.parent = None 
            c.left = None 
            c.pull()

            self.nodes.pop(key)
            self.edge_nodes.pop((u,v))
            self.edge_nodes.pop((v,u))
            self.edges.pop(key)
        else:
            self.edge_nodes.pop((u,v))
            self.edge_nodes.pop((v,u))

            self.evert(u)
            self.expose(v)
            c = self.nodes[v]
            c.left.parent = None 
            c.left = None 
            c.pull()

        return True
        
    # queries whether u and v are connected
    def connected(self, u, v):
        if u == v:
            return True
        if u not in self.nodes or v not in self.nodes:
            return False
        self.expose(u) 
        self.expose(v) 
        return self.nodes[u].parent != None 

    # queries minimum on path from u to v
    def path(self, u, v):
        if u not in self.nodes or v not in self.nodes:
            return None
        self.evert(u)
        self.expose(v)
        if self.nodes[u].parent == None: 
            return None
        return self.nodes[v].path
    
    # set value of u to x
    def set_node(self, u, x):
        if self.edgevals or u not in self.nodes:
            return False
        self.expose(u)
        c = self.nodes[u]
        c.val = x 
        c.pull()
        return True

    # set value of edge from u to v to x
    def set_edge(self, u, v, x):
        if not self.edgevals or (u,v) not in self.edge_nodes:
            return False
        key = self.edge_nodes[(u,v)]
        self.expose(key)
        c = self.nodes[key]
        c.val = x 
        c.pull()
        return True

    # add x to all values on path from u to v
    def update_path(self, u, v, x):
        if not self.connected(u,v):
            return False
        self.evert(u)
        self.expose(v)
        self.nodes[v].update = x 
        self.nodes[v].push()
        return True

    # return the next node after u on the path to v
    def next_on_path(self, u, v):
        if not self.connected(u,v) or u == v:
            return None 
        
        self.evert(u)
        self.expose(v)
        c = self.nodes[u]
        self.splay(c)
        
        # must go two steps to the right if using edge values
        if self.edgevals:
            c = self.head(c.right)
            return self.head(c.right).key
        else:
            return self.head(c.right).key

    def mincost_helper(self, c):
        p = c
        p.push()
        while p.val != p.path:
            if p.left != None: p.left.push()
            if p.right != None: p.right.push()

            if p.left != None and p.left.path == p.path:
                p = p.left 
            else:
                p = p.right 
        self.splay(p)
        return p 

    # returns the first node with the minimum cost on path from u to v
    def get_mincost_node(self, u, v):
        if self.edgevals or not self.connected(u,v):
            return None
        
        self.evert(u)
        self.expose(v)
        c = self.mincost_helper(self.nodes[v])
        if c.val == None:
            return None 
        return c.key

    # returns the first edge with the minimum cost on path from u to v
    def get_mincost_edge(self, u, v):
        if not self.edgevals or not self.connected(u,v):
            return None
        
        self.evert(u)
        self.expose(v)
        c = self.mincost_helper(self.nodes[v])
        if c.val == None:
            return None
        return self.edges[c.key]
    
    # uesd for debugging
    def output(self):
        for key in self.edges:
            print(key, self.edges[key])
        for key in self.nodes:
            c = self.nodes[key]
            c.output()

# used for testing the LinkCutTree
# calculates minimum of edge values, O(n) bfs per query
class BruteForceTree:
    def __init__(self, keys):
        self.graph = dict() 
        for key in keys:
            self.graph[key] = dict() 

    def bfs(self, start):
        lvl = dict() 
        pred = dict()
        minval = dict()
        q = deque()
        lvl[start] = 0
        pred[start] = None 
        minval[start] = None
        q.append(start)
        
        while len(q) != 0:
            u = q.popleft()
            for v in self.graph[u]:
                if v not in lvl:
                    lvl[v] = lvl[u] + 1
                    pred[v] = u
                    minval[v] = self.graph[u][v] if minval[u]==None else min(minval[u], self.graph[u][v])
                    q.append(v)
        return lvl, pred, minval
    
    def connected(self, u, v):
        lvl, _pred, _minval = self.bfs(u)
        return v in lvl 

    def link(self, u, v, x = None):
        if self.connected(u,v):
            return False
        self.graph[u][v] = x
        self.graph[v][u] = x 
        return True
    
    def cut(self, u, v):
        if v not in self.graph[u]:
            return False
        self.graph[u].pop(v)
        self.graph[v].pop(u)
        return True

    def path(self, u, v):
        _lvl, _pred, minval = self.bfs(u) 
        if v not in minval:
            return None
        return minval[v] 

    def set_edge(self, u, v, x):
        if v not in self.graph[u]:
            return False
        self.graph[u][v] = x 
        self.graph[v][u] = x 
        return True

    def update_path(self, u, v, x):
        _lvl, pred, _minval = self.bfs(u)
        if v not in pred:
            return False 
        while v != u:
            v2 = pred[v]
            self.graph[v][v2] += x
            self.graph[v2][v] += x 
            v = v2 
        return True
    
    def next_on_path(self, u, v):
        _lvl, pred, _minval = self.bfs(v)
        if u not in pred:
            return None 
        return pred[u]
    
    def get_mincost_edge(self, u, v):
        _lvl, pred, minval = self.bfs(v)
        if u not in minval or u == v:
            return None 
        val = minval[u]
        while True:
            u2 = pred[u]
            if self.graph[u][u2] == val:
                return (u,u2)
            u = u2 


def stress_test():
    n = 100
    ops = 10000
    keys = [i for i in range(n)]
    lct = LinkCutTree(keys, True)
    brute = BruteForceTree(keys)
    edges = []

    # probs = [0, 5, 5, 3, 4, 5, 3, 3, 3]

    def output(op, input, output1, output2):
        opnames = ["", "connected", "link", "cut", "path", "set_edge", "update_path", "next_on_path", "get_mincost_edge"]
        print(opnames[op], input, output1, output2)

    for opnum in range(ops):
        op = random.randint(1,8)
        if opnum < 100:
            op = 2
        u = random.randint(0,n-1)
        v = random.randint(0,n-1)
        x = random.randint(1, 1000)
        input = None 
        output1 = None
        output2 = None
        if op == 1:
            input = (u,v)
            output1 = lct.connected(u,v)
            output2 = brute.connected(u,v)
        elif op == 2:
            input = (u,v,x)
            output1 = lct.link(u,v,x)
            output2 = brute.link(u,v,x)
            if output1:
                edges.append((u,v))
        elif op == 3:
            if len(edges) == 0:
                continue
            index = random.randint(0, len(edges)-1)
            u,v = edges[index]
            edges.pop(index)
            input = (u,v)
            output1 = lct.cut(u,v)
            output2 = brute.cut(u,v)
        elif op == 4:
            input = (u,v)
            output1 = lct.path(u,v)
            output2 = brute.path(u,v)
        elif op == 5:
            if len(edges) == 0:
                continue
            index = random.randint(0, len(edges)-1)
            u,v = edges[index]
            edges.pop(index)
            input = (u,v,x)
            output1 = lct.set_edge(u,v,x)
            output2 = brute.set_edge(u,v,x)
        elif op == 6:
            input = (u,v,x)
            output1 = lct.update_path(u,v,x)
            output2 = brute.update_path(u,v,x)
        elif op == 7:
            input = (u,v)
            output1 = lct.next_on_path(u,v)
            output2 = brute.next_on_path(u,v)
        elif op == 8:
            def standardize(edge):
                if edge == None:
                    return None
                a,b = edge 
                if a > b:
                    return b,a 
                return a,b
            input = (u,v)
            output1 = standardize(lct.get_mincost_edge(u,v))
            output2 = standardize(brute.get_mincost_edge(u,v))
        
        # output(op, input, output1, output2)
        if output1 != output2:
            print("ERROR")
            output(op, input, output1, output2)
            return
    print("Stress test successful!")
    return

def main():
    print("Expected answer: False, True, False, True")
    lct = LinkCutTree([1, 2, 3, 4, 5], False)
    print(lct.connected(1, 5))
    lct.link(1,2)
    lct.link(1,3)
    lct.link(3,4)
    lct.link(5,4)
    print(lct.connected(1,5))
    lct.cut(4,5)
    print(lct.connected(1,5))
    lct.cut(3,4)
    lct.link(3,5)
    print(lct.connected(1,5))
    lct.link(3,4)

    print("Expected answers: 2, 1, 2, 3, 5, 12")
    lct.set_node(1,3)
    lct.set_node(3,2)
    lct.set_node(2,6)
    lct.set_node(4,1)
    lct.set_node(5,5)
    print(lct.path(1,3))
    print(lct.path(2,4))
    print(lct.path(2,5))
    print(lct.path(2,1))
    lct.update_path(1,4,10)
    print(lct.path(2,5))
    print(lct.path(1,3))

    print("Expected answers: 2, 1, 3, 2, 3, 5, 6")
    lct = LinkCutTree([1, 2, 3, 4, 5], True)
    lct.link(1,2,3)
    lct.link(1,3,4)
    lct.link(3,4,1)
    lct.link(3,5,2)
    print(lct.path(2,5), lct.path(1,4), lct.path(2,3))
    lct.set_edge(3,4,6)
    print(lct.path(4,5), lct.path(2,4))
    lct.update_path(2, 5, 3)
    print(lct.path(4,5), lct.path(1,4))

    # random.seed(0)
    print("Stress Test:")
    stress_test()

if __name__ == "__main__":
    main()