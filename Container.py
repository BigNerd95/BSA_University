from Guillotine import Guillotine

class Container:
    """
    Items class for rectangles inserted into sheets
    """
    def __init__(self, width, height, x=0, y=0, rotated=False) -> None:
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.area = self.width * self.height
        self.rotated = rotated
        self.id = 0
        self.items = []
        self.shelves = []
        self.wastemap = Guillotine(0, 0, rotation = False, heuristic='best_area')


    def __repr__(self):
        return 'Item(width=%r, height=%r, x=%r, y=%r)' % (self.width, self.height, self.x, self.y)


    def rotate(self) -> None:
        self.width, self.height = self.height, self.width
        self.rotated = False if self.rotated == True else True