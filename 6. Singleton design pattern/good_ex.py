class Logger:
    # Class Variable
    __instance = None
    __initialized = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, file_name):
        # Only run this once!
        if not self.__initialized:
            self.file_name = file_name
            self.log_count = 0
            self.__class__.__initialized = True # Mark as done

    def log(self, msg):
        print(f"Logging {msg} in {self.file_name}")
        self.log_count += 1

    def get_log_count(self) -> int:
        return self.log_count


log1 = Logger("app.log")
log1.log("Hey")

log2 = Logger("app.log")
log2.log("Bye")

log3 = Logger("app.log")
log3.log("Good")

print(log1.get_log_count())
print(log2.get_log_count())
print(log3.get_log_count())