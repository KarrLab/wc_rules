from .rete_net import ReteNet
from .rete_build import increment_net_with_pattern

class Matcher(object):
    def __init__(self):
        self.rete_net = ReteNet()

    # Matcher-level operations
    def add_pattern(self,pattern):
        increment_net_with_pattern(self.rete_net,pattern)
        return self

    def send_token(self,token,verbose):
        root = self.rete_net.get_root()
        root.receive_token(token,self,verbose)
        return self

def main():
    pass

if __name__ == '__main__':
    main()
