from abc import ABC, abstractmethod
from operator import length_hint

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    @abstractmethod
    def parameter(self):
        pass


class Rectangle(Shape):

    def __init__(self, lenght, breadth):
        self.length = lenght
        self.breadth = breadth

    def area(self):
        print(self.length * self.breadth)
    
    def parameter(self):
        pass

r1 = Rectangle(10, 20)
r1.area()