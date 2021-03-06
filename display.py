class Display(object):
    """
    This is a library for doing a comprehensive, realtime display of all the states within the EKF.
    """
    
    # Hacks for singleton functionality (is there a better way to do this?)
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Display, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.categories = {}
        try:
            import curses
            self.curses_available = True
            self.screen = curses.initscr()
        except:
            print "Curses library not installed defaulting to standard console output"
            self.curses_available = False

    def __del__(self):
        if self.curses_available:
            curses.endwin()

    def register_scalar(self, label, scalar, category="Internal states"):
        self.categories.setdefault(category, {"scalars":{},"matrices":{}})
        self.categories[category]['scalars'][label] = scalar

    def register_scalars(self, scalars, category="Internal states"):
        for label, scalar in scalars.items():
            self.register_scalar(label, scalar, category)

    def register_matrix(self, label, matrix, category="Internal states"):
        self.categories.setdefault(category, {"scalars":{},"matrices":{}})
        self.categories[category]['matrices'][label] = matrix

    def register_matrices(self, matrices, category="Internal states"):
        for label, matrix in matrices.items():
            self.register_matrix(label, matrix, category)

    def display_matrix(self, m, x, y, precision=2, title=None):
        a, b = self.get_matrix_display_size(m, precision=precision)
        c, d = self.screen.getmaxyx()
        if x + a < c and y + b < d: # if there's space to draw it, go for it
            rows, cols = m.shape
            if title:
                self.screen.addstr(x, y, title)
                x += 1
            self.screen.addstr(x, y, "[")
            self.screen.addstr(x, cols*(4+precision)+y+1, "]")
            self.screen.addstr(rows+x-1, y, "[")
            self.screen.addstr(rows+x-1, cols*(4+precision)+y+1, "]")
            for row in range(rows):
                for col in range(cols):
                    self.screen.addstr(row+x, col*(4+precision)+y+1, "%+.*f," % (precision, m[row, col]))
            return rows+x, cols*(4+precision)+y+2 # returns the position of the bottom right corner plus one for padding
        else: # not enough room to draw the matrix
            return x + 1, y + 1

    def get_matrix_display_size(self, m, precision=2, title=True):
        rows, cols = m.shape
        if title:
            rows += 1
        return rows, cols*(4+precision)+1 # returns the position of the bottom right corner plus one for padding

    def display_state(self, precision):
        self.screen.erase()
        rows, cols = self.screen.getmaxyx()
        self.screen.addstr(0, 0, "Shumai: the Extended Kalman Filter for aircraft")
        i = 1
        x, y = 2, 0
        for category in sorted(self.categories.keys(), key=str.lower):
            self.screen.addstr(x, y, "%s:" % category)
            x += 2
            for s in sorted(self.categories[category]['scalars'].keys(), key=str.lower):
                if y + precision + len(s) > cols:
                    x += 1
                    y = 0
                if x < rows and y + precision + len(s) < cols:
                    self.screen.addstr(x, y, "%s: %+0.*f" % (s, precision, self.categories[category]['scalars'][s]))
                y += 20 + precision
                i += 1
            if len(self.categories[category]['scalars']) > 0:
                x, y = x + 2, 0
            maxheight = 0
            for m in sorted(self.categories[category]['matrices'].keys(), key=str.lower):
                matrix = self.categories[category]['matrices'][m]
                a, b = self.get_matrix_display_size(matrix, precision=precision)
                if a > maxheight:
                    maxheight = a
                if b + y > cols-10:
                    y = 0
                    x += maxheight + 1
                    maxheight = 0
                c, d = self.display_matrix(matrix, x, y, precision=precision, title=m)
                y += b + 3
            if len(self.categories[category]['matrices']) > 0:
                x += maxheight + 2
            else:
                x += maxheight + 1
            y = 0
        # point the cursor in the bottom right corner so it doesn't hide anything
        self.screen.move(rows-1, cols-1)

    def draw(self, precision=4):
        self.display_state(precision=precision)
        rows, cols = self.screen.getmaxyx()
        self.screen.move(rows-1, cols-1)
        self.screen.refresh()
        self.scalars = {}
        self.matrices = {}
