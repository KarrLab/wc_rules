import uuid, random

######## random name generator
# To modify this seed, load this module, then execute this_module.idgen.seed(<new_seed>)
idgen = random.Random()
idgen.seed(0)

def generate_id():
    return str(uuid.UUID(int=idgen.getrandbits(128)))


class RandomIDXGenerator:

    def __init__(self,seed=0):
        self.seed = seed
        self.idgen = random.Random()
        self.idgen.seed(0)

    def generate_id(self):
        return str(uuid.UUID(int=self.idgen.getrandbits(128)))

