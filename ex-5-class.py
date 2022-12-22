class WaterState:
    def __init__(self):
        self.apt = None
        self.cold = None
        self.hot = None

w = WaterState()
w.apt = 1
w.cold = 2
print(vars(w))
print(w.hot)
