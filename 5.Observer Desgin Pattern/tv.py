from observer import Observer


class Tvdisplay(Observer):
    def update(self, temp):
        print(f"TV Temp updated to {temp}")

