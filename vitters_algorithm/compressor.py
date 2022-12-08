from .core import AdaptiveHuffman
from bitarray import bitarray


class AdaptiveHuffmanCompressor(AdaptiveHuffman):
    def __init__(self):
        super().__init__()

    def compress(self, alphabet_idx):
        # node is implicitly an index
        node = self.representation[alphabet_idx]
        stack = bitarray()
        if node <= self.M-1:        # If node is unseen before this point
            # Special logic for transmitting (we don't have to do -1 like in original paper because Python is 0-indexed
            # unlike scala)
            num_bits = -1
            if node < 2*self.R:
                num_bits = self.E+1
            else:
                node -= self.R
                num_bits = self.E
            # Get the base 2 representation of (potentially modified) node
            for i in range(num_bits):
                stack += "1" if node & 1 else "0"
                node = node >> 1
            # We need to transfer over the location of the NYT node so decompressor knows this is a new letter
            node = self.M-1
        # If this is the first letter we are seeing
        root = -1
        if self.M == self.ALPHABET_SIZE:
            root = self.ALPHABET_SIZE-1
        else:
            root = self.NUM_NODES_POSSIBLE-1
        # Traverse up the tree and append to attack
        while node != root:
            # print(self.block, node)
            node_block = self.block[node]
            # Made this part a little easier to understand than in the paper
            # Since the tree is balanced, you can figure out your direction (i.e. left or right) depending on the leader
            # of your block;s direction
            leader_node_implicit_diff = self.leader_node[node_block] - node
            # print(leader_node_implicit_diff)
            leader_direction = self.parity[node_block]
            if leader_node_implicit_diff % 2 == 0:   # Same as leader
                stack += "1" if leader_direction else "0"
            else:                               # Different from leader
                stack += "0" if leader_direction else "1"
            # print(f"Leader of {node} is {self.leader_node[node_block]}")
            # Update the node (i.e. set node to parent of current node)
            leader_parent = self.parent[node_block]
            # Intuition: For every 2 movements from leader to node, we have 1 movement from parent to node's parent
            # because balanced tree
            leader_parent_node_parent_implicit_diff = (leader_node_implicit_diff + (1-self.parity[node_block])) // 2
            node = leader_parent - leader_parent_node_parent_implicit_diff
            # print(leader_node_implicit_diff, leader_parent_node_parent_implicit_diff)
        stack.reverse()
        return stack

    def compress_update(self, alphabet_idx):
        ret = self.compress(alphabet_idx)
        self.update(alphabet_idx)
        return ret
