from enum import Enum
from os.path import join
class Prompt(Enum):
    INFO_DESCRIPCION ="descripcion_de_productos.txt"

def load_prompt(prompt: Prompt) -> str:
    prompt_path = join("prompts", prompt.value)
    with open(prompt_path) as f:
        print(f.read())
        return f.read()