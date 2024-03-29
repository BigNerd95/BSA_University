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
from TabooList import Move

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

    for s in container.shelves:
        for r in s.wastemap.freerects:
            patches3.append(Rectangle((r.x,r.y),r.width,r.height))

    pc1 = PatchCollection(patches1, facecolor='None', alpha=1, edgecolor='blue', linewidths=3, zorder=3)
    pc2 = PatchCollection(patches2, facecolor='red', alpha=1, edgecolor='black', zorder=1)
    pc3 = PatchCollection(patches3, facecolor='green', alpha=1, edgecolor='black', zorder=2)    

    x.add_collection(pc1)
    x.add_collection(pc2)
    x.add_collection(pc3)

def drawRect(fig, instance, block):
    print("disegno")
    fig.clear()


    #print(len(instance.items))

    containers=instance.containers


    #attenzione                 ceil
    righe   = math.floor(math.sqrt(len(containers)))
    colonne = math.ceil(math.sqrt(len(containers)))
    if righe*colonne < len(containers):
        righe += 1
    ax = fig.subplots(righe, colonne)
    
    if righe == 1 and colonne == 1:
        draw_bin(containers[0], ax)
        ax.axis('equal')
        ax.axis("off")
    elif righe == 1 and colonne > 1:
        i=0
        for x in ax:
            if(i < len(containers)):
                draw_bin(containers[i], x)
                i+=1
            x.axis('equal')
            x.axis("off")
    else:
        i=0
        for y in ax:
            for x in y:
                if(i < len(containers)):
                    draw_bin(containers[i], x)
                    i+=1
                x.axis('equal')
                x.axis("off")

    fig.suptitle("Instance: "+ instance.ainst +"    Used Bins: "+str(len(containers))+"    Lower bound: "+str(math.ceil(instance.binLowerBound()))+"    Global wasted area: "+ str(math.floor(instance.wastedArea()))+"%")
    

    fig.canvas.draw()
    
    #plt.show(block=block)
    #plt.pause(0.5)
    #plt.close()

def shiftAll(rect, shelf):
    for r in shelf.items:
        rc=rectOnLeft(r, shelf)
        if(r.x > rect.x and r.y == rect.y and (rc == None or rc == rect)):
            #if(r.y + r.height < shelf.vertical_offset+shelf.height):                
            #    freeRect=getTopFreeRect(r, shelf)
            #    if(freeRect):
                    #print("getTopFreeRect")
            #        freeRect.x-=rect.width
            r.x-=rect.width

    """
    #lo scaffale non è pieno quindi c'è un rettangolo libero da estendere
    if(shelf.available_width > 0):
        #last_rect = shelf.items[len(shelf.items)-1]
        #shelf.width - last_rect.x + last_rect.width
        freeRect=getShelfFreeRect(shelf)

        shelf.available_width += rect.width

        freeRect.x=shelf.width-shelf.available_width
        freeRect.width+=rect.width

    else:#lo scaffale era pieno, quindi non c'è il rettangolo libero allora lo creo
        freeRect = FreeRectangle(rect.width, shelf.height, shelf.width-rect.width, shelf.vertical_offset)
        shelf.wastemap.freerects.add(freeRect)
        shelf.available_width+=rect.width
    """

#shelf1 contiene i rettangoli da shiftare (scaffale sopra), shelf2 scaffale sotto da riempire
def moveRect(rect, freeRect, shelf1, shelf2):
    
    #print(rect.id)
    shiftAll(rect, shelf1)

    #aumento e riduco lo spazio disponibile negli scaffali

    if(rect.y == shelf1.vertical_offset):# and shift):
        shelf1.available_width += rect.width
    
    if(freeRect.y == shelf2.vertical_offset):
        shelf2.available_width -= rect.width

    #sposto il rettangolo
    rect.x=freeRect.x
    rect.y=freeRect.y

    #aggiungo e rimuovo il rettangolo dagli scaffali
    shelf2.items.append(rect)
    shelf1.items.remove(rect)   

    #shelf1.area = shelf1.available_width * shelf1.height
    #shelf2.area = shelf2.available_width * shelf2.height

    #ricalcolo i rettangoli liberi per gli scaffali
    shelf1.wastemap.freerects.clear()
    shelf2.wastemap.freerects.clear()

    _add_to_wastemap(shelf1)
    _add_to_wastemap(shelf2)


