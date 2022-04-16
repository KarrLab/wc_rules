import uuid, random

def generate_id():
    return str(uuid.UUID(int=random.getrandbits(128)))

# For reproducibility, in the main module
# import random
# random.seed(0)