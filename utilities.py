class Contador:

    def __init__(self, initValue):
        self.value = initValue

    def nextValue(self):
        self.value += 1
        return self.value

    def previewValue(self):
        self.value -= 1
        return self.value

    def reset(self, resetValue):
        self.value = resetValue