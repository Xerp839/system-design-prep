from observer import Observer


class Mobile_display(Observer):
    def update(self, temp):
        print(f"Mobile Temp updated to {temp}")

