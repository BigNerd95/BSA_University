import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import random
import math
from Guillotine import FreeRectangle
from Item import Item
from Container import Container
from Shelf import Shelf

def drawRect(cont):

	#print(rectangles)

	patches1 = []
	patches2 = []
	patches3 = []

	patches1.append(Rectangle((cont.x,cont.y),cont.width,cont.height))

	for r in cont.items:
		patches2.append(Rectangle((r.x,r.y),r.width,r.height))

	for r in cont.wastemap.freerects:
		patches3.append(Rectangle((r.x,r.y),r.width,r.height))
	
	pc1 = PatchCollection(patches1, facecolor='None', alpha=1, edgecolor='b')
	pc2 = PatchCollection(patches2, facecolor='None', alpha=1, edgecolor='r')
	pc3 = PatchCollection(patches3, facecolor='None', alpha=1, edgecolor='g')
	
	fig, ax = plt.subplots(1)
	
	ax.add_collection(pc1)
	ax.add_collection(pc2)
	ax.add_collection(pc3)
	
	#imposta coordinate visuale piano cartesiano
	ax.set_xlim((-100,cont.width+100),auto=True)
	ax.set_ylim((-100,cont.height+100),auto=True)
	
	plt.show()

#def intraNeighborhood(cont):


def greedyShelf(cont, rectangles):
	#rect_inserted = []
	rectangles.sort(key=lambda x: (x.height,x.width), reverse=True)#(x.h,x.w), reverse=True)

	sheight=rectangles[0].height

	hlimit=False

	y=cont.height
	i=0

	#se il primo rettangolo sta nel bin comincio a inserire
	if(sheight <= cont.height):
		while(not hlimit):						
			sh=Shelf(cont.width, sheight, cont.height-y)
			cont.shelves.append(sh)
			y-=sheight
			
			#finchè ci stanno inserisce rettangoli nello scaffale			
			while(i < len(rectangles) and sh._item_fits_shelf(rectangles[i])):
				sh.insert(rectangles[i])
				cont.items.append(rectangles[i])
				i+=1
			
			#controlla se sono finiti i rettangoli oppure se lo scaffale nuovo supererebbe l'altezza massima
			if i >= len(rectangles):
				hlimit=True
			else:
				sheight=rectangles[i].height
				
				if y - sheight <= 0:
					hlimit=True

					if y > 0:
						#aggiunge lo spazio vuoto in alto alla wastemap
						freeRect = FreeRectangle(cont.width, y, cont.x, cont.height-y)
						cont.wastemap.freerects.add(freeRect)						
					
			#aggiunge lo spazio libero dello scaffale alla wastemap
			_add_to_wastemap(cont,sh)

	#return rect_inserted,wastemap,shelves

def _add_to_wastemap(cont,shelf):
		""" Add lost space above items to the wastemap """
		# Add space above items to wastemap
		for item in shelf.items:
			if item.height < shelf.y:
				freeWidth = item.width
				freeHeight = shelf.y - item.height
				freeX = item.x
				freeY = item.height + shelf.vertical_offset
				freeRect = FreeRectangle(freeWidth,	freeHeight, freeX, freeY)
				cont.wastemap.freerects.add(freeRect)
		# Move remaining shelf width to wastemap
		if shelf.available_width > 0:
			freeWidth = shelf.available_width
			freeHeight = shelf.y
			freeX = cont.width - shelf.available_width
			freeY = shelf.vertical_offset
			freeRect = FreeRectangle(freeWidth, freeHeight, freeX, freeY)
			cont.wastemap.freerects.add(freeRect)
		# Close Shelf
		shelf.available_width = 0
		# Merge rectangles in wastemap
		cont.wastemap.rectangle_merge()

def main():
	cont=Container(500,500,0,0)
	
	rectangles = []

	for i in range(100):
		w = random.randint(10, 50)
		h = random.randint(50, 100)
		rectangles.append(Item(h,w))
		#rectangles.append(Rect(0,0,h,w))

	#wastemap = Guillotine(0, 0, rotation = False, heuristic='best_area')

	greedyShelf(cont, rectangles)

	drawRect(cont)

if __name__ == '__main__':
		main()