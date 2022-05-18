import uuid, random

def generate_uuid():
    return str(uuid.UUID(int=random.getrandbits(128)))
# For reproducibility, in the main module
# import random
# random.seed(0)

SEQUENTIAL_SEED = 1
def generate_sequential():
    global SEQUENTIAL_SEED
    idx = f'x{SEQUENTIAL_SEED}'
    SEQUENTIAL_SEED += 1
    return idx

generate_id = generate_sequential

