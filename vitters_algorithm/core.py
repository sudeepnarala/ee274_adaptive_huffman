from typing import List, Union
import traceback

class CustomList(list):
    def __init__(self, iterable):
        super().__init__(item for item in iterable)

    def __getitem__(self, idx):
        print(f"Get requested on {idx}")
        traceback.print_stack(limit=2)
        return super().__getitem__(idx)

    def __setitem__(self, key, value):
        print(f"Set requested on {key} with value {value}")
        traceback.print_stack(limit=2)
        return super().__setitem__(key, value)

# Set requested on 0 with value 255
# Set requested on 1 with value 510
# Set requested on 2 with value 509


class AdaptiveHuffman:
    # aka n in original paper
    ALPHABET_SIZE = 256
    # Aka Z in original paper
    NUM_NODES_POSSIBLE = 2 * ALPHABET_SIZE - 1  # In the case of a completely balanced tree

    def __init__(self):
        # Init all data structures to 0s initially
        self.alphabet: List[int] = [0] * self.ALPHABET_SIZE          # Node value to alphabet index mapping (ascii value)
        self.representation: List[int] = [0] * self.ALPHABET_SIZE    # Alphabet index to node value mapping

        self.block: List[int] = [0] * self.NUM_NODES_POSSIBLE

        self.weight: List[int] = [0] * self.NUM_NODES_POSSIBLE
        self.parent: List[Union[int, None]] = [0] * self.NUM_NODES_POSSIBLE
        # self.parent = CustomList([0]*self.NUM_NODES_POSSIBLE)
        self.parity: List[int] = [0] * self.NUM_NODES_POSSIBLE
        self.right_child: List[Union[int, None]] = [0] * self.NUM_NODES_POSSIBLE
        # aka first node in original paper
        self.leader_node: List[int] = [0] * self.NUM_NODES_POSSIBLE
        # self.leader_node: List[int] = CustomList([0]*self.NUM_NODES_POSSIBLE)
        self.last_node: List[int] = [0] * self.NUM_NODES_POSSIBLE
        self.prev_block: List[int] = [0] * self.NUM_NODES_POSSIBLE
        self.next_block: List[int] = [0] * self.NUM_NODES_POSSIBLE
        self.available_block: int = 0

        # Maintained such that M = 2^E+R
        self.M = 0      # This holds the number of unseen elements of alphabet
        self.E = 0
        self.R = -1
        # Get correct values for M, R and E (could also use a log2)
        for i in range(self.ALPHABET_SIZE):
            self.M += 1
            self.R += 1
            # Reached point where residual is equal to 2^E
            if 2*self.R == self.M:
                self.E += 1
                self.R = 0

        # Set initial mapping to be the identity mapping
        for i in range(self.ALPHABET_SIZE):
            self.alphabet[i] = i
            self.representation[i] = i

        # Initialize n'th node as NYT (0-node)
        # Bug, was 1, needs to be 0 because of 0 indexing
        self.block[self.ALPHABET_SIZE-1] = 0
        self.prev_block[0] = 0
        self.next_block[0] = 0
        self.weight[0] = 0
        self.leader_node[0] = self.ALPHABET_SIZE-1
        self.last_node[0] = self.ALPHABET_SIZE-1
        self.parity[0] = 0
        self.parent[0] = None
        self.available_block = 1
        for i in range(self.available_block, self.NUM_NODES_POSSIBLE-2):
            self.next_block[i] = i+1
        self.next_block[self.NUM_NODES_POSSIBLE-1] = 0

    def interchange_leaves(self, node1, node2):
        self.representation[node1], self.representation[node2] = self.representation[node2], self.representation[node1]
        self.alphabet[node1], self.alphabet[node2] = self.alphabet[node2], self.alphabet[node1]

    # Originally under FindNode in paper
    def spawn_new_node(self, node):
        self.interchange_leaves(node, self.M-1)
        # Maintaining M = 2^E+R
        if self.R == 0:
            self.R = self.M // 2
            if self.R > 0:
                self.E = self.E-1
        self.M -= 1
        self.R -= 1
        # Set node to the 0-node
        node = self.M
        node_block = self.block[node]
        # Zero node is @ self.M-1, just like it usually is
        if self.M > 0:  # I.e. more unseen
            old_nyt_block = self.block[self.M]
            # Copy block from old NYT to new NYT
            self.block[self.M-1] = old_nyt_block
            self.last_node[old_nyt_block] = self.M-1
            old_nyt_parent = self.parent[old_nyt_block]
            # Bug fix, needs to be self.M-1 not self.M (because this is start of array in Python)
            self.parent[node_block] = self.M - 1 + self.ALPHABET_SIZE
            # MAJOR BUG FIX, I THINK THIS IS WRONG IN THE PAPER
            # self.leader_node[node_block] = self.M
            # Leader is now on the right (leader is the newly created 0-weight node)
            self.parity[node_block] = 1
            # Now, create parent @ M+n for these 2 nodes
            old_available_block = self.available_block
            self.available_block = self.next_block[self.available_block]
            self.prev_block[old_available_block] = old_nyt_block
            self.next_block[old_available_block] = self.next_block[node_block]
            self.prev_block[self.next_block[node_block]] = old_available_block
            self.next_block[node_block] = old_available_block
            self.parent[old_available_block] = old_nyt_parent
            self.parity[old_available_block] = 0
            self.right_child[old_available_block] = node
            self.block[self.M-1+self.ALPHABET_SIZE] = old_available_block
            self.weight[old_available_block] = 0
            self.leader_node[old_available_block] = self.M-1+self.ALPHABET_SIZE
            self.last_node[old_available_block] = self.M-1+self.ALPHABET_SIZE
            leaf_to_increment = node
            node = self.M-1+self.ALPHABET_SIZE
            return [node, leaf_to_increment]
        else:
            return [node, None]

    def get_leaf(self, alphabet_idx):
        print("Before", self.leader_node)
        node = self.representation[alphabet_idx]
        leaf_to_increment = None
        if node <= self.M-1:    # We just saw an unseen node, spawn a new node
            node, leaf_to_increment = self.spawn_new_node(node)
            print(f"spawn outputted {node}")
        else:
            # Move leaf to the front of block
            self.interchange_leaves(node, self.leader_node[self.block[node]])
            node = self.leader_node[self.block[node]]
            # If your sibling is NYT (0-node)
            if node == self.M and self.M > 0:
                leaf_to_increment = node
                node = self.parent[self.block[node]]
        print("After", self.leader_node)
        return [node, leaf_to_increment]

    def slide_and_increment(self, node):
        print(f"Slide and increment before for {node}", self.leader_node)
        # We know that node is the leader of its block
        node_block = self.block[node]
        # Bug, was doing self.next_block[node]
        next_block = self.next_block[self.block[node]]
        node_parent = self.parent[node_block]     # since node is the leader
        old_parent = node_parent
        old_parity = self.parity[node_block]
        to_slide = False
        # Means node is a leaf and the next block is a block of internal nodes with same weight OR
        # node is a an internal node and next block is a block of leaves with weight being 1 higher (need to slide ahead
        # of block of leaves to maintain invariant that leaves with same implicit number occur before internal nodes)

        # Is it an error to access uninitialized leader_node[next_block]?? This happens at the very beginning.
        # I think it is an error because get_leaf is not doing its job correctly.
        print(node, self.ALPHABET_SIZE, self.leader_node[next_block], next_block, self.block[node])
        print(self.last_node[node_block], node)
        if (node < self.ALPHABET_SIZE <= self.leader_node[next_block] and
            self.weight[node_block] == self.weight[next_block]) or \
            (self.leader_node[next_block] < self.ALPHABET_SIZE <= node and
            self.weight[node_block] + 1 == self.weight[next_block]):
            print("here")
            to_slide = True
            old_parent = self.parent[next_block]
            old_parity = self.parity[next_block]
            if node_parent is not None:
                parent_block = self.block[node_parent]
                if self.right_child[parent_block] == node:
                    self.right_child[parent_block] = self.last_node[next_block]
                elif self.right_child[parent_block] == self.leader_node[next_block]:
                    self.right_child[parent_block] = node
                else:
                    self.right_child[parent_block] = self.right_child[parent_block] + 1
                # if parent is not root
                if node_parent != self.NUM_NODES_POSSIBLE-1:
                    if self.block[node_parent+1] != parent_block:
                        if self.right_child[self.block[node_parent+1]] == self.leader_node[next_block]:
                            self.right_child[self.block[node_parent+1]] = node_parent
                        elif self.block[self.right_child[self.block[node_parent+1]]] == next_block:
                            self.right_child[self.block[node_parent+1]] = self.right_child[self.block[node_parent+1]]+1
                self.parent[next_block] = self.parent[next_block] - 1 + self.parity[next_block]
                # Flipping parity
                self.parity[next_block] = 1 - self.parity[next_block]
        else:
            to_slide = False
        if (node < self.ALPHABET_SIZE and self.leader_node[next_block] < self.ALPHABET_SIZE) or \
                (node >= self.ALPHABET_SIZE and self.leader_node[next_block] >= self.ALPHABET_SIZE):
            self.block[node] = next_block
            self.last_node[next_block] = node
            # Current node was the only node in the block
            if self.last_node[node_block] == node:
                self.next_block[self.prev_block[node_block]] = self.next_block[node_block]
                self.prev_block[self.next_block[node_block]] = self.prev_block[node_block]
                self.next_block[node_block] = self.available_block
                self.available_block = node_block
            else:
                if node >= self.ALPHABET_SIZE:
                    self.right_child[node_block] = self.find_child(node-1, 1)
                    if self.parity[node_block] == 0:
                        self.parent[node_block] = self.parent[node_block]-1
                        # Flipping parity
                        self.parity[node_block] = 1-self.parity[node_block]
                        self.leader_node[node_block] = node-1
        elif self.last_node[node_block] == node:
            if to_slide:
                self.prev_block[self.next_block[node_block]] = self.prev_block[node_block]
                self.next_block[self.prev_block[node_block]] = self.next_block[node_block]
                self.prev_block[node_block] = self.prev_block[next_block]
                self.next_block[node_block] = next_block
                self.prev_block[next_block] = node_block
                self.next_block[self.prev_block[node_block]] = node_block
                self.parent[node_block] = old_parent
                self.parity[node_block] = old_parity
            self.weight[node_block] = self.weight[node_block]+1
        else:   # Moves to a block of its own
            print("own block")
            block_to_use = self.available_block
            self.available_block = self.next_block[self.available_block]
            self.block[node] = block_to_use
            self.leader_node[block_to_use] = node
            self.last_node[block_to_use] = node
            if node >= self.ALPHABET_SIZE:
                self.right_child[block_to_use] = self.right_child[node_block]
                self.right_child[node_block] = self.find_child(node-1, 1)
                # THIS SHOULD BE 255 BUT GETTING 256!
                print(f"Found child for {node-1}: {self.right_child[node_block]}")
                if self.right_child[block_to_use] == node-1:
                    self.parent[node_block] = node
                elif self.parity[node_block] == 0:
                    self.parent[node_block] = self.parent[node_block]-1
            elif self.parity[node_block] == 0:
                self.parent[node_block] = self.parent[node_block]-1
            # Bug fix: all of this stuff
            # Leader is node before you
            self.leader_node[node_block] = node-1
            self.parity[node_block] = 1-self.parity[node_block]
            self.prev_block[block_to_use] = self.prev_block[next_block]
            self.next_block[block_to_use] = next_block
            self.prev_block[next_block] = block_to_use
            self.next_block[self.prev_block[block_to_use]] = block_to_use
            self.weight[block_to_use] = self.weight[node_block]+1
            self.parent[block_to_use] = old_parent
            self.parity[block_to_use] = old_parity

        if node < self.ALPHABET_SIZE:
            node = old_parent
        else:
            node = node_parent
        print("Slide and increment after", self.leader_node)
        return node

    def find_child(self, node, direction):
        delta = 2*(self.leader_node[self.block[node]]-node) + 1 - direction
        right = self.right_child[self.block[node]]
        gap = right-self.last_node[self.block[right]]
        if delta <= gap:
            return right-delta  # Same block as right child of leader so can just do direct subtraction arithmetic
        else:
            delta = delta-gap-1
            right = self.leader_node[self.prev_block[self.block[right]]]
            gap = right-self.last_node[self.block[right]]
            if delta <= gap:
                return right-delta
            else:
                return self.leader_node[self.prev_block[self.block[right]]]-delta+gap+2

    # Update tree given that we just got a new element @ alphabet idx
    def update(self, alphabet_idx) -> None:
        node, leaf_to_increment = self.get_leaf(alphabet_idx)
        print(f"UPDATE GOING THROUGH FOR NODE {node}, {leaf_to_increment}")
        while node is not None:
            node = self.slide_and_increment(node)
        if leaf_to_increment is not None:
            node = self.slide_and_increment(leaf_to_increment)













