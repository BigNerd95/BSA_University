import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import random
from Rect import Rect
import math

def drawRect(bin, rectangles):

	patches = []
	patches.append(Rectangle((bin.x,bin.y),bin.w,bin.h))

	for r in rectangles:
		patches.append(Rectangle((r.x,r.y),r.w,r.h))
	
	pc = PatchCollection(patches, facecolor='None', alpha=1, edgecolor='r')
	
	fig, ax = plt.subplots(1)
	
	ax.add_collection(pc)
	
	#imposta coordinate visuale piano cartesiano
	ax.set_xlim((-10,bin.w+100),auto=True)
	ax.set_ylim((-10,bin.h+100),auto=True)
	
	plt.show()

def greedyShelf(bin, rectangles):
	rect_inserted = []
	rectangles.sort(key=lambda x: (x.h,x.w), reverse=True)#(x.h,x.w), reverse=True)

	sheight=rectangles[0].h

	hlimit=False

	y=0
	i=0

	while(not hlimit):
		x=0
		while(i < len(rectangles) and x+rectangles[i].w<bin.w):
			#rectangles.pop(0)
			rectangles[i].x=x
			rectangles[i].y=y
			rect_inserted.append(rectangles[i])

			x+=rectangles[i].w
			i+=1

		if i >= len(rectangles):
			hlimit=True
		else:
			# sale di scaffale
			w_rimanente = bin.w - x
			y_rimanente = sheight

			y+=sheight
			sheight=rectangles[i].h
			
			if y+sheight > bin.h:
				hlimit=True

	return rect_inserted

def main():
	bin=Rect(0,0,500,500)

	rectangles=[]
	
	for i in range(1000):
		w = random.randint(10, 50)
		h = random.randint(50, 100)
		rectangles.append(Rect(0,0,h,w))

	rect_inserted = greedyShelf(bin, rectangles)

	drawRect(bin, rect_inserted)

if __name__ == '__main__':
		main()