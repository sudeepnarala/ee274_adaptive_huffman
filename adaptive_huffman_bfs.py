from dataclasses import dataclass
from collections import deque
from bitarray import bitarray
from bitarray.util import int2ba, ba2int

@dataclass
class huffman_adaptive_node():
    def __init__(self, parent=None, left_child=None, right_child=None, value=None, weight=None):
        self.parent = parent
        self.left_child = left_child
        self.right_child = right_child
        self.value = value
        self.weight = weight

    @property
    def is_leaf(self):
        return (self.left_child is None) and (self.right_child is None)
    
    @property
    def is_left_child(self):
        if(self.parent is None):
            return False
        else:
            return (self is self.parent.left_child)
        
    @property
    def is_right_child(self):
        if(self.parent is None):
            return False
        else:
            return (self is self.parent.right_child)
    
    def swap_nodes(self, node):
        """
        Interchanges the position of 2 nodes in the tree
        """
        if(self is node):
            return
        else:
            # change pointers from parents
            if(self.is_left_child and node.is_left_child):
                self.parent.left_child, node.parent.left_child = node, self
            elif(self.is_left_child and node.is_right_child):
                self.parent.left_child, node.parent.right_child = node, self
            elif(self.is_right_child and node.is_left_child):
                self.parent.right_child, node.parent.left_child = node, self
            elif(self.is_right_child and node.is_right_child):
                self.parent.right_child, node.parent.right_child = node, self
            else:
                # Impossible case, something wrong
                assert(False)
            # change pointers from two nodes to parents
            self.parent, node.parent = node.parent, self.parent


    def _get_lines(self):
        """
        internal function to visualize the tree starting from the root node.
    
        Returns:
            lines, root_node
        """
    
        # utility function to merge two lists of strings
        def merge_lines(lines_1, lines_2):
            """
            example: lines_1 = ["A","B","C"],
            lines_2 = ["1","2","3"]
            -> return lines = ["A1","B2","C3"]
            """
            lines = []
            for l1, l2 in zip(lines_1, lines_2):
                lines.append(l1 + str(l2))
            return lines
    
        # form a printable id (in case it is None)
        _value = self.value if self.value else "\u00B7"  # -> center dot
    
        # if node is leaf, return only the id
        if self.is_leaf:
            return [_value], 0
    
        # recursively get lines, and root node location for the
        # left and right subtrees
        if self.left_child is not None:
            lines_left, root_loc_left = self.left_child._get_lines()
        else:
            lines_left, root_loc_left = [], None
    
        if self.right_child is not None:
            lines_right, root_loc_right = self.right_child._get_lines()
        else:
            lines_right, root_loc_right = [], None
    
        ## The strategy to join the two subtrees is:
        #    |--left_tree
        # id-|
        #    |--right_tree
        #
        ## Step 0: Join the lines together (with a space in between)
        #       left_tree
        #
        #       right_tree
        #
        ## Step 1: add the first stage
        #
        #     --left_tree
        #
        #     --right_tree
        #
        ## Step 2: add the second stage
        #
        #    |--left_tree
        #    |
        #    |--right_tree
        #
        ## Step 3: Finally add the id
        #    |--left_tree
        # id-|
        #    |--right_tree
        #
    
        ## join the two lines
        lines = lines_left + [""] + lines_right
        root_node_loc = len(lines_left)
    
        # update right loc if it is not None
        if root_loc_right is not None:
            root_loc_right = root_node_loc + 1 + root_loc_right
    
        # add the first stage
        spacer = ["  " for i in range(len(lines))]
        if root_loc_left is not None:
            spacer[root_loc_left] = "--"
        if root_loc_right is not None:
            spacer[root_loc_right] = "--"
        lines = merge_lines(spacer, lines)
    
        # add the second stage
        spacer = [" " for i in range(len(lines))]
        if root_loc_left is not None:
            for i in range(root_loc_left, root_node_loc + 1):
                spacer[i] = "|"
    
        if root_loc_right is not None:
            for i in range(len(lines_left) + 1, root_loc_right + 1):
                spacer[i] = "|"
        lines = merge_lines(spacer, lines)
    
        # add the final stage
        _value = _value + "-"
        spacer = [" " * len(_value) for i in range(len(lines))]
        spacer[root_node_loc] = _value
        lines = merge_lines(spacer, lines)
    
        return lines, root_node_loc
    
    def print_node(self):
        """
        Print the tree from the root node
    
        returns the lines of the tree, and the line number of the node
        internal function used in recursively printing the node
    
                    |--D
               |--·-|
               |    |--C
          |--·-|
          |    |--B
        ·-|
          |--A
        """
        lines, _ = self._get_lines()
        print()  # add empty line to make sure we start on newline
        for line in lines:
            print(line)


