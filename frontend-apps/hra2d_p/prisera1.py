def pozicia():
    return 1, 1

def uprav(self):
    self.x += 0.05
    if self.x >= self.bludisko.sirka-1:
        self.x = 0

