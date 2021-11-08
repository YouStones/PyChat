import json

def load_data(file_name):
	with open(file_name, 'r+') as file:
		data = file.read()
		if not data:
			return None
		else:
			return load(data)

def save_data(file_name, data):
	with open(file_name, 'w') as file:
		file.write(dump(data))

def fetch(data, *data_wanted):
	return tuple([data[n] for n in data_wanted])

def load(data):
	return json.loads(data)

def dump(data):
	return json.dumps(data)