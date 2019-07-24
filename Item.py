"""
2D Item class.
"""
class Item:
    """
    Items class for rectangles inserted into sheets
    """
    ID = -1

    def __init__(self, width, height, x=0, y=0, rotated=False) -> None:
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.area = self.width * self.height
        self.rotated = rotated
        self.id = Item.setID()

    def setID():
        Item.ID += 1
        return Item.ID

    def __repr__(self):
        return 'Item(width=%r, height=%r, x=%r, y=%r)' % (self.width, self.height, self.x, self.y)


    def rotate(self) -> None:
        self.width, self.height = self.height, self.width
        self.rotated = False if self.rotated == True else True