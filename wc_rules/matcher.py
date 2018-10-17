from .rete_net import ReteNet
from .rete_build import increment_net_with_pattern

class Matcher(object):
    def __init__(self):
        self.rete_net = ReteNet()
        self.pattern_nodes = dict()

    # Matcher-level operations
    def add_pattern(self,pattern):
        current_node = increment_net_with_pattern(self.rete_net,pattern)
        self.pattern_nodes[pattern.id] = current_node
        return self

    def get_pattern(self,pattern_id):
        return self.pattern_nodes[pattern_id]

    def send_token(self,token,verbose=False):
        print(" ".join(['sending token',str(token)]))
        root = self.rete_net.get_root()
        root.receive_token(token,self,verbose)
        return self

def main():
    pass

if __name__ == '__main__':
    main()
