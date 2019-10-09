def pozicia():
    return 3, 1

def uprav(self):
    self.y += 0.02
    if self.y >= self.bludisko.vyska-1:
        self.y = 0

