class Bank:
    def __init__(self, name:str, balance:int):
        self.name = name
        self.__balance = balance

    def get_balance(self) -> None:
        print(f"Balance : {self.__balance}")

    def deposti(self, amount:int):
        self.__balance += amount
        print(f"Amout Deposit done, current balance: {self.__balance}")

    def withdraw(self, amount:int) -> None:
        if amount < self.__balance:
            self.__balance -= amount
            print(f"Withdraw done, current balance: {self.__balance}")

        else:
            print("Not Suffiecient balance")

