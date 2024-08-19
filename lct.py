# Initial skeleton transcribed from C++ implementation by https://usaco.guide/adv/link-cut-tree?lang=cpp

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
        if self.reverse:
            self.reverse = False 
            self.left, self.right = self.right, self.left 
            if self.left != None: self.left.reverse = not self.left.reverse 
            if self.right != None: self.right.reverse = not self.right.reverse
        if self.update != 0:
            if self.val != None: self.val += self.update 
            if self.path != None: self.path += self.update 
            if self.left != None: self.left.update += self.update 
            if self.right != None: self.right.update += self.update 
            self.update = 0
    
    def comb(self, a, b):
        if a == None: return b 
        if b == None: return a
        return min(a, b)

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
    
class LinkCutTree:
    # initialize with labels of all nodes involved
    def __init__(self, keys):
        self.nodes = {}
        for key in keys:
            self.nodes[key] = Node(key)

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
    def link(self, u, v):
        self.evert(v)
        c = self.nodes[v]
        c.parent = self.nodes[u]

    # cuts the edge between u and v
    def cut(self, u, v):
        self.evert(u)
        self.expose(v)
        if self.nodes[v].left != None:
            self.nodes[v].left.parent = None 
            self.nodes[v].left = None 
            self.nodes[v].pull()

    # queries whether u and v are connected
    def connected(self, u, v):
        self.expose(u) 
        self.expose(v) 
        return self.nodes[u].parent != None 

    # queries minimum on path from u to v
    def path(self, u, v):
        self.evert(u)
        self.expose(v)
        if self.nodes[u].parent == None: return None
        return self.nodes[v].path
    
    # update value of u to x
    def update(self, u, x):
        self.expose(u)
        c = self.nodes[u]
        c.val = x 
        c.pull()

    # add x to all values on path from u to v
    def update_path(self, u, v, x):
        self.evert(u)
        self.expose(v)
        self.nodes[v].update = x 
        self.nodes[v].push()
    

def main():
    print("Expected answer: False, True, False, True")
    lct = LinkCutTree([1, 2, 3, 4, 5])
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
    lct.update(1,3)
    lct.update(3,2)
    lct.update(2,6)
    lct.update(4,1)
    lct.update(5,5)
    print(lct.path(1,3))
    print(lct.path(2,4))
    print(lct.path(2,5))
    print(lct.path(2,1))
    lct.update_path(1,4,10)
    print(lct.path(2,5))
    print(lct.path(1,3))

if __name__ == "__main__":
    main()