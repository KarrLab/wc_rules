
superset_log_locations = ['Start','End','Class','Canonical Label','Pattern','Variable']

LOG_LOCATIONS = []

def validate_log_locations():
	return all([x in superset_log_locations for x in LOG_LOCATIONS])

class Logger:
	@staticmethod
	def write(location,number,token):
		if location in LOG_LOCATIONS:
			print(f'{location}:{number} Token:{token}')
		return

	@staticmethod
	def start(number,token):
		Logger.write('Start',number,token)
		return

	@staticmethod
	def end(number,token):
		Logger.write('End',number,token)
		return 

	@staticmethod
	def _class(number,token):
		Logger.write('Class',number,token)
		return 

	@staticmethod
	def canonical_label(number,token):
		Logger.write('Canonical Label',number,token)
		return 

	@staticmethod
	def pattern(number,token):
		Logger.write('Pattern',number,token)
		return 

	@staticmethod
	def variable(number,token):
		Logger.write('Variable',number,token)
		return 
