class Student:
    #Method

    def __init__(self, name:str , age:int , gender:str ) -> None: 
        #Attributes

        self.name = name
        self.age = age
        self.gender = gender

    def display(self) -> None:
        print(f"Name:{self.name}, Age:{self.age}, Gender:{self.gender}")
    
    def get_age(self) -> int:
        return self.age


s1 = Student("Valeria", 32, "Female")
age = s1.get_age()
print(age)

    