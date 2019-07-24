import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import random
import math
from Guillotine import FreeRectangle
from Item import Item
from Container import Container
from Shelf import Shelf
import Parser
import sys


def drawRect(instance):

    #print(rectangles)

    containers=instance.containers

    patches1 = []
    patches2 = []
    patches3 = []



    for cont in containers:
        patches1.append(Rectangle((cont.x,cont.y),cont.width,cont.height))

        for r in cont.items:
            patches2.append(Rectangle((r.x,r.y),r.width,r.height))

        for r in cont.wastemap.freerects:
            patches3.append(Rectangle((r.x,r.y),r.width,r.height))
    
    pc1 = PatchCollection(patches1, facecolor='None', alpha=1, edgecolor='blue', linewidths=3, zorder=3)
    pc2 = PatchCollection(patches2, facecolor='red', alpha=1, edgecolor='black', zorder=2)
    pc3 = PatchCollection(patches3, facecolor='green', alpha=1, edgecolor='green', zorder=1)
    
    fig, ax = plt.subplots(1)
    
    ax.add_collection(pc1)
    ax.add_collection(pc2)
    ax.add_collection(pc3)
    
    #imposta coordinate visuale piano cartesiano
    ax.set_xlim((-100,instance.container_w+100),auto=True)
    ax.set_ylim((-100,instance.container_w+100),auto=True)

    plt.axis('equal')
    plt.show()


def greedyShelf(instance):
    #rect_inserted = []
    rectangles = instance.items
    rectangles.sort(key=lambda x: (x.height,x.width), reverse=True)#(x.h,x.w), reverse=True)

    cont_height = instance.container_h

    sheight=rectangles[0].height	

    #se il primo rettangolo sta nel bin comincio a inserire	
    if(sheight <= cont_height):
        i=0
        while i < len(rectangles):			
            cont=Container(instance.container_h, instance.container_w,0,0)
            instance.containers.append(cont)

            hlimit=False

            y=cont_height

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
    else:
        raise Exception("Rettangolo più alto non sta nel bin")
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
    
    
    #rectangles = []

    #for i in range(100):
    #	w = random.randint(10, 50)
    #	h = random.randint(50, 100)
    #	rectangles.append(Item(h,w))

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        instances = Parser.parse(filepath)
        #for i in instances:
        #    print(i)
        #rectangles.append(Rect(0,0,h,w))

        #wastemap = Guillotine(0, 0, rotation = False, heuristic='best_area')
        #print(len(instances))
        greedyShelf(instances[0])
        #greedyShelf(cont, instances[0].items)

        drawRect(instances[0])
    else:
        print("Manca argomento")

if __name__ == '__main__':
        main()