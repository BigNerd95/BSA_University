import re
import sys
from Item import Item

class Instance():

    def __init__(self, pclass, rinst, ainst, container_h, container_w):
        self.pclass = pclass
        self.rinst = rinst
        self.ainst = ainst
        if(container_h < container_w):
            container_h, container_w = container_w, container_h
        self.container_h = container_h
        self.container_w = container_w
        self.container_area = self.container_h * self.container_w
        
        self.containers = []
        self.items = []
        self.shelves=[]
        self.itemID = -1
        self.greedyDone = False

    def addItem(self, item_h, item_w):
        self.itemID += 1
        self.items.append(Item(item_w, item_h, id=self.itemID))

    def reset(self):
        self.containers = []
        self.greedyDone = False

    def wastedArea(self):
        freeArea = 0
        containerArea = self.container_area * len(self.containers)
        print("Containers:", len(self.containers))
        
        for c in self.containers:
            #print(c.wastemap.free_area)
            for s in c.shelves:
                for r in s.wastemap.freerects:
                    freeArea+=r.area

        return freeArea/containerArea*100

    def binLowerBound(self):
        tot_area = 0
        for i in self.items:
            tot_area += i.area

        return tot_area/self.container_area

    def __str__(self):
        s  = "Instance Class: " + self.pclass + ", Relative N: " + self.rinst + ", Absolute N: " + self.ainst + "\n"
        s += "Item number: " + str(len(self.items)) + "\n"
        s += "Container sizes: H: " + str(self.container_h) + ", W: " + str(self.container_w) + "\n"
        return s


def parse_instance(p):
    lines = p.split("\n")
    if len(lines) > 4:
        pclass = re.findall(".* ([0-9]+) .*", lines.pop(0))[0] # PROBLEM CLASS
        nitems = re.findall(".* ([0-9]+) .*", lines.pop(0))[0] # N. OF ITEMS
        rinst, ainst = re.findall(".* ([0-9]+) .* ([0-9]+) .*", lines.pop(0))[0] # RELATIVE AND ABSOLUTE N. OF INSTANCE
        cont_h, cont_w = re.findall(".* ([0-9]+) .* ([0-9]+) .*", lines.pop(0))[0] # HBIN,WBIN

        new_instance = Instance(pclass, rinst, ainst, int(cont_h), int(cont_w))

        for l in lines:
            ih, iw = re.findall(".* ([0-9]+) .* ([0-9]+).*", l)[0]
            new_instance.addItem(int(ih), int(iw))

        if len(new_instance.items) != int(nitems):
            raise Exception("[Parser] Il numero di item non corrisponde! Letti: "+str(len(new_instance.items))+ ", Attesi: " + nitems)

        return new_instance
    else:
        return None

def parse(filepath):
    instances = []

    with open(filepath, "rt") as f:
        data = f.read()
    
    problems = data.split("\n\n")

    for p in problems:
        
        #try:
        new_instance = parse_instance(p)
        if new_instance:
            instances.append(new_instance)
        #except Exception as e:
        #    print(e)
            

    return instances

def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        instances = parse(filepath)
        for i in instances:
            print(i)

if __name__ == "__main__":
    main()