import asyncio
import os
import sys
import json
import contextvars

clients = contextvars.ContextVar('clients', default=list())
clients_count = contextvars.ContextVar('clients_count', default=0)
rooms = contextvars.ContextVar('rooms', default=dict())
rooms_count = contextvars.ContextVar('rooms_count', default=0)

class Server(asyncio.Protocol):
	def __init__(self):
		pass

	def connection_made(self, transport):
		self.client = Client(transport)
		clients.get().append(self.client)

	def data_received(self, data):
		raw_data = data.decode()
		data_type, data = raw_data.split(':', 1)
		self.data_handler(data_type, data)

	def data_handler(self, data_type, data):
		if data_type == 'm':
			self.send_message(data)

		elif data_type == 'p':
			self.set_pseudo(data)

		elif data_type == 'cr':
			self.send(*self.create_room(data))

		elif data_type == 'jr':
			self.send(*self.join_room(data))

		elif data_type == 'lr':
			self.send(*self.leave_room())

	def send(self, data_type, data='', clients=None):
		if not clients:
			clients = (self.client,)
		length = len(data_type) + len(data) + 2
		for client in clients:
			client.transport.write('{}:{}:{}'.format(length, data_type, data).encode('UTF-8'))


	def send_message(self, data):
		self.send('m', data, self.client.room.clients)


	def set_pseudo(self, data):
		self.client.set_pseudo(data)


	def create_room(self, data):
		name, max_clients = data.split('/')

		if not name or name.isspace():
			name = 'room#{}'.format(rooms_count.get())
			rooms_count.set(rooms_count.get() + 1)
			print(rooms_count.get())

		elif name in rooms.get():
			return 'ecr', 'The room name "{}" is already taken'.format(name)

		rooms.get()[name] = Room(name, max_clients)

		return ('cr', name)


	def join_room(self, data):
		if not data in rooms.get():
			self.send('ejr', 'No room named "{}" has been found'.format(msg))
			return

		room = rooms.get()[data]
		if room.clients_count == room.max_clients:
			self.send('ejr', 'The room "{}" is full'.format(msg))
			return

		self.client.room = room
		room.add(self.client)
		self.send('m', '{} joined the room'.format(self.client.pseudo), [c for c in self.client.room.clients if c != self.client])

		return ('jr', data)


	def leave_room(self):
		if not self.client.room:
			return ('elr', "You're not currently in a room")

		else:
			self.send('m', '{} left the room'.format(self.client.pseudo), [c for c in clients.get() if c != self.client])
			self.client.room.remove(self.client)

		if self.client.room.clients_count == 1:
			self.delete_room(self.client.room)

		self.client.room = None

		return ('lr',)

	def delete_room(self, room):
		rooms.get().remove(room.name)
		self.send()

	def eof_received(self):
		pass

	def connection_lost(self, exc):
		if exc: print('ERROR : ', exc)
		print("Lost connection with client", self.client.pseudo)
		clients.get().remove(self.client)
		if self.client.room:
			self.client.room.remove(self.client)
		self.client.transport.close


	def shutdown(self, client):
		client.conn.shutdown(socket.SHUT_RD)



class Client():
	def __init__(self, transport):
		self.transport = transport
		self.pseudo = 'Client#{}'.format(clients_count.get())
		clients_count.set(clients_count.get() + 1)
		self.room = None

	def set_pseudo(self, pseudo):
		self.pseudo = pseudo

	def set_room(self, room):
		self.room = room



class Room():
	def __init__(self, name, max_clients):
		self.name = name
		self.max_clients = max_clients
		self.clients = list()
		self.clients_count = 0


	def add(self, client):
		self.clients.append(client)
		self.clients_count += 1


	def remove(self, client):
		self.clients.remove(client)
		self.clients_count -= 1


async def main(host, port):

	loop = asyncio.get_running_loop()

	server = await loop.create_server(lambda: Server(), host, port)

	async with server:
		await server.serve_forever()


if __name__ == '__main__':

	try:
		asyncio.run(main('', 4145))
	except KeyboardInterrupt:
		print('\rserver shutdown')
	except Exception as e:
		print('ERROR :', e)