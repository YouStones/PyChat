import json

def load_data(file_name):
	with open(file_name, 'r+') as file:
		data = file.read()
		if not data:
			return None
		else:
			return json.loads(data)

def write_data(file_name, data):
	with open(file_name, 'w') as file:
		file.write(json.dumps(data))

def load(data):
	return json.loads(data)

def dump(data):
	return json.dumps(data)