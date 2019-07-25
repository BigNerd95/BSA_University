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

def draw_bin(container, x):
    patches1 = []
    patches2 = []
    patches3 = []

    patches1.append(Rectangle((container.x, container.y), container.width, container.height))

    for r in container.items:
        patches2.append(Rectangle((r.x,r.y),r.width,r.height))

    for r in container.wastemap.freerects:
        patches3.append(Rectangle((r.x,r.y),r.width,r.height))

    pc1 = PatchCollection(patches1, facecolor='None', alpha=1, edgecolor='blue', linewidths=3, zorder=3)
    pc2 = PatchCollection(patches2, facecolor='red', alpha=1, edgecolor='black', zorder=1)
    pc3 = PatchCollection(patches3, facecolor='green', alpha=1, edgecolor='black', zorder=2)    

    x.add_collection(pc1)
    x.add_collection(pc2)
    x.add_collection(pc3)

def drawRect(instance):

    #print(len(instance.items))

    containers=instance.containers

    

    #attenzione                 ceil
    fig, ax = plt.subplots(math.floor(math.sqrt(len(containers))), math.ceil(math.sqrt(len(containers))))
    
    if len(containers) == 1:
        draw_bin(containers[0], ax)
        ax.axis('equal')
        ax.axis("off")
    else:
        i=0
        for y in ax:
            for x in y:
                if(i < len(containers)):
                    draw_bin(containers[i], x)
                    i+=1
                x.axis('equal')
                x.axis("off")

    plt.title("Problem "+instance.rinst)
    plt.show(block=True)
    #plt.pause(0.5)
    #plt.close()

def rotateWide(rectangles):
    for r in rectangles:
        if(r.width > r.height):
            r.rotate()
    return rectangles

def greedyShelf(instance):
    #rect_inserted = []
    rectangles = instance.items
    rectangles = rotateWide(rectangles)
    rectangles.sort(key=lambda x: (x.height,x.width), reverse=True)#(x.h,x.w), reverse=True)

    cont_height = instance.container_h

    shelf_height=rectangles[0].height    

    #se il primo rettangolo sta nel bin comincio a inserire 
    if(shelf_height <= cont_height):
        i=0        
        while i < len(rectangles):          
            cont=Container(instance.container_h, instance.container_w,0,0)
            instance.containers.append(cont)

            hlimit=False

            available_height=cont_height
            
            while(not hlimit):                      
                
                sh=Shelf(cont.width, shelf_height, cont.height-available_height)
                cont.shelves.append(sh)
                available_height-=shelf_height
                
                #finchè ci stanno inserisce rettangoli nello scaffale           
                while(i < len(rectangles) and sh._item_fits_shelf(rectangles[i])):
                    sh.insert(rectangles[i])
                    cont.items.append(rectangles[i])
                    i+=1
                
                #controlla se sono finiti i rettangoli oppure se lo scaffale nuovo supererebbe l'altezza massima
                if i >= len(rectangles):
                    hlimit=True
                else:
                    
                    shelf_height = rectangles[i].height
                    
                    if available_height < shelf_height:
                        hlimit=True
                        #print(y)
                
                if available_height < shelf_height or i >= len(rectangles):
                    #aggiunge lo spazio vuoto in alto alla wastemap
                    freeRect = FreeRectangle(cont.width, available_height, cont.x, cont.height-available_height)
                    cont.wastemap.freerects.add(freeRect)
                    #print(i)
                    
                      
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
                freeRect = FreeRectangle(freeWidth, freeHeight, freeX, freeY)
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
    #   w = random.randint(10, 50)
    #   h = random.randint(50, 100)
    #   rectangles.append(Item(h,w))

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        instances = Parser.parse(filepath)
        #for i in instances:
        #    print(i)
        #rectangles.append(Rect(0,0,h,w))

        #wastemap = Guillotine(0, 0, rotation = False, heuristic='best_area')
        #print(len(instances))

        #print(instances[9])
        #greedyShelf(instances[9])
        #drawRect(instances[9])
        instances = instances[40:41]

        for instance in instances:
            print(instance)
            greedyShelf(instance)
            drawRect(instance)
            
    else:
        print("Manca argomento")

if __name__ == '__main__':
        main()