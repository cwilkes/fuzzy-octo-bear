from operator import attrgetter
import sys
import datetime


MAX_MILLIS = 9 * 1000 * 1000


class MyTimer(object):
    def __init__(self):
        self.start_time = datetime.datetime.now()

    def delta(self):
        dt = datetime.datetime.now() - self.start_time
        return 1000*1000*dt.seconds + dt.microseconds

    def is_over(self):
        ret = self.delta() >= MAX_MILLIS
        if ret:
            lgi('Over time! %s', ret)
        return ret


def lgi(fmt, *msg):
    print >>sys.stderr, fmt % msg
    sys.stderr.flush()


class CoverBoard(object):
    def __init__(self, board):
        self.board = board
        self.widths, self.heights, self.indexes = list(), list(), list()
        for t in board.tiles:
            self.widths.append((t.col, t.col+t.width-1))
            self.heights.append((t.row, t.row+t.height-1))
            self.indexes.append(t.index)

    def find_min_col(self, col, row):
        ret = -sys.maxint
        for pos, (min_row, max_row) in enumerate(self.heights):
            if min_row <= row <= max_row:
                min_col, max_col = self.widths[pos]
                if col >= max_col:
                    ret = max(ret, max_col)
        return ret

    def __contains__(self, item):
        for pos, (min_col, max_col) in enumerate(self.widths):
            if min_col <= item[0] <= max_col:
                min_row, max_row = self.heights[pos]
                if min_row <= item[1] <= max_row:
                    lgi('hit on # %d with tile %s for col %d <= %d <= %d and row %d <= %d <= %d',
                        pos, self.board[self.indexes[pos]], min_col, item[0], max_col, min_row, item[1], max_row)
                    return True
        return False


class Board(object):
    def __init__(self, A, B):
        self.tiles = list()
        for pos, (w, h) in enumerate(zip(A, B)):
            self.tiles.append(Tile(len(self.tiles), w, h))

    def __getitem__(self, item):
        return self.tiles[item]

    def __iter__(self):
        return self.tiles.__iter__()

    def __len__(self):
        return len(self.tiles)

    def get_by_max_dim(self):
        return sorted(self.tiles, key=attrgetter('max_dim'))

    def __nonzero__(self):
        return len(self.tiles) != 0

    def make_cover_board(self):
        return CoverBoard(self)

    def array_out(self):
        ret = list()
        for tile in self.tiles:
            ret.append(tile.col)
            ret.append(tile.row)
            ret.append(tile.direction)
        return ret


class Tile(object):
    def __init__(self, index, width, height, col=0, row=0):
        self.index = index
        self.width, self.height = width, height
        self.col, self.row = col, row
        self.direction = 0
        self.max_dim = max(self.width, self.height)
        self.min_dim = min(self.width, self.height)

    def flip(self):
        self.direction = (self.direction+1) % 2
        self.width, self.height = self.height, self.width
        return self

    def move(self, col, row):
        self.col, self.row = col, row
        return self

    def bump(self, col=0, row=0):
        return self.move(self.col + col, self.row+row)

    def rotate_longway(self, direction):
        if self.height > self.width:
            if direction == 0:
                self.flip()
        else:
            if direction == 1:
                self.flip()
        return self

    def __str__(self):
        return 'Rectangle %d (w:%d,h:%d) is (%d, %d) - (%d, %d)' % (self.index, self.width, self.height, self.col, self.row, self.col+self.width, self.row+self.height)
