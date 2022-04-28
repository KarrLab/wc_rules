# see tokens.py for the different types of tokens
from .token import VarToken

class ChannelFunctions:

	def function_channel_pass(self,channel,token):
		node = self.get_node(core=channel.target)
		node.state.incoming.append(token)
		return self

	def function_channel_transform(self,channel,token):
		if token.action not in channel.data.allowed_token_actions:
			return self
		if not channel.data.filter_data(token.data):
			return self
		newtoken = channel.data.transformer.transform(token,channel=channel.num)
		self.function_channel_pass(channel,newtoken)
		return self

	def function_channel_variable_update(self,channel,token):
		token = VarToken(variable=channel.data.variable)
		self.function_channel_pass(channel,token)
		return 

