import matplotlib.pyplot as plt
plt.rcParams['toolbar'] = 'toolmanager'
from matplotlib.backend_tools import ToolBase, ToolToggleBase
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

def label(rect, text, bin):
    x = rect.get_x() + rect.get_width()/2
    y = rect.get_y() + rect.get_height()/2
    bin.text(x, y, text, ha="center", va='center', family='sans-serif', size=6)

def draw_bin(container, x):
    patches1 = []
    patches2 = []
    patches3 = []

    patches1.append(Rectangle((container.x, container.y), container.width, container.height))

    for r in container.items:
        new_rect = Rectangle((r.x,r.y), r.width, r.height, label="x")
        patches2.append(new_rect)
        label(new_rect, r.id, x)

    for r in container.wastemap.freerects:
        patches3.append(Rectangle((r.x,r.y),r.width,r.height))

    pc1 = PatchCollection(patches1, facecolor='None', alpha=1, edgecolor='blue', linewidths=3, zorder=3)
    pc2 = PatchCollection(patches2, facecolor='red', alpha=1, edgecolor='black', zorder=1)
    pc3 = PatchCollection(patches3, facecolor='green', alpha=1, edgecolor='black', zorder=2)    

    x.add_collection(pc1)
    x.add_collection(pc2)
    x.add_collection(pc3)

def drawRect(fig, instance, block):
    fig.clear()


    #print(len(instance.items))

    containers=instance.containers


    #attenzione                 ceil
    ax = fig.subplots(math.floor(math.sqrt(len(containers))), math.ceil(math.sqrt(len(containers))))
    
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

    fig.suptitle("Used Bins: "+str(len(containers))+"    Lower bound: "+str(math.floor(instance.binLowerBound()))+"    Global wasted area: "+ str(math.floor(instance.wastedArea()))+"%")
    

    #fig.canvas.manager.toolbar.add_tool(tm.get_tool("newtool"), "toolgroup")

    plt.show(block)

    #plt.pause(0.5)
    #plt.close()

def shiftAll(rect, shelf, container):
    for r in shelf.items:
        if(r.x > rect.x):
            if(r.y + r.height < shelf.vertical_offset+shelf.height):                
                freeRect=getTopFreeRect(r, container)
                if(freeRect):
                    #print("getTopFreeRect")
                    freeRect.x-=rect.width
            r.x-=rect.width

    #lo scaffale non è pieno quindi c'è un rettangolo libero da estendere
    if(shelf.available_width > 0):
        #last_rect = shelf.items[len(shelf.items)-1]
        #shelf.width - last_rect.x + last_rect.width
        freeRect=getShelfFreeRect(shelf, container)

        shelf.available_width += rect.width

        freeRect.x=shelf.width-shelf.available_width
        freeRect.width+=rect.width

    else:#lo scaffale era pieno, quindi non c'è il rettangolo libero allora lo creo
        freeRect = FreeRectangle(rect.width, shelf.height, shelf.width-rect.width, shelf.vertical_offset)
        container.wastemap.freerects.add(freeRect)
        shelf.available_width+=rect.width

def moveRect(rect, freeRect, shelf, container):
    shiftAll(rect, shelf, container)
    rect.x=freeRect.x
    rect.y=freeRect.y

    freerects = container.wastemap._split_free_rect(rect, freeRect)
    for r in freerects:
        container.wastemap.freerects.add(r)
    container.wastemap.freerects.remove(freeRect)

def getTopFreeRect(rect, container):
    for r in container.wastemap.freerects:
        if(rect.x==r.x and rect.y+rect.height==r.y):
            return r

def getShelfFreeRect(shelf, container):
    for r in container.wastemap.freerects:
        if(r.x == shelf.width - shelf.available_width and r.y==shelf.vertical_offset):
            return r

def intraNeighborhood(instance):
    #best_height = 0
    best_width = 0
    best = None

    for container in instance.containers:             
        for i in range(0, len(container.shelves)-1): 
            
            freeRect=getShelfFreeRect(container.shelves[i],container)

            if(freeRect):
                for r in container.shelves[i+1].items:
                    if(r.width <= freeRect.width and r.width > best_width):
                        best=r
                        best_width=r.width

                if(best!=None):
                    moveRect(best, freeRect, container.shelves[i+1], container)
                    best=None
                    best_width=0
            #else:
                #print("Non c'è il free rect")

        container.wastemap.rectangle_merge()

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
            if item.height < shelf.height:
                freeWidth = item.width
                freeHeight = shelf.height - item.height
                freeX = item.x
                freeY = item.height + shelf.vertical_offset
                freeRect = FreeRectangle(freeWidth, freeHeight, freeX, freeY)
                cont.wastemap.freerects.add(freeRect)
        # Move remaining shelf width to wastemap
        if shelf.available_width > 0:
            freeWidth = shelf.available_width
            freeHeight = shelf.height
            freeX = cont.width - shelf.available_width
            freeY = shelf.vertical_offset
            freeRect = FreeRectangle(freeWidth, freeHeight, freeX, freeY)
            cont.wastemap.freerects.add(freeRect)
        # Close Shelf
        #shelf.available_width = 0
        # Merge rectangles in wastemap
        cont.wastemap.rectangle_merge()

def genGUI():
    fig = plt.figure()
    #fig.canvas.manager.toolbar._Button("PREVIOUS", "back_large", <ACTION_PREV>)
    #fig.canvas.manager.toolbar._Button("NEXT", "forward_large", <ACTION_NEXT>)
    fig.show()

class mycallback(ToolBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def trigger(self, *args, **kwargs):
        global fig
        fig.clear()
        plt.show()
        print("welaaa")

class nextInstance(ToolBase):

    def __init__(self, *args, instances, **kwargs):
        self.instances = instances
        self.counter = 0
        super().__init__(*args, **kwargs)

    def trigger(self, *args, **kwargs):
        global fig
        instance = self.instances[self.counter]
        self.counter += 1
        print(instance)
        greedyShelf(instance)
        drawRect(fig, instance, True) # ATTENZIONE! CON BLOCK NON ESEGUE DOPO DO QUESTA RIGA


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


        #instances = instances[40:41]

        global fig
        fig = plt.figure()
        fig.canvas.manager.toolmanager.add_tool('Neigh 1', mycallback)
        fig.canvas.manager.toolmanager.add_tool('Neigh 2', mycallback)
        fig.canvas.manager.toolbar.add_tool('Neigh 1', 'neigh')
        fig.canvas.manager.toolbar.add_tool('Neigh 2', 'neigh')
        fig.canvas.manager.toolmanager.add_tool('Next instance', nextInstance, instances=instances)
        fig.canvas.manager.toolbar.add_tool('Next instance', 'instance')
        plt.show()

        #for instance in instances:
        #    print(instance)
        #    greedyShelf(instance)
        #    drawRect(fig, instance)

        """
        instances = instances[13:14]

        for instance in instances:
            print(instance)
            greedyShelf(instance)
            drawRect(instance,False)
            intraNeighborhood(instance)
            drawRect(instance,True)
        """ 
    else:
        print("Manca argomento")

if __name__ == '__main__':
        main()