def buildTower(rect, shelf):
    tower = [list(),0]
    
    tower[0].append(rect)
    tower[1]+=rect.height

    overRect = getRectOverRect(rect, shelf)

    while(overRect):
        tower[0].append(overRect)
        tower[1]+=overRect.height
        overRect = getRectOverRect(overRect, shelf)

    return tower

def inTowers(rect, towers):
    for tower in towers:
        for r in tower[0]:
            if rect == r:
                return True

    return False 
def realignAll(shelf):

    towers=[]
    
    for r in shelf.items:
        if(not inTowers(r, towers)):
            tower = buildTower(r, shelf)
            towers.append(tower)

    towers.sort(key=lambda x:x[1], reverse=True)

    x = 0
    for tower in towers:
        #print("Tower")
        #[print(r.id) for r in tower[0]]

        for rect in tower[0]:
            rect.x = x

        x += tower[0][0].width

    shelf.available_width = shelf.width - x

def moveRectInter(rect, freeRect, shelf1, shelf2):
    
    #print(len(shelf2.wastemap.freerects))
    #print("rect x "+str(rect.x)+" freeRect x "+str(freeRect.x)+"rect y "+str(rect.y)+" freeRect y "+str(freeRect.y))
    
    pushed = pushDownRect(rect, shelf1)
    #print(rect.id)
    
    if(freeRect.y==shelf2.vertical_offset):
        shelf2.available_width-=rect.width
    #cambio coordinate rettangolo
    rect.x=freeRect.x
    rect.y=freeRect.y

    #aggiungo e rimuovo il rettangolo dagli scaffali
    shelf2.items.append(rect)
    shelf1.items.remove(rect)

    realignAll(shelf1)
    #realignAll(shelf2)

    #print("rect x "+str(rect.x)+" freeRect x "+str(freeRect.x)+"rect y "+str(rect.y)+" freeRect y "+str(freeRect.y))  

    #ricalcolo i rettangoli liberi per gli scaffali
    shelf1.wastemap.freerects.clear()
    shelf2.wastemap.freerects.clear()

    _add_to_wastemap(shelf1)
    _add_to_wastemap(shelf2)


def getRectOverRect(rect, shelf):
    for r in shelf.items:
        if(rect.x==r.x and rect.y+rect.height==r.y):
            return r
    return None

def rectOverRect(rect, shelf):
    for r in shelf.items:
        if(rect.x==r.x and rect.y+rect.height==r.y):
            return True
    return False

def rectOnRight(rect,shelf):
    for r in shelf.items:
        if(rect.y==r.y and rect.x+rect.width==r.x):
            return True
    return False

def rectOnLeft(rect,shelf):
    for r in shelf.items:
        if(rect.y==r.y and r.x+r.width==rect.x):
            return r
    return None

def rectUnderRect(rect, shelf):
    under = []
    for r in shelf.items:
        if (r.x <= rect.x and r.y < rect.y):
            under.append(r)
    if(len(under) > 0):
        under.sort(key=lambda x: (x.x, x.y), reverse=True)
        return under[0]
    else:
        return None

def getTopFreeRect(rect, shelf):
    for r in shelf.wastemap.freerects:
        if(rect.x==r.x and rect.y+rect.height==r.y):
            return r

def getShelfFreeRect(shelf):
    for r in shelf.wastemap.freerects:
        if(r.x == shelf.width - shelf.available_width and r.y==shelf.vertical_offset):
            return r

"""
Primo intorno:
- cicla tutti i container 
- prende gli scaffali a coppie
- controlla se nello scaffale sotto c'e' un rettanoglo libero
- se c'e' prende il rettangolo piu largo dello scaffale sopra e lo sposta
"""
def intraNeighborhood(instance):
    #best_height = 0
    best_width = 0
    best = None

    change=False

    for container in instance.containers:             
        for i in range(0, len(container.shelves)-2): 
            
            freeRect=getShelfFreeRect(container.shelves[i])

            if(freeRect):
                for r in container.shelves[i+1].items:
                    if(r.width <= freeRect.width and r.width > best_width):
                        best=r
                        best_width=r.width

                if(best!=None):
                    moveRect(best, freeRect, container.shelves[i+1], container.shelves[i])                    
                    best=None
                    best_width=0
                    change=True
            #else:
                #print("Non c'è il free rect")
            container.shelves[i].wastemap.rectangle_merge()
            #container.shelves[i].wastemap.rectangle_merge()
            if(len(container.shelves[i+1].items)==0):
                compactShelves(container, instance)
            else:
                container.shelves[i+1].wastemap.rectangle_merge()
            #container.shelves[i+1].wastemap.rectangle_merge()

    return change


