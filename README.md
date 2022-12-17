There are 2 implementations of dynamic huffman codes via Vitter's Algorithm in this code base.

The first is in adaptive_huffman_bfs.py and is a naive implementation which showcases the algorithm itself for learning purposes.

The second is in the vitters_algorithm directory. However, there are some bugs that pop up for larger file sizes that we are working on fixing.
It can be run as follows (from the root project directory):
```
python3 -m vitters_algorithm --file file_you_want_to_compress.txt
```

Our final report and slides are also in the root directory of this project.
