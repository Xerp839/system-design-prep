class Student:
    #Attribute
    name = ""
    age = 0
    gender = ""


    #Method

    def set_info(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def display(self):
        print(f"Name:{self.name}, Age:{self.age}, Gender:{self.gender}")
    


s1 = Student()
s1.set_info("Valeria", 32, "Female")
s1.display()

    