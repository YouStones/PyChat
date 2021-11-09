import threading
import os
import sys
import socket
import lib.gui as gui
import lib.data as d
import argparse


class Client():
	def __init__(self):
		self.load()
		self.host, self.port = d.fetch(self.data, 'host', 'port')
		self.pseudo = None

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.app = gui.App()
		self.set_room_name(None)


	
	def set_room_name(self, name):
		self.room_name = name
		if not name:
			self.app.room_name.set('Bienvenue dans Pychat !')
		else:
			self.app.room_name.set('[{}]'.format(name))



	def load(self):
		self.data = d.load('data.json')
		if not self.data:
			self.data = {'host':'127.0.0.1','port':'4145'}
			d.save('data.json', self.data)

		parser = argparse.ArgumentParser(description="A python client for chatting between Umons students")
		parser.add_argument('-i', '--ip',
							type=str,
							nargs='?',
							const=self.data['host'],
							default=self.data['host'],
							help="Set the host's ip for this session")
		parser.add_argument('-p', '--port',
							type=str,
							nargs='?',
							const=self.data['port'],
							default=self.data['port'],
							help="Set the host's port for this session")
		args = parser.parse_args()

		self.data['host'], self.data['port'] = args.ip, args.port


	def connect(self):
		self.socket.settimeout(2)
		self.socket.connect((self.host, int(self.port)))
		self.socket.settimeout(None)



	def receive(self):
		data = self.socket.recv(1024).decode('UTF-8')
		if not data:
			return None
		else:
			return data



	def start_listening(self):
		threading.Thread(target=self.listening).start()



	def listening(self):
		while True:
			data = self.receive()

			if not data:
				self.close()
				break


			_, data_len, _ = data.split(':', 2)
			while int(data_len) <= len(data):
				data_type, _, data = data.split(':', 2)
				if int(data_len) < len(data):
					data = data[data_len:]
					_, data_len, _ = data.split(':', 2)
				self.data_handler(data_type, data)



	def data_handler(self, data_type, data):

			if data_type == 'm':
				self.app.edit_output(data)

			elif data_type == 'cr':
				print(data)
				print('message from server :', data)
				self.join_room(data)

			elif data_type == 'ecr':
				self.app.edit_output(data)

			elif data_type == 'jr':
				self.set_room_name(data)
				self.app.clear(self.app.display)
				self.app.msg_input.config(state='normal')
				self.app.create_button.config(state='disabled')
				self.app.root.bind('<Escape>', lambda event: self.leave_room())
				self.app.root.bind('<Return>', lambda event: self.send_message())

			elif data_type == 'ejr':
				self.app.edit_output(data)

			elif data_type == 'r':
				if not d.json2dic(data):
					self.app.join_button.config(state='disabled')
				else:
					self.app.join_button.config(state='normal')
					self.app.room_name_list.selection_set(0)
				self.app.rooms_list.set(d.json2dic(data))



	def send(self, data_type, data):
		self.socket.send('{}:{}'.format(data_type, data).encode('UTF-8'))



	def send_message(self):

		msg = self.app.msg_input.get()

		if not msg or msg.isspace():
			return

		self.app.clear(self.app.msg_input)
		self.send('m', msg)



	def set_pseudo(self):
		default_data = d.load('data.json')
		print(data)
		default_data['pseudo'] = self.app.pseudo_input.get()
		d.save('data.json', default_data)



	def set_gui(self):
		self.app.msg_input.config(state='disabled')
		self.app.root.bind('<Escape>', lambda event: self.quit())
		self.app.create_button.config(command=self.create_room)
		self.app.join_button.config(command=self.check_room_list)
		self.app.pseudo_button.config(command=self.set_pseudo)

		vcmd1 = (self.app.root.register(self.set_pseudo))
		self.app.pseudo_input.config(validatecommand=vcmd1)



	def create_room(self):
		if not self.pseudo:
			self.app.edit_output('Please choose a pseudo in "Setting" tab')
			return
		name = self.app.create_room_name.get()
		max_clients = self.app.max_clients.get()
		self.send('cr', '{}/{}'.format(name, max_clients))


	def check_room_list(self):
		select_id = self.app.room_name_list.curselection()
		print(select_id)
		if not select_id:
			self.app.edit_output('No room is currently selected')
			return
		self.join_room(self.app.room_name_list.get(select_id))


	def join_room(self, name):
		print(self.pseudo)
		if not self.pseudo:
			self.app.edit_output('Please choose a pseudo in "Setting" tab')
			return
		self.send('jr', '{}'.format(name))



	def leave_room(self):
		self.send('lr', '{}'.format(self.room_name))
		
		self.set_room_name(None)
		self.app.clear(self.app.display)
		self.app.create_button.config(state='enabled')
		self.app.msg_input.config(state='disabled')
		self.app.root.bind('<Escape>', lambda event: self.quit())



	def close(self):
		self.socket.close()
		self.app.root.after(10, self.app.root.destroy)



	def quit(self):
		self.socket.shutdown(socket.SHUT_RD)



if __name__ == '__main__':


	client = Client()

	try:
		client.connect()
	except:
		print('No server has been found at : {}, {}'.format(client.host, client.port))
		os._exit(1)

	client.start_listening()

	client.set_gui()

	client.app.root.mainloop()