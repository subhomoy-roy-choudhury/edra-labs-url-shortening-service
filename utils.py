import string
import random

def random_alias_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))