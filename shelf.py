from Item import Item

class Shelf:
	"""
	Shelf class represents of row of items on the sheet
	"""
	def __init__(self, x: int, y: int, v_offset: int = 0) -> None:
		self.y = y
		self.x = x
		self.available_width = self.x
		self.area = self.available_width * self.y
		self.vertical_offset = v_offset
		self.items = [] # type: List[Item]

	def __repr__(self):
		return str(self.__dict__)
		#return "Shelf(Available Width=%r, Height=%r, Vertical Offset=%r)" % (self.available_width, self.y, self.vertical_offset)

	def _item_fits_shelf(self, item, rotation = False) -> bool:
		if ((item.width <= self.available_width and item.height <= self.y) or
		   (rotation and item.height <= self.available_width and item.width <= self.y)):
			return True
		return False

	def insert(self, item: Item, rotation: bool=True) -> bool:
		if item.width <= self.available_width and item.height <= self.y:
			item.x, item.y = (self.x - self.available_width, self.vertical_offset)
			self.items.append(item)
			self.available_width -= item.width
			self.area = self.available_width * self.y
			return True
		if rotation:
			if (item.height <= self.available_width and
				item.width <= self.y):
				item.rotate()
				item.x, item.y = (self.x - self.available_width, self.vertical_offset)
				self.items.append(item)
				self.available_width -= item.width
				self.area = self.available_width * self.y
				return True
		return False