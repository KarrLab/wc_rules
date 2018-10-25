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
        root = self.rete_net.get_root()
        root.receive_token(token,self,verbose)
        return self

    def send_tokens(self,tokens,verbose=False):
        for token in tokens:
            self.send_token(token)
        return self

    def select_random(self,pattern_id,variable_name,n=1):
        p = self.get_pattern(pattern_id)
        toks = p.select_random(n)
        new_var = pattern_id + ':' + variable_name
        return [tok[new_var] for tok in toks]

    def count(self,pattern_id):
        return self.get_pattern(pattern_id).count()

def main():
    pass

if __name__ == '__main__':
    main()
