from matplotlib.patches import Rectangle

class Rect:
	def __init__(self,x,y,h,w):
		#self.r = Rectangle((x,y),w,h)
		self.area = h*w
		self.x=x
		self.y=y
		self.h = h
		self.w = w
		