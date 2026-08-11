class Animal:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def eat(self) -> None:
        print("i am eating")
    
    def sleep(self) -> None :
        print("I am sleeping")

    
class Dog(Animal):
    def __init__(self, name: str, age: int, breed: str) -> None:
        super().__init__(name, age)
        self.breed = breed
    
    def bark(self) -> None:
        print("Woof Woof")

    def display(self) -> None:
        print(f"My name is {self.name}, age is {self.age}")
    
    def sleep(self) -> None:
        print("Sleeping like a dawg")


dog = Dog("Doggie", 14, "german shepard")
dog.sleep()