def getContainerShelf(containers, shelf):
    for container in containers:
        if(shelf in container.shelves):
            return container

#quello che sta in items2 viene tolto da items1
def removeItems(items1, items2):
    for item in items2:
        if(item in items1):
            items1.remove(item)

def updateShelfRectangles(container, shelf):
    #aggiornare solo ordinate
    old_offset = shelf.vertical_offset
    shelf.vertical_offset = container.height-container.available_height#+shelf.vertical_offset

    for r in shelf.items:
        r.y = r.y - old_offset + shelf.vertical_offset

    for r in shelf.wastemap.freerects:
        r.y = r.y - old_offset + shelf.vertical_offset

#riordina gli scaffali per altezza e mette in cima uno scaffale vuoto se serve
def compactShelves(container, instance):
    #y=0

    emptyShelves = []
    container.available_height = container.height
    container.shelves.sort(key=lambda x: (x.height), reverse=True)

    for shelf in container.shelves:
        if(len(shelf.items) > 0):
            updateShelfRectangles(container, shelf)
            #shelf.vertical_offset=container.height - container.available_height#y
            
            #y+=shelf.height
            container.available_height-=shelf.height
        else:
            emptyShelves.append(shelf)

    removeItems(container.shelves, emptyShelves)

    FreeShelf = Shelf(container.width, container.available_height, container.height-container.available_height)
    freeRect = FreeRectangle(container.width, FreeShelf.height, container.x, FreeShelf.vertical_offset)
    FreeShelf.wastemap.freerects.add(freeRect)
    container.shelves.append(FreeShelf)
    instance.shelves.append(FreeShelf)
    #GESTIRE SCAFFALI VUOTI UNIRLI
    #for shelf in emptyShelves:
        #shelf.vertical_offset=y
        #updateShelfRectangles(container, shelf)
        #y+=shelf.height

#ridimensiono lo scaffale vuoto in cima al container
"""
def redimLastShelf(container, instance, height):
    emptyShelf = container.shelves[len(container.shelves)-1]

    if(height == container.available_height):
        container.shelves.remove(emptyShelf)
        instance.shelves.remove(emptyShelf)
    else:
        emptyRect=emptyShelf.wastemap.freerects[0]
        new_y = container.height-container.available_height+height
        
        container.available_height-=height
        
        emptyRect.height=container.available_height
        emptyRect.y=new_y
        
        emptyShelf.vertical_offset=new_y
        emptyShelf.height=container.available_height
"""

def moveShelf(container1, container2, shelf, instance):
    #rimuovo i rettangoli da container1 e li metto in container2
    removeItems(container1.items, shelf.items)
    container2.items+=shelf.items

    #aggiorno le coordinate dei rettangoli dello scaffale
    updateShelfRectangles(container2, shelf)

    #ridimensiono l'ultimo scaffale del container2 dovrebbe contenere sempre il rettangolo vuoto
    #dovrebbe essere più efficiente, invece che ricompattare gli scaffali
    #redimLastShelf(container2, instance, shelf.height)#container2.shelves.remove(container2.shelves[len(container2.shelves)-1])    

    #sposto lo scaffale da container1 a container2
    container1.shelves.remove(shelf)
    container2.shelves.append(shelf)

    #creo uno scaffale con un rettangolo vuoto dentro per sostituire lo scaffale spostato
    if(len(container1.items)>0):
        #FreeShelf = Shelf(container1.width, shelf.height, shelf.vertical_offset)
        #freeRect = FreeRectangle(container1.width, shelf.height, container1.x, shelf.vertical_offset)
        #FreeShelf.wastemap.freerects.add(freeRect)
        compactShelves(container1,instance)
        #container1.shelves.append(FreeShelf)
        #instance.shelves.append(FreeShelf)
    else:
        #c'è solo uno scaffale quindi elimino il container
        instance.shelves.remove(container1.shelves[0])
        instance.containers.remove(container1)

    compactShelves(container2,instance)

def searchBestShelf(container, shelves):
    best_height = 0
    best_shelf = None

    for shelf in shelves:
        if (container.available_height > shelf.height and shelf.height > best_height
            and shelf not in container.shelves and len(shelf.items) > 0):
            
            best_shelf = shelf
            best_height = shelf.height

    return best_shelf

"""
Secondo intorno:
- ordina i container per spazio disponibile in altezza (crescente)
- ordina gli scaffali di tutti i container per altezza (crescente)
- considera solo i container che sono piu' pieni di meta' (l'altezza disponibile e' minore della meta' della sua altezza)
- prende il container con minor spazio disponibile e cerca lo scaffale piu' alto che ci stia dentro (cosi da riempirlo il piu possibile)
- la tabulist permette di non ripetere le mosse che ha appena fatto
"""
def interShelfborhood(instance):
    
    if(len(instance.containers) > 1):
        #ordino i container per spazio libero, cerco di riempire prima i più stretti
        #instance.containers.sort(key=lambda x: (x.available_height))
        containers = sorted(instance.containers,key=lambda x: (x.available_height))

        #instance.shelves.sort(key=lambda x: (x.height))
        shelves=sorted(instance.shelves,key=lambda x: (x.height))
        #ciclo finchè non trovo uno container che possa contenere uno scaffale di un altro container
        for i in range(0, len(containers)):
            #print("spostiamo uno scaffale")
            #print("Containers len", len(containers))
            #print("i ", i)
            if(containers[i].available_height < containers[i].height/2):
                best_shelf=searchBestShelf(containers[i], shelves)    
                
                #print("J",j)
                if(best_shelf):
                    #provare a cercare nei container successivi al mio (Taboo List)

                    move = Move(moveShelf, [best_shelf,getContainerShelf(containers, best_shelf),containers[i]])
                                        
                    if not instance.tabooList.contains(move):
                        moveShelf(getContainerShelf(containers, best_shelf), containers[i], best_shelf, instance)
                        instance.tabooList.insert(move)
                        return True
                    else:
                        instance.tabooList.reduce()
                    

    return False


def getShelf(item, container):

    for shelf in container.shelves:
        if(item in shelf.items):
            return shelf

def insertInContainer(container, shelf, item): 
    container.items.append(item)
    #shelf.items.append(item)


def removeFromContainer(instance, container, item, shelf):
    container.items.remove(item)
    #shelf=getShelf(item, container)

    #shelf.items.remove(item)
    
    if(len(container.items) == 0):
        instance.containers.remove(container)
        instance.shelves.remove(shelf)
    else:
        if(len(shelf.items)==0):
            container.shelves.remove(shelf)
            instance.shelves.remove(shelf)
            compactShelves(container, instance)
        """else:
            shiftAll(item, shelf)
            shelf.wastemap.freerects.clear()
            shelf.available_width += item.width
            _add_to_wastemap(shelf)
            print("asdasd")"""

def pushDownRect(item,shelf):
    stack = []
    rect = getRectOverRect(item,shelf)

    if(rect and item.width > rect.width):
        shelf.available_width=shelf.available_width+item.width-rect.width

    if(rect):
        while (rect):
            stack.append(rect)
            rect = getRectOverRect(rect,shelf)

        for r in stack:
            r.y-=item.height
        
        return True
    return False
    """rect = getRectOverRect(item,shelf)
    if(rect): 
        pushDownRect(rect,shelf)
        print("rect sopra "+str(rect.id)+" rect sotto "+str(item.id))
        print("altezza sopra "+str(rect.height)+" altezza sotto "+str(item.height))
        print("y sopra "+str(rect.y)+" y sotto "+str(item.y))
        rect.y -= item.height

        return True
    return False"""

"""
Terzo intorno:
- ordina i container in base al rapporto area_occupata/numero_item (cosi da trovare i bin con tanti oggetti piccoli)
- ordina gli oggetti per area (crescente)
- prende il piu' piccolo e prova a spostarlo nel miglior rettangolo libero di un altro container
- la tabulist permette di non ripetere le mosse che ha appena fatto
"""
def interRectangle(instance):
    #riordinare i bin per numero di pezzi (lower bound)
    #containers = sorted(instance.containers,key=lambda x: (sum(map(lambda y: y.area,instance.containers.items))/len(instance.containers.items)))
    containers = sorted(instance.containers,key=lambda x: x.areaPiecesRatio())


    #cercare di spostare i rettangoli più grandi
    for i,container1 in enumerate(containers):
        items = sorted(container1.items, key=lambda x: x.area)
        for item in items:
            res = tryToMove(item, container1, containers[i+1:], instance)
            if res == True:
                return True

    return False

def tryToMove(item, container1, containers, instance):
    for container2 in containers:
        for shelf2 in container2.shelves:
            if(shelf2._item_fits_shelf(item)):
                #shelf.wastemap.insert(item)
                _, freeRect, rot = shelf2.wastemap._find_best_score(item)
                if(freeRect and (freeRect.y == shelf2.vertical_offset or (freeRect.y > shelf2.vertical_offset and freeRect.x == rectUnderRect(freeRect, shelf2).x))):
                    shelf1=getShelf(item, container1)
                    
                    move = Move(moveRect, [item, container1, container2])
                    
                    #print(instance.tabooList.contains(move))

                    if not instance.tabooList.contains(move):                                
                        #avvenuto = pushDownRect(item, shelf1)
                        moveRectInter(item, freeRect, shelf1, shelf2)#, True)#not avvenuto)                     
                        insertInContainer(container2, shelf2, item)
                        removeFromContainer(instance, container1, item, shelf1)
                    
                        instance.tabooList.insert(move)
                                                
                        return True
                    else:
                        instance.tabooList.reduce()
                        return None
                        

def rotateWide(rectangles):
    for r in rectangles:
        if(r.width > r.height):
            r.rotate()
    return rectangles

def bsa(instance):
    instance.reset()
    greedyShelf(instance)

    n1=True
    n2=True
    n3=True

    cont = 1000
    while( (n1 or n2 or n3) and cont > 0):
        n1=intraNeighborhood(instance)
        if(not n1):
            n2=interShelfborhood(instance)
            if(not n2):
                n3=interRectangle(instance)
        cont -= 1

"""
Soluzione iniziale:
- ruota tutti i rettangoli in verticale
- ordina i rettangoli per altezza e larghezza
- li inserisce in uno scaffale alto come il primo rettangolo da inserire
- quando non ci stanno piu in larghezza, verifica se ci sta un altro scaffale nel container
- se non ci sta crea un altro container
- ogni volta che riempe uno scaffale, vengono calcolati i rettangoli liberi
"""
def greedyShelf(instance):
    if not instance.greedyDone:
        print("Eseguo greedy")
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
                
                while(not hlimit):                      
                    
                    sh=Shelf(cont.width, shelf_height, cont.height-cont.available_height)
                    cont.shelves.append(sh)
                    instance.shelves.append(sh)
                    cont.available_height-=shelf_height
                    
                    #finchè ci stanno inserisce rettangoli nello scaffale           
                    while(i < len(rectangles) and sh._item_fits_shelf(rectangles[i])):
                        sh.insert(rectangles[i])
                        cont.items.append(rectangles[i])
                        i+=1
                    
                    #aggiunge lo spazio libero dello scaffale alla wastemap
                    _add_to_wastemap(sh)

                    #controlla se sono finiti i rettangoli oppure se lo scaffale nuovo supererebbe l'altezza massima
                    if i >= len(rectangles):
                        hlimit=True
                    else:
                        
                        shelf_height = rectangles[i].height
                        
                        if cont.available_height < shelf_height:
                            hlimit=True
                            #print(y)
                    
                    if cont.available_height < shelf_height or i >= len(rectangles):
                        #aggiunge uno scaffale vuoto in alto alla wastemap
                        freeRect = FreeRectangle(cont.width, cont.available_height, cont.x, cont.height-cont.available_height)
                        sh=Shelf(cont.width, cont.available_height, cont.height-cont.available_height)
                        cont.shelves.append(sh)
                        instance.shelves.append(sh)
                        sh.wastemap.freerects.add(freeRect)
                        #print(i)
                        
            instance.greedyDone = True
        else:
            raise Exception("Rettangolo più alto non sta nel bin")
        #return rect_inserted,wastemap,shelves

def genHorizontalFreeRect(rect, shelf):
    if(rect.y != shelf.vertical_offset and not rectOnRight(rect,shelf)):
        #print(rect.id)
        underRect = rectUnderRect(rect, shelf)
        #print(underRect.id)
        if(underRect):
            freeWidth = (underRect.x+underRect.width) - (rect.width+rect.x)
            freeHeight = (shelf.vertical_offset + shelf.height) - (rect.y)
            freeX = rect.x + rect.width
            freeY = rect.y
            freeRect = FreeRectangle(freeWidth, freeHeight, freeX, freeY)
            shelf.wastemap.freerects.add(freeRect)

def _add_to_wastemap(shelf):
        """ Add lost space above items to the wastemap """
        # Add space above items to wastemap
        for item in shelf.items:
            if item.y+item.height < shelf.height+shelf.vertical_offset and not rectOverRect(item, shelf):
                freeWidth = item.width
                freeHeight = (shelf.vertical_offset + shelf.height) - (item.height + item.y)
                freeX = item.x
                freeY = item.y + item.height
                freeRect = FreeRectangle(freeWidth, freeHeight, freeX, freeY)
                shelf.wastemap.freerects.add(freeRect)
            genHorizontalFreeRect(item,shelf)

        # Move remaining shelf width to wastemap
        if shelf.available_width > 0:
            freeWidth = shelf.available_width
            freeHeight = shelf.height
            freeX = shelf.width - shelf.available_width
            freeY = shelf.vertical_offset
            freeRect = FreeRectangle(freeWidth, freeHeight, freeX, freeY)
            shelf.wastemap.freerects.add(freeRect)
        # Close Shelf
        #shelf.available_width = 0
        # Merge rectangles in wastemap
        shelf.wastemap.rectangle_merge()

def genGUI():
    fig = plt.figure()
    #fig.canvas.manager.toolbar._Button("PREVIOUS", "back_large", <ACTION_PREV>)
    #fig.canvas.manager.toolbar._Button("NEXT", "forward_large", <ACTION_NEXT>)
    fig.show()

class searchInstanceBtn(ToolBase):
    def trigger(self, *args, **kwargs):
        search()

class resetInstanceBtn(ToolBase):
    def trigger(self, *args, **kwargs):
        reset()

class nextInstanceBtn(ToolBase):
    def trigger(self, *args, **kwargs):
        nextI()

class prevInstanceBtn(ToolBase):
    def trigger(self, *args, **kwargs):
        prevI()

class Neigh_1Btn(ToolBase):
    def trigger(self, *args, **kwargs):
        neigh_1()

class Neigh_2Btn(ToolBase):
    def trigger(self, *args, **kwargs):
        neigh_2()

class Neigh_3Btn(ToolBase):
    def trigger(self, *args, **kwargs):
        neigh_3()

def search():
    global fig
    global instances
    global instance_index
    instance = instances[instance_index]
    print(instance)

    bsa(instance)
    print("BSA terminata")
    drawRect(fig, instance, True) # ATTENZIONE! CON BLOCK NON ESEGUE DOPO DO QUESTA RIGA

def reset():
    global fig
    global instances
    global instance_index
    instance = instances[instance_index]
    print(instance)

    instance.reset()
    greedyShelf(instance)
    drawRect(fig, instance, True) # ATTENZIONE! CON BLOCK NON ESEGUE DOPO DO QUESTA RIGA


def nextI():
    global fig
    global instances
    global instance_index

    if instance_index < len(instances) - 1:
        instance_index += 1
        instance = instances[instance_index]
    

        print(instance)
        if not instance.greedyDone:
            greedyShelf(instance)
        drawRect(fig, instance, True) # ATTENZIONE! CON BLOCK NON ESEGUE DOPO DO QUESTA RIGA
    else:
        print("Instanze finite")

