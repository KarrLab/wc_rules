# see tokens.py for the different types of tokens
class ChannelFunctions:

	def function_channel_pass(self,channel,token):
		node = self.get_node(core=channel.target)
		node.state.incoming.append(token)
		return self

	def function_channel_transform(self,channel,token):
		newtoken = channel.data.transformer.transform(token,channel=channel.num)
		self.function_channel_pass(channel,newtoken)
		return self