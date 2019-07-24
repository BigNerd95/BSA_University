import re
import sys

class Item:
    def __init__(self, width, height, x = 0, y = 0, rotation = True):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.area = self.width * self.height
        self.rotated = False
        self.id = 0


    def __repr__(self):
        return 'Item(width=%r, height=%r, x=%r, y=%r)' % (self.width, self.height, self.x, self.y)


    def rotate(self):
        self.width, self.height = self.height, self.width
        self.rotated = False if self.rotated == True else True

class Container(Item):
    pass

class Instance():
    def __init__(self, pclass, rinst, ainst, container_h, container_w):
        self.pclass = pclass
        self.rinst = rinst
        self.ainst = ainst
        self.container_h = container_h
        self.container_w = container_w
        self.containers = []
        self.items = []

    def addItem(self, item_h, item_w):
        self.items.append(Item(item_w, item_h))

    def __str__(self):
        s  = "Instance Class: " + self.pclass + ", Relative N: " + self.rinst + ", Absolute N: " + self.ainst + "\n"
        s += "Item number: " + str(len(self.items)) + "\n"
        s += "Container sizes: H: " + str(self.container_h) + ", W: " + str(self.container_w) + "\n"
        return s


def parse_instance(p):
    lines = p.split("\n")
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


def parse(filepath):
    instances = []

    with open(filepath, "rt") as f:
        data = f.read()
    
    problems = data.split("\n\n")

    for p in problems:
        
        try:
            new_instance = parse_instance(p)
            instances.append(new_instance)
        except Exception:
            pass

    return instances

def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        instances = parse(filepath)
        for i in instances:
            print(i)

if __name__ == "__main__":
    main()