import json

def load(file_name):
	with open(file_name, 'w+') as file:
		data = file.read()
		return None if not data else json.loads(data)


def json2dic(data):
	return json.loads(data)

def dic2json(data):
	return json.dumps(data)


def save(file_name, data):
	with open(file_name, 'w') as file:
		file.write(json.dumps(data))


def fetch(data, *data_wanted):
	return [data[n] for n in data_wanted]
