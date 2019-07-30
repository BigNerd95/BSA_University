from Item import Item
from Guillotine import Guillotine

class Shelf:
	"""
	Shelf class represents of row of items on the sheet
	"""
	def __init__(self, width: int, height: int, v_offset: int = 0) -> None:
		self.height = height
		self.width = width
		self.available_width = self.width
		self.area = self.available_width * self.height
		self.vertical_offset = v_offset
		self.items = [] # type: List[Item]
		self.wastemap = Guillotine(self, 0, 0, rotation = False, heuristic='best_area')

	def __repr__(self):
		return str(self.__dict__)
		#return "Shelf(Available Width=%r, Height=%r, Vertical Offset=%r)" % (self.available_width, self.y, self.vertical_offset)

	def _item_fits_shelf(self, item, rotation = False) -> bool:
		if ((item.width <= self.available_width and item.height <= self.height) or
		   (rotation and item.height <= self.available_width and item.width <= self.height)):
			return True
		return False

	def insert(self, item: Item, rotation: bool=True) -> bool:
		if item.width <= self.available_width and item.height <= self.height:
			item.x, item.y = (self.width - self.available_width, self.vertical_offset)
			self.items.append(item)
			self.available_width -= item.width
			self.area = self.available_width * self.height
			return True
		if rotation:
			if (item.height <= self.available_width and
				item.width <= self.height):
				item.rotate()
				item.x, item.y = (self.width - self.available_width, self.vertical_offset)
				self.items.append(item)
				self.available_width -= item.width
				self.area = self.available_width * self.width
				return True
		return False