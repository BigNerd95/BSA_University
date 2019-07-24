import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import random
from Rect import Rect
import math
from Guillotine import Guillotine
from Guillotine import FreeRectangle
from Item import Item
from Shelf import Shelf

def drawRect(bin, rectangles, wastemap, shelves):

	#print(rectangles)

	patches1 = []
	patches2 = []
	patches3 = []

	patches1.append(Rectangle((bin.x,bin.y),bin.width,bin.height))

	for r in rectangles:
		patches2.append(Rectangle((r.x,r.y),r.width,r.height))

	for r in wastemap.freerects:
		patches3.append(Rectangle((r.x,r.y),r.width,r.height))
	
	pc1 = PatchCollection(patches1, facecolor='None', alpha=1, edgecolor='b')
	pc2 = PatchCollection(patches2, facecolor='None', alpha=1, edgecolor='r')
	pc3 = PatchCollection(patches3, facecolor='None', alpha=1, edgecolor='g')
	
	fig, ax = plt.subplots(1)
	
	ax.add_collection(pc1)
	ax.add_collection(pc2)
	ax.add_collection(pc3)
	
	#imposta coordinate visuale piano cartesiano
	ax.set_xlim((-100,bin.width+100),auto=True)
	ax.set_ylim((-100,bin.height+100),auto=True)
	
	plt.show()

def greedyShelf(bin, shelves, rectangles, wastemap):
	rect_inserted = []
	rectangles.sort(key=lambda x: (x.height,x.width), reverse=True)#(x.h,x.w), reverse=True)

	sheight=rectangles[0].height

	hlimit=False

	y=bin.height
	i=0

	if(sheight <= bin.height):
		while(not hlimit):			
			#x=bin.w
			#pare non mi debba preoccupare di available height del bin
			sh=Shelf(bin.width, sheight, bin.height-y)
			shelves.append(sh)
			y-=sheight

			#while(i < len(rectangles) and x+rectangles[i].width<bin.width):						
			while(i < len(rectangles) and sh._item_fits_shelf(rectangles[i])):
				#print("entrato while while")
				#rectangles.pop(0)
				#rectangles[i].x=x
				#rectangles[i].y=y
				#Inseriamo nello scaffale
				sh.insert(rectangles[i])
				rect_inserted.append(rectangles[i])
	
				#x+=rectangles[i].width
				i+=1
	
			if i >= len(rectangles):
				hlimit=True
			else:
				# sale di scaffale
				#w_rimanente = bin.width - x
				#y_rimanente = sheight
	
				#y+=sheight
				sheight=rectangles[i].height
				
				if y - sheight <= 0:
					hlimit=True				
					
				#if y+sheight > bin.height:
				#	hlimit=True
				#else:
				#	_add_to_wastemap(bin,sh,wastemap)
			_add_to_wastemap(bin,sh,wastemap)

	return rect_inserted,wastemap,shelves

def _add_to_wastemap(bin,shelf,wastemap):
		""" Add lost space above items to the wastemap """
		# Add space above items to wastemap
		for item in shelf.items:
			if item.height < shelf.y:
				freeWidth = item.width
				freeHeight = shelf.y - item.height
				freeX = item.x
				freeY = item.height + shelf.vertical_offset
				freeRect = FreeRectangle(freeWidth,	freeHeight, freeX, freeY)
				wastemap.freerects.add(freeRect)
		# Move remaining shelf width to wastemap
		if shelf.available_width > 0:
			freeWidth = shelf.available_width
			freeHeight = shelf.y
			freeX = bin.width - shelf.available_width
			freeY = shelf.vertical_offset
			freeRect = FreeRectangle(freeWidth, freeHeight, freeX, freeY)
			wastemap.freerects.add(freeRect)
		# Close Shelf
		shelf.available_width = 0
		# Merge rectangles in wastemap
		wastemap.rectangle_merge()

def main():
	bin=Item(500,500,0,0)

	rectangles=[]
	shelves = []
	
	for i in range(100):
		w = random.randint(10, 50)
		h = random.randint(50, 100)
		rectangles.append(Item(h,w))
		#rectangles.append(Rect(0,0,h,w))

	wastemap = Guillotine(0, 0, rotation = False, heuristic='best_area')

	rect_inserted,wastemap,shelves = greedyShelf(bin, shelves, rectangles, wastemap)

	drawRect(bin, rect_inserted,wastemap,shelves)

if __name__ == '__main__':
		main()