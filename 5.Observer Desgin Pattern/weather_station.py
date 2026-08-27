from observer import Observer

class WeatherStation():
    def __init__(self) -> None:
        self.__temperature = 0
        self.__observers: Observer = []

    def add_obeserver(self, observer:Observer):
        self.__observers.append(observer)

    def remove_observers(self, obs: Observer):
        self.__observers.remove(obs)

    def update_temp(self, temp):
        self.__temperature = temp
        self.notify()
        # notfiy 
    
    def notify(self):
        for i in self.__observers:
            i.update(self.__temperature)
