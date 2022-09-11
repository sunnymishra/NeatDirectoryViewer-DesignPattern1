from threading import Lock, Thread

class SingletonType(type):
    """
    The SingletonType class can be implemented in various ways in Python, eg. base class, decorator, metaclass. 
    A class is an instance of its metaclass.
    The (only) instance of Logger class will be of type 'your_module.Logger'. Try type(obj).
    However, Logger class in itself will be of type 'your_module.SingletonType'. Try type(Logger).
    When you call logger with Logger(), Python first asks the metaclass of Logger i.e. SingletonType, what to do, allowing instance creation to be pre-empted and controller in our SingletonType class.

    The most common reason for using Singletons is to control access to some shared resource, eg. a database or a file eg. Log file.
    """

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        Any change to the `__init__` argument do not affect the created instance.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super(SingletonType, cls).__call__(*args, **kwargs)
                cls._instances[cls] = instance
            else:
                # If you don't want to run this __init__ every time the class is called,
                # then comment it
                cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


class Logger(metaclass=SingletonType):
    val: str = None
    def __init__(self, value: str) -> None:
        self.val = value

    def some_business_logic(self):
        """
        Class level business logic, which will be executed on its instance.
        """
        print("inside business logic")

def test(value: str) -> None:
    obj = Logger(value)

    print(type(obj))
    print(type(Logger))

    print(obj.val)

if __name__ == "__main__":
    # The client code.

    s1 = Logger("a")
    s2 = Logger("b")
    s1.some_business_logic()
    if id(s1) == id(s2):
        print("Singleton works, both variables contain the same instance.")
    else:
        print("Singleton failed, variables contain different instances.")

    process1 = Thread(target=test, args=("FOO",))
    process2 = Thread(target=test, args=("BAR",))
    process1 = Thread(target=test, args=("ABC",))

    process1.start()
    process2.start()
