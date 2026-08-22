# { "Depends": "py-genlayer:0.1.0" }
from genvm import *

class Hello(Contract):
    message: str = "Hello GenLayer"

    @call
    def say_hello(self, name: str) -> str:
        return f"{self.message}, {name}!"
    
    @write
    def set_message(self, new_msg: str):
        self.message = new_msg
