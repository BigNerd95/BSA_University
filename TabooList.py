class Move:
    def __init__(self, operation, parameters):
        self.operation=operation
        self.parameters=parameters

    def compare(self, move):
        parameters2 = move.parameters

        parameters2[1], parameters2[2] = parameters2[2], parameters2[1] 

        if(self.operation == move.operation and Move.compareParameters(self.parameters,move.parameters) and Move.compareParameters(self.parameters,parameters2)):
            return True
        else:
            return False

    def compareParameters(parameters1, parameters2):
        for p1, p2 in zip(parameters1, parameters2):
            if(not p1.compare(p2)):
                return False

        return True

    def __str__(self):
        a = str(self.operation) + "    "
        for p1 in self.parameters:
            a += str(p1) + "    "
        a += "\n\n"
        return a

class TabooList:
    def __init__(self):
        self.moves=dict()

    def insert(self, move):
        if move not in self.moves:
            self.moves[move]=15
        self.reduce()

    def reduce(self):
        deleted=None
        
        for move, count in self.moves.items():
            self.moves[move]-=1
            if(self.moves[move]==0):
                deleted=move

        if(deleted):
            self.moves.pop(deleted)

    def contains(self, move):
        #print("TABOOLIST LENGHT:",len(self.moves))
        #print(move)
        #print("---")
        for m in self.moves:
            #print(m)
            if(move.compare(m)):
                return True

        return False