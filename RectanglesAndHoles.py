from util import lgi, MyTimer, Board
#from entry1 import do_layout
from entry2 import do_layout
import sys

class RectanglesAndHoles(object):
    def __init__(self):
        pass

    def place(self, A, B):
        mt = MyTimer()
        board = Board(A, B)
        do_layout(board, mt)
        lgi('Total time %s', mt.delta())
        sys.stderr.flush()
        return board.array_out()
