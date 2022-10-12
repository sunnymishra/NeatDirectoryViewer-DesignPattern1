from src.model.singleton import SingletonType

class Logger(metaclass=SingletonType):
    val: str = None
    def __init__(self, value: str) -> None:
        self.val = value
        self.file = open(summary_log_file, "a")

    def some_business_logic(self):
        """
        Class level business logic, which will be executed on its single instance.
        """
        print("inside business logic")