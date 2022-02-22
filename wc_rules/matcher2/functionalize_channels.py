# see tokens.py for the different types of tokens

class FunctionalizeChannels:

	def function_channel_pass(self,channel,token):
		node = self.get_node(core=channel.target)
		node.state.incoming.append(token)
		return self