#from Guillotine import Guillotine
from Item import Item

class Container(Item):
    """
    Items class for rectangles inserted into sheets
    """
    ID=0

    def __init__(self, width, height, x=0, y=0, rotated=False):
        super(Container,self).__init__(width, height)        
        self.items = []
        self.shelves = []
        #self.wastemap = Guillotine(0, 0, rotation = False, heuristic='best_area')
        self.available_height=height
        self.id=Container.ID
        Container.ID+=1

    def areaPiecesRatio(self):
        areaItems=0

        for item in self.items:
            areaItems+=item.area

        return areaItems/len(self.items)

    def compare(self, container):
        return self.id == container.id