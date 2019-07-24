from Guillotine import Guillotine
from Item import Item

class Container(Item):
    """
    Items class for rectangles inserted into sheets
    """
    def __init__(self, width, height, x=0, y=0, rotated=False):
        super(Container,self).__init__(width, height)        
        self.items = []
        self.shelves = []
        self.wastemap = Guillotine(0, 0, rotation = False, heuristic='best_area')