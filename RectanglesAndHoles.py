from operator import attrgetter
import sys
import datetime


MAX_MILLIS = 9 * 1000 * 1000

start_time = None


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

def lgi(format, *msg):
    print >>sys.stderr, format % msg
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


def _outside_box(board, mt):
    total_length = 0
    for tile in board:
        total_length += tile.max_dim
    tile_ids = [_.index for _ in sorted(board, key=attrgetter('max_dim'), reverse=True)]
    lgi('total length %d', total_length)
    side_length = (total_length * 0.95) / 5
    # can have some overlap in the starting corner
    tile = board[tile_ids.pop(0)]
    tile.move(0, 0)
    tile.rotate_longway(0)
    col = tile.width
    row = 0
    lgi('Start top wall at %s', mt.delta())
    while col < side_length and tile_ids:
        tile = board[tile_ids.pop(0)]
        tile.rotate_longway(0)
        tile.move(col, row)
        col += tile.width
    lgi('Start right wall at %s', mt.delta())
    while row > -side_length and tile_ids:
        tile = board[tile_ids.pop(0)]
        tile.rotate_longway(1)
        row -= tile.height
        tile.move(col, row)
    row += tile.height-1
    lgi('Start bottom wall at %s', mt.delta())
    while col > 0 and tile_ids:
        tile = board[tile_ids.pop(0)]
        tile.rotate_longway(0)
        col -= tile.width
        tile.move(col, row-tile.height)
    col = 0
    row_bottom = row
    max_width = 0
    lgi('Start left wall at %s', mt.delta())
    while row < 1 and tile_ids:
        tile = board[tile_ids.pop(0)]
        tile.rotate_longway(1)
        tile.move(col-tile.width, row)
        row += tile.height
        max_width = max(max_width, tile.width)
    prev_tile = None
    col += max_width + 100
    row = row_bottom
    inner_wall_ids = list()
    lgi('Start inner wall at %s', mt.delta())
    while row < 0 and tile_ids:
        tile = board[tile_ids.pop(0)]
        inner_wall_ids.append(tile.index)
        tile.rotate_longway(1)
        if tile.height + row >= 0:
            tile.move(prev_tile.col + prev_tile.width, 0 - tile.height)
            break
        tile.move(col, row)
        row += tile.height
        prev_tile = tile
    lgi('end initial placement at %s', mt.delta())
    return tile_ids, col + max_width + 100, row_bottom, inner_wall_ids


def _move_left(board, tile_ids, mt):
    furthest_left = list()
    cb = board.make_cover_board()
    lgi('cover board done at %s', mt.delta())
    for tile in (board[_] for _ in tile_ids):
        if mt.is_over():
            lgi('not even done with furthest left')
            break
        min_col = -sys.maxint
        for row in range(tile.row, tile.row+tile.height):
            min_col = max(min_col, cb.find_min_col(tile.col-1, row))
        #lgi('for %s furthest left is %d', tile, min_col)
        furthest_left.append(min_col)
    lgi('furthest left at %s : %s', mt.delta(), furthest_left)
    sliders = list()
    for left_col, tile_id in zip(furthest_left, tile_ids):
        tile = board[tile_id]
        if left_col == -1:
            sliders.append(tile)
        else:
            tile.move(left_col+1, tile.row)
    lgi('left with %d sliders at %s', len(sliders), mt.delta())
    cb = board.make_cover_board()
    for tile in sliders:
        if mt.is_over():
            break
        # see what is one row beneath me
        min_col1 = cb.find_min_col(tile.col-1, tile.row - 1)
        min_col2 = cb.find_min_col(tile.col-1, tile.row + tile.height)
        if min_col1 == -1:
            min_col = min_col2
        elif min_col2 == -1:
            min_col = min_col1
        else:
            min_col = min(min_col1, min_col2)
        if min_col != -1:
            tile.move(min_col+1, tile.row)
            #lgi('slid1 %s', tile)
    cb = board.make_cover_board()
    lgi('sliders stage 2 at %s', mt.delta())
    for tile in sliders:
        if mt.is_over():
            break
        # see what is one row beneath me
        min_col1 = cb.find_min_col(tile.col-1, tile.row - 1)
        min_col2 = cb.find_min_col(tile.col-1, tile.row + tile.height)
        if min_col1 == -1:
            min_col = min_col2
        elif min_col2 == -1:
            min_col = min_col1
        else:
            min_col = min(min_col1, min_col2)
        if min_col != -1:
            tile.move(min_col+1, tile.row)
            #lgi('slid2 %s', tile)


def box_layout(board, mt):
    tile_ids, col, row_bottom, inner_wall_ids = _outside_box(board, mt)
    # for now just place the remaining outside the box
    row = 1050
    my_col = 0
    for tile in (board[_] for _ in tile_ids):
        tile.move(my_col, row)
        my_col += tile.width
    lgi('At %s done with placement phase 1', mt.delta())
    tile_ids = list(reversed(tile_ids))
    lgi('final at %s (%d): %s', mt.delta(), len(tile_ids), tile_ids)
    total_height = 0
    for tile in (board[_] for _ in tile_ids):
        total_height += tile.min_dim
    spacing = (abs(row_bottom)-total_height) / (len(tile_ids))
    row = row_bottom+1
    while tile_ids:
        tile = board[tile_ids.pop(0)]
        tile.rotate_longway(0)
        tile.move(0, row)
        row += tile.height + spacing
    lgi('left: %s %s', tile_ids, inner_wall_ids)
    lgi('enter move left at %s', mt.delta())
    if mt.is_over():
        return
    _move_left(board, inner_wall_ids, mt)


def simple_layout(board):
    col, row = 0, 0
    by_col = list()
    entries = list()
    max_width = 0
    for tile in board.get_by_max_dim():
        tile.move(col, row)
        if tile.height < tile.width:
            pass
        else:
            tile.flip()
        row += tile.height
        max_width = max(max_width, tile.width)
        entries.append(tile.index)
        if row > 12000:
            row = 0
            col += max_width
            by_col.append(entries)
            lgi('by col: %s', entries)
            entries = list()
    if entries:
        by_col.append(entries)
    return by_col


def max_width_in_column(board, by_col):
    for col_number, entries in enumerate(by_col):
        max_width = 0
        min_max_col_row = [sys.maxint, -sys.maxint, sys.maxint, -sys.maxint]
        for tile in (board[_] for _ in entries):
            max_width = max(max_width, tile.width)
            min_max_col_row[0] = min(min_max_col_row[0], tile.col)
            min_max_col_row[1] = max(min_max_col_row[1], tile.col+tile.width)
            min_max_col_row[2] = min(min_max_col_row[2], tile.row)
            min_max_col_row[3] = max(min_max_col_row[3], tile.row+tile.height)
        lgi('Column %d goes from (%d, %d) to (%d, %d) max width: %d',
            col_number, min_max_col_row[0], min_max_col_row[2], min_max_col_row[1], min_max_col_row[3], max_width)
        for tile in (board[_] for _ in entries):
            if tile.width < tile.height <= max_width:
                # can flip
                tile.flip()
                lgi('flipped', tile)
        row = board[entries[0]].row + board[entries[0]].height
        for tile in (board[_] for _ in entries[1:]):
            delta_row = tile.row - row
            if delta_row > 0:
                #tile.move(tile.col, tile.row-delta_row)
                lgi('squashed', tile)
            row = tile.row + tile.height
        # now put the top on on the bottom
        t = board.tiles[entries[-1]]
        t.move(min_max_col_row[0], min_max_col_row[2] - t.height)
        bottom_tile, top_tile =  board.tiles[entries[-1]], board.tiles[entries[-2]]
        if top_tile.width < bottom_tile.width:
            top_tile.bump(bottom_tile.width-top_tile.width, 0)
        i = 1
        while i < len(entries):
            t0 = board[entries[i-1]]
            t1 = board[entries[i]]
            if t0.width == t1.width:
                #lgi('flip blocks: %s %s', t0, t1)
                i+=2
                pass
            else:
                #lgi('different widths: %s %s', t0, t1)
                i+=1


class RectanglesAndHoles(object):
    def __init__(self):
        pass

    def place(self, A, B):
        mt = MyTimer()
        board = Board(A, B)
        box_layout(board, mt)
        lgi('Total time %s', mt.delta())
        sys.stderr.flush()
        return board.array_out()
