from operator import attrgetter
from util import lgi
import sys


def place_row(board, tile_ids, row, col, max_col):
    placed = list()
    max_row = row
    while col < max_col and tile_ids:
        t_id = tile_ids.pop(0)
        placed.append(t_id)
        t = board[t_id]
        t.move(col, row)
        t.rotate_longway(0)
        col += t.width + 1
        max_row = max(max_row, row + t.height)
        if col > max_col:
            break
        if tile_ids:
            filler = tile_ids.pop(len(tile_ids)-1)
            t = board[filler]
            t.rotate_longway(1)
            placed.append(filler)
            t.move(col-1, row-t.height)
            col = t.col + t.width
    max_row += 1050
    return placed, max_row, col


def do_layout(board, mt):
    lgi('Have %d tiles', len(board))
    total_length = 0
    for tile in board:
        total_length += tile.max_dim
    side_length = (total_length * 0.8) / 10
    tile_ids = [_.index for _ in sorted(board, key=attrgetter('max_dim'), reverse=True)]
    row = 0
    rows = list()
    max_cols = list()
    while True:
        col = 0
        placed, max_row, max_col = place_row(board, tile_ids, row, col, side_length)
        lgi('Placed: %d, remaining: %d', len(placed), len(tile_ids))
        row = max_row
        if placed:
            rows.append(placed)
            max_cols.append(max_col)
        else:
            break
    lgi('max cols %s : %s', max_cols, sorted(max_cols))
    for _ in range(len(rows)-4):
        flatten_slices(board, rows[_], rows[_+1])
    # now take the top 3 slices and make a big square
    to_place = list()
    to_place.extend(rows[-1])
    to_place.extend(rows[-2])
    to_place.extend(rows[-3])
    make_square(board, rows[:len(rows)-3], to_place, side_length)


def make_square(board, prevs, to_place, side_length):
    tiles = [board[_] for _ in to_place]
    to_place = [_.index for _ in sorted(tiles, key=attrgetter('max_dim'), reverse=True)]
    lgi('To place: %s', to_place)
    col = 0
    row = 20000
    el_topper = list()
    while col < side_length:
        tile = board[to_place.pop(0)]
        el_topper.append(tile)
        tile.move(col, row)
        col += tile.width
    # take the remaining and make walls
    lt2 = board[prevs[-1][0]]
    left_col = 0
    left_row = lt2.row + lt2.height
    lt3 = board[prevs[-1][-1]]
    right_col = lt3.col + lt3.width
    right_row = lt3.row + lt3.height
    last_right_piece = None
    while to_place:
        tile = board[to_place.pop(0)]
        if left_row < right_row:
            tile.rotate_longway(1)
            tile.move(left_col-tile.width, left_row)
            left_row += tile.height
        else:
            tile.rotate_longway(1)
            tile.move(right_col, right_row)
            right_row += tile.height
            last_right_piece = tile
    # now move the top part down to meet walls
    for tile in el_topper:
        tile.move(tile.col, min(left_row, right_row))
    max_right_col_el = el_topper[-1].col + el_topper[-1].width
    if max_right_col_el < last_right_piece.col:
        last_right_piece.move(max_right_col_el, last_right_piece.row)


def get_highest_point(board, tile, ids):
    high_row = -sys.maxint
    for other_tile in (board[_] for _ in ids):
        if other_tile.col > tile.col + tile.width:
            break
        if other_tile.col + other_tile.width < tile.col:
            continue
        high_row = max(high_row, other_tile.row + other_tile.height)
    return high_row


def flatten_slices(board, bottom_row, top_row):
    for tile in (board[_] for _ in top_row):
        high_row = get_highest_point(board, tile, bottom_row)
        lgi('High row for %s is %d', tile, high_row)
        tile.move(tile.col, high_row)
