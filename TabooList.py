class Move:
    def __init__(self, operation, parameters):
        self.operation=operation
        self.parameters=parameters

    def compare(self, move):
        if(self.operation == move.operation and self.parameters == move.parameters):
            return True
        else:
            return False

class TabooList:
    def __init__(self):
        self.moves=dict()

    def insert(self, move):
        if move not in self.moves:
            self.moves[move]=3

        for move, count in self.moves.items():
            count-=1
            if(count==0):
                self.moves.remove(move)

    def contains(self, move):
        for m in self.moves:
            if(move.compare(m)):
                return True

        return False