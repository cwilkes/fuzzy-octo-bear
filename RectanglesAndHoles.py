

class RectanglesAndHoles(object):
    def __init__(self):
        pass

    def place(self, A, B):
        col = 0
        row = 0
        ret = list()
        max_height = 0
        for w, h in zip(A, B):
            if h < w < max_height:
                ret.append((col, row, 0))
                row += h
                max_height = max(max_height, w)
            else:
                ret.append((col, row, 1))
                row += w
                max_height = max(max_height, h)
            if row > 15000:
                row = 0
                col += max_height
        ret2 = list()
        for r in ret:
            for _ in r:
                ret2.append(_)
        return ret2