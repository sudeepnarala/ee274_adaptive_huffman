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
        return ret

    def decompress(self):
        print("_"*10)
        try:
            if self.M == self.ALPHABET_SIZE-1:
                node = self.M-1
            else:
                node = self.NUM_NODES_POSSIBLE-1
            while node > self.M-1:
                node = self.find_child(node, self.receive())
                print(f"Node {node}")
            if node == self.M-1:
                node = 0
                for i in range(self.E):
                    node = 2*node+self.receive()
                if node < self.R:
                    node = 2*node+self.receive()
                else:
                    node = node+self.R
                # No need to do +1 because didn't do -1 in compressor
            print(node, self.alphabet[node])
            print(chr(self.alphabet[node]))
        except CompletedException:
            print("Done processing input on decompressor side")