class huffman_adaptive_tree:
    """
    Tree-based adaptive Huffman coder
    """
    def __init__(self):
        self.root = huffman_adaptive_node(parent=None, weight=0)
        self.nyt = self.root        # NYT node
        self.implicit_order = []    # list of all nodes in descending implicit order
        self.codebook = {}          # dict for input data encoding table
        self.alphabet_size = 256    # max number of symbols

    def encode_symbol(self, symbol):
        """
        For the first symbol, only the binary code will be transmitted
        
        For subsequent new symbols, the path to NYT node will first be
        transmitted, followed by the binary code for the symbol
        
        For subsequent symbols already in codebook, only the path to the node
        will be transmitted
        
        Encoding occurs prior to updating the tree
        """
        leaf_to_increment = None    # leaf to increment
        encoded_symbol = []
        p = self._find_symbol(symbol)   # pointer to leaf node containing next symbol
        if(p is self.nyt):
            if(len(self.codebook) == 0):
                encoded_symbol = int2ba(symbol, length=8)
            else:
                encoded_symbol = self.codebook[None] + int2ba(symbol, length=8)
            if(len(self.implicit_order) == (2*self.alphabet_size - 1)):
                p.value = symbol
                self.nyt = None
            else:
                p.left_child = huffman_adaptive_node(parent=p, weight=0, value=None)
                p.right_child = huffman_adaptive_node(parent=p, weight=0, value=symbol)
                self.nyt = p.left_child
                leaf_to_increment = p.right_child
                self._update_implicit_order()
        else:
            encoded_symbol = self.codebook[symbol]
            # swap p with leader of its block
            for node in self.implicit_order:
                if((node.weight == p.weight) and node.is_leaf):  # find leader
                    p.swap_nodes(node)
                    self._update_implicit_order()
                    break
            if(p is self.implicit_order[-2]):  # p is sibling of NYT node
                leaf_to_increment = p
                p = p.parent
        while(p is not None):
            p = self._slide_and_increment(p)
        if(leaf_to_increment is not None):
            p = self._slide_and_increment(leaf_to_increment)
        self._update_codebook(self.root)
        return encoded_symbol
        
    def decode_symbol(self, encoded_bitarray):
        """
        First symbol is special case. Read 8 bits for symbol binary code.
        
        For subsequent symbols, read in bits until a match in the codebook is
        found. If node is NYT, read next 8 bits for symbol binary code. If
        symbol is not NYT, find symbol from codebook then update tree.
        """
        num_bits = 1
        symbol = None
        if(self.nyt is self.root):
            # special case for first symbol
            symbol = ba2int(encoded_bitarray[0:8])
            num_bits = 8
        else: 
            # read in bits until a codeword is found (NYT is in codebook)
            # if NYT then read in another 8 bits for symbol binary code
            path = encoded_bitarray[0:num_bits]
            while(path not in self.codebook.values()):
                num_bits += 1
                path = encoded_bitarray[0:num_bits]
            key = list(self.codebook.keys())[list(self.codebook.values()).index(path)]
            if(key is None):  # new symbol
                symbol = ba2int(encoded_bitarray[num_bits:num_bits+8])
                num_bits += 8
            else:
                symbol = key
        self.encode_symbol(symbol)
        return symbol, num_bits

    def _slide_and_increment(self, p):
        """
        Internal function to update the tree
        """
        def _get_index():
            for i in range(len(self.implicit_order)):
                if(p is self.implicit_order[i]):
                    return i

        prev_p = p.parent
        if(p.is_leaf is False):  # p is internal node
            # slide p to higher than leaf nodes of wt + 1    
            idx = _get_index()
            if(idx == 0):
                pass
            else:
                while((self.implicit_order[idx-1].is_leaf and (self.implicit_order[idx-1].weight <= p.weight+1))
                      or ((self.implicit_order[idx-1].is_leaf is False) and (self.implicit_order[idx-1].weight <= p.weight))):
                    p.swap_nodes(self.implicit_order[idx-1])
                    idx -= 1
            # increase weight of p by 1
            p.weight += 1
            p = prev_p
            self._update_implicit_order()
        else:  # p is leaf
            # slide p higher than internal nodes of wt
            idx = _get_index()
            if(idx == 0):
                pass
            else:
                while(self.implicit_order[idx-1].weight <= p.weight):
                    p.swap_nodes(self.implicit_order[idx-1])
                    idx -= 1
            # increase weight of p by 1
            p.weight += 1
            p = p.parent
            self._update_implicit_order()
        return p

    def _find_symbol(self, symbol):
        """
        Internal function to return a pointer to the leaf node for the symbol
        """
        p = self.root
        if(symbol in self.codebook):
            path = self.codebook[symbol].copy()
            while(len(path) > 0):
                if(path[0] == 0):
                    p = p.left_child
                else:
                    p = p.right_child
                path = path[1:]
            return p
        else:
            return self.nyt

    def _update_implicit_order(self):
        """
        Internal function to update the implicit order by BFS traversal from
        right to left
        """
        self.implicit_order = [self.root]
        q = deque(maxlen=(2*self.alphabet_size - 1))
        q.append(self.root)
        while(len(q) > 0):
            v = q.popleft()
            if(v.right_child is not None):
                self.implicit_order.append(v.right_child)
                q.append(v.right_child)
            if(v.left_child is not None):
                self.implicit_order.append(v.left_child)
                q.append(v.left_child)
            
    def _update_codebook(self, node, path=None):
        """
        Internal function to update codebook by DFS
        """
        if(path is None):  # initialize
            path = bitarray()
            self.codebook = {}
        # if leaf, add codeword to codebook
        if(node.is_leaf):
            self.codebook[node.value] = path.copy()
        # DFS
        if(node.left_child is not None):
            path += "0"
            path = self._update_codebook(node.left_child, path)
        if(node.right_child is not None):
            path += "1"
            path = self._update_codebook(node.right_child, path)
        # update visited before going up the tree a level
        path = path[:-1]
        return path


    def print_tree(self):
        """
        Print out the tree line graph, implicit order, and codebook
        """
        self.root.print_node()
        print()
        order = 2*self.alphabet_size - 1
        for node in self.implicit_order:
            if(node.is_leaf):
                print(f'Order: {order:3d} | Weight: {node.weight:3d} | Value: {node.value} | LEAF')
            else:
                print(f'Order: {order:3d} | Weight: {node.weight:3d} | Value: {node.value} | INTERNAL')
            order -= 1
        print()
        print(self.codebook)
        





def test_encdec():
    # string = "aa bbb c"
    string = []
    tx = huffman_adaptive_tree()
    encoded_bitarray = bitarray()
    for i in range(256):
        string.append(i)
        encoded_bitarray += tx.encode_symbol(i)
    for i in range(256):
        string.append(i)
        encoded_bitarray += tx.encode_symbol(i)
    
    print()
    symbols = []
    rx = huffman_adaptive_tree()
    while(len(encoded_bitarray) > 0):
        symbol, num_bits = rx.decode_symbol(encoded_bitarray)
        symbols.append(symbol)
        encoded_bitarray = encoded_bitarray[num_bits:]
    print(string == symbols)
    
    
if __name__ == "__main__":
    test_encdec()
    
    
