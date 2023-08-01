import json

class Config:
	settings = None
	
	@classmethod
	def get_settings(cls):
		if cls.settings == None:
			with open('config.json', 'r') as f:
				cls.settings = json.load(f)
		return cls.settings