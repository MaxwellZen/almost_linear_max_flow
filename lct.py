# Transcribed from C++ implementation by https://usaco.guide/adv/link-cut-tree?lang=cpp

class Node:
    def __init__(self):
        self.key = None
        self.left = None 
        self.right = None 
        self.parent = None 
        self.reverse = False 
    
    def __init__(self, key):
        self.key = key
        self.left = None 
        self.right = None 
        self.parent = None 
        self.reverse = False 
    
    def push(self):
        if self.reverse:
            self.reverse = False 
            self.left, self.right = self.right, self.left 
            if self.left:
                self.left.reverse = not self.left.reverse 
            if self.right:
                self.right.reverse = not self.right.reverse
    
    def is_root(self):
        return self.parent == None or (self.parent.left != self and self.parent.right != self)
    
class LinkCutTree:
    # initialize with labels of all nodes involved
    def __init__(self, keys):
        self.nodes = {}
        for key in keys:
            self.nodes[key] = Node(key)

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
    
    def access(self, v):
        last = None 
        c = self.nodes[v]
        p = c 
        while p != None:
            self.splay(p)
            p.right = last 
            last = p 
            p = p.parent 
        self.splay(c) 
        return last
    
    def make_root(self, v):
        self.access(v)
        c = self.nodes[v]
        if c.left != None:
            c.left.reverse = not c.left.reverse
            c.left = None 
    
    # assumes u and v are in separate trees
    # makes v the root of its tree, then makes u the parent of v
    def link(self, u, v):
        self.make_root(v)
        c = self.nodes[v]
        c.parent = self.nodes[u]

    def cut(self, u, v):
        self.make_root(u)
        self.access(v)
        if self.nodes[v].left != None:
            self.nodes[v].left.parent = None 
            self.nodes[v].left = None 

    def connected(self, u, v):
        self.access(u) 
        self.access(v) 
        return self.nodes[u].parent != None 

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

if __name__ == "__main__":
    main()