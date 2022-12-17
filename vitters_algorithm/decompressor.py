from .core import AdaptiveHuffman


class CompletedException(Exception):
    pass


class AdaptiveHuffmanDecompress(AdaptiveHuffman):
    def __init__(self, stream):
        super().__init__()
        self.stream = stream
        self.stream_idx = 0

    def receive(self) -> int:
        if self.stream_idx == len(self.stream):
            raise CompletedException
        ret = self.stream[self.stream_idx]
        self.stream_idx += 1
        # print(f"Consumed {ret}")
        return ret

    def decompress(self):
        # print("_"*10)
        res = ""
        while True:
            try:
                # import pdb; pdb.set_trace()
                # Bug: Had this as self.ALPHABET_SIZE-1 but should be self.ALPHABET_SIZE
                if self.M == self.ALPHABET_SIZE:
                    node = self.M-1
                else:
                    node = self.NUM_NODES_POSSIBLE-1
                consumed = 0
                # import pdb; pdb.set_trace()
                while node > self.ALPHABET_SIZE-1:
                    bit = self.receive()
                    # print(f"Node: {node}")
                    node = self.find_child(node, bit)
                    # print(f"Node {node} after consuming bit {bit}")
                    consumed += 1
                # print(f"Node {node}, leader: {self.leader_node[self.block[node]]}")

                if node == self.M-1:
                    # print(f"GOT NYT and consumed {consumed} bits to get here")
                    node = 0
                    # print(self.E)
                    for i in range(self.E):
                        node = 2*node+self.receive()
                        consumed += 1
                    if node < self.R:
                        node = 2*node+self.receive()
                        consumed += 1
                    else:
                        node = node+self.R
                    # No need to do +1 here because didn't do -1 in compressor
                # print(node, self.alphabet[node])
                # THIS IS A PATCH: FIGURE OUT WHY IT IS WORKING!
                # print(f"DECOMPRESSOR GOT letter: {chr(self.alphabet[node])}, consumed: {consumed}, @ node: {node}")
                res += chr(self.alphabet[node])
                # Bug, was passing in node
                self.update(self.alphabet[node])
            except CompletedException:
                # print("Done processing input on decompressor side")
                break
        # print(res)
