import sys
import RectanglesAndHoles


def read_int():
    return int(sys.stdin.readline().strip())


#ERROR: rectangles 0 (0-based) and 1 (0-based) in your solution overlap. Rectangle 0 is (0, 0) - (204, 961). Rectangle 1 is (0, 204) - (496, 511).
# if (overlap(LX[i], RX[i], LX[j], RX[j]) && overlap(LY[i], RY[i], LY[j], RY[j])) {
#   System.err.println("ERROR: rectangles " + i + " (0-based) and " + j + " (0-based) in your solution overlap. Rectangle " + i +
#            " is (" + LX[i] + ", " + LY[i] + ") - (" + RX[i] + ", " + RY[i] + "). Rectangle " + j +
#            " is (" + LX[j] + ", " + LY[j] + ") - (" + RX[j] + ", " + RY[j] + ").");
#    return -1;
#}

#    boolean overlap(int A, int B, int C, int D) {
#        return Math.max(A, C) < Math.min(B, D);
#    }

# so overlap(0, 204, 0, 496) & overlap(0, 961, 204, 511)
#   max(0,0) < min(204,496) & max(0, 204) < min(961, 511)
#    0 < 204 & 204 < 961
#   true & true


def main(args):
    N = read_int()
    A = [read_int() for _ in range(N)]
    B = [read_int() for _ in range(N)]
    r = RectanglesAndHoles.RectanglesAndHoles()
    ret = r.place(A, B)
    for r in ret:
        print r
    sys.stdout.flush()

if __name__ == '__main__':
    main(sys.argv)