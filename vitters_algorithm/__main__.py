import argparse
from bitarray import bitarray
from .compressor import AdaptiveHuffmanCompressor
from.decompressor import AdaptiveHuffmanDecompress


def run_vitters(file_name):
    compressor = AdaptiveHuffmanCompressor()
    stream = bitarray()
    decompressor = AdaptiveHuffmanDecompress(stream=stream)
    with open(file_name, "r") as f:
        while True:     # Keep reading till EOF
            next_char = f.read(1)
            if next_char == "":
                break
            next_char_ascii = ord(next_char)
            # print("Updating for "+str(next_char_ascii))
            # print(f"Update complete from {next_char}, got value: {compressor.compress_update(next_char_ascii)}")
            # print("-"*20)
            bits = compressor.compress_update(next_char_ascii)
            stream += bits
            print(f"Sending over bits {bits}")
    decompressor.decompress()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-name", dest="file_name", help="file to compress", required=True)
    args = parser.parse_args()
    run_vitters(args.file_name)