def prevI():
    global fig
    global instances
    global instance_index

    if instance_index > 0:
        instance_index -= 1
        instance = instances[instance_index]

        print(instance)
        if not instance.greedyDone:
            greedyShelf(instance)
        drawRect(fig, instance, True) # ATTENZIONE! CON BLOCK NON ESEGUE DOPO DO QUESTA RIGA
    else:
        print("Instanze finite")

def neigh_1():
    global fig
    global instances
    global instance_index
    instance = instances[instance_index]
    print(instance)

    intraNeighborhood(instance)
    drawRect(fig, instance, True) # ATTENZIONE! CON BLOCK NON ESEGUE DOPO QUESTA RIGA

def neigh_2():
    global fig
    global instances
    global instance_index
    instance = instances[instance_index]
    print(instance)

    interShelfborhood(instance)
    #intraNeighborhood(instance)
    drawRect(fig, instance, True) # ATTENZIONE! CON BLOCK NON ESEGUE DOPO DO QUESTA RIGA


def neigh_3():
    global fig
    global instances
    global instance_index
    instance = instances[instance_index]
    print(instance)

    interRectangle(instance)
    #interShelfborhood(instance)
    #intraNeighborhood(instance)
    drawRect(fig, instance, True) # ATTENZIONE! CON BLOCK NON ESEGUE DOPO DO QUESTA RIGA


def press(event, *args, **kwargs):
    print('press', event.key)
    sys.stdout.flush()

    if event.key == "right":
        nextI()
    elif event.key == "left":
        prevI()
    elif event.key == 'r':
        reset()
    elif event.key == 'b':
        search()
    elif event.key == '1':
        neigh_1()
    elif event.key == '2':
        neigh_2()
    elif event.key == '3':
        neigh_3()

def main():
    
    
    #rectangles = []

    #for i in range(100):
    #   w = random.randint(10, 50)
    #   h = random.randint(50, 100)
    #   rectangles.append(Item(h,w))

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        global  instances
        instances = Parser.parse(filepath)

        global instance_index
        instance_index = 0

        global fig
        fig = plt.figure()
        fig.canvas.manager.toolmanager.add_tool('Neigh 1', Neigh_1Btn)
        fig.canvas.manager.toolbar.add_tool('Neigh 1', 'neigh')
        fig.canvas.manager.toolmanager.add_tool('Neigh 2', Neigh_2Btn)
        fig.canvas.manager.toolbar.add_tool('Neigh 2', 'neigh')
        fig.canvas.manager.toolmanager.add_tool('Neigh 3', Neigh_3Btn)
        fig.canvas.manager.toolbar.add_tool('Neigh 3', 'neigh')

        fig.canvas.manager.toolmanager.add_tool('Prev <--', prevInstanceBtn)
        fig.canvas.manager.toolbar.add_tool('Prev <--', 'instance')
        fig.canvas.manager.toolmanager.add_tool('--> Next', nextInstanceBtn)
        fig.canvas.manager.toolbar.add_tool('--> Next', 'instance')

        fig.canvas.manager.toolmanager.add_tool('Search', searchInstanceBtn)
        fig.canvas.manager.toolbar.add_tool('Search', 'instance2')
        fig.canvas.manager.toolmanager.add_tool('Reset', resetInstanceBtn)
        fig.canvas.manager.toolbar.add_tool('Reset', 'instance2')
         
        fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
        plt.rcParams["keymap.all_axes"] = []
        plt.rcParams["keymap.back"] = []
        plt.rcParams["keymap.forward"] = []
        plt.rcParams["keymap.fullscreen"] = []
        plt.rcParams["keymap.grid"] = []
        plt.rcParams["keymap.grid_minor"] = []
        plt.rcParams["keymap.home"] = []
        plt.rcParams["keymap.pan"] = []
        plt.rcParams["keymap.quit"] = []
        plt.rcParams["keymap.quit_all"] = []
        plt.rcParams["keymap.save"] = []
        plt.rcParams["keymap.xscale"] = []
        plt.rcParams["keymap.yscale"] = []
        plt.rcParams["keymap.zoom"] = []
        

        fig.canvas.mpl_connect('key_press_event', press)
        print(plt.rcParams)


        instance = instances[instance_index]
        print(instance)
        greedyShelf(instance)
        drawRect(fig, instance, True)

        
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