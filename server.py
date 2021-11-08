import threading
import socket
import os
import sys
import json

class Server():
	def __init__(self, port):
		self.port = port
		self.clients_count = 0
		self.rooms_count = 0
		self.rooms = dict()
		self.threads = list()
		self.clients = list()

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(('', self.port))



	def listen(self):
		self.socket.listen(5)

		try:
			while True:
				client = Client(self.socket.accept(), self)

				print('New connection from {}'.format(client.address[0]))
				new_thread = threading.Thread(target=self.listening, args=(client,))
				new_thread.start()
				self.clients.append(client)
				self.threads.append(new_thread)
				
		except KeyboardInterrupt:
			print('\rServer shutting down !')

			for client in self.clients:
				self.shutdown(client)

			for thread in self.threads:
				thread.join()

			self.socket.close()



	def send_rooms_list(self, client):
		self.send(client, 'r', json.dumps([*self.rooms]))



	def create_room(self, name, max_clients):
		self.rooms[name] = Room(name, max_clients)
		for client in self.clients:
			self.send_rooms_list(client)



	def delete_room(self, name):
		self.rooms.pop(name)
		for client in self.clients:
			self.send_rooms_list(client)



	def send(self, client, data_type, data):
		length = len('{}:{}'.format(data_type, data))
		print(length)
		length += len(str(length))+1
		client.conn.send('{}:{}:{}'.format(data_type, length, data).encode('UTF-8'))



	def listening(self, client):
		self.send_rooms_list(client)
		while True:
			data = client.conn.recv(1024).decode('UTF-8')

			if not data:
				break

			data_type, msg = data.split(':', 1)

			print(data)

			if data_type == 'm' and client.room:
				for other_client in client.room.clients:
					self.send(other_client, 'm', '{} >> {}'.format(client.pseudo, msg))

			elif data_type == 'p':
				client.pseudo = msg

			elif data_type == 'cr':
				name, max_clients = msg.split('/')
				print('creating a new room :', name, max_clients)
				if name == '':
					name = 'room#{}'.format(self.rooms_count)
					self.rooms_count += 1

				elif name in self.rooms:
					self.send(client, 'ecr', 'The room name "{}" is already taken'.format(name))
					return

				print('room name :', name)
				self.send(client, 'cr', name)
				self.create_room(name, max_clients)

			elif data_type == 'jr':
				print('Searching room...')
				if not msg in self.rooms:
					self.send(client, 'ejr', 'No room named "{}" has been found'.format(msg))
					continue

				room = self.rooms[msg]

				print('Room found :', room)

				if int(len(room.clients)) == int(room.max_clients):
					self.send(client, 'ejr', 'The room "{}" is full'.format(msg))
					continue

				print('Room is not full :',len(room.clients),'/',room.max_clients)

				client.room = room
				client.room.add_client(client)

				print('Adding client to room...')
				self.send(client, 'jr', msg)

				for other_client in client.room.clients:
					if other_client.conn.getpeername() == client.conn.getpeername():
						continue
					self.send(other_client, 'm', '{} joined the room'.format(client.pseudo))


			elif data_type == 'lr':
				if len(client.room.clients) == 1:
					self.delete_room(client.room.name)
				else:
					for other_client in client.room.clients:
						if other_client.conn.getpeername() == client.conn.getpeername():
							continue
						self.send(other_client, 'm', '{} left the room'.format(client.pseudo))
					client.room.remove_client(client)
				client.room = None

		if client.room:
			client.room.remove_client(client)
			for other_client in client.room.clients:
				if other_client.conn.getpeername() == client.conn.getpeername():
					continue
				self.send(other_client, 'm', '{} left the room'.format(client.pseudo))

		print('{}/{} is disconnected'.format(client.address[0], client.pseudo))
		client.conn.close()
		self.clients.remove(client)



	def shutdown(self, client):
		client.conn.shutdown(socket.SHUT_RD)




class Client():
	def __init__(self, info, server):
		self.conn, self.address = info
		self.pseudo = 'Client#{}'.format(server.clients_count)
		server.clients_count += 1
		self.room = None



class Room():
	def __init__(self, name, max_clients):
		self.name = name
		self.max_clients = max_clients
		self.clients = list()


	def add_client(self, client):
		self.clients.append(client)


	def remove_client(self, client):
		self.clients.remove(client)




if __name__ == '__main__':
	server = Server(4145)
	server.listen()
