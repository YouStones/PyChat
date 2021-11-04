import threading
import os
import sys
import socket
import lib.gui as gui
import lib.data as d


class Client():
	def __init__(self):
		data = d.load_data('client_data.json')
		self.host, self.port = self.load(('host', 'port'))
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



	def load(self, data_wanted):
		data = d.load_data('client_data.json')
		data_fetch = list()
		for i in data_wanted:
			data_fetch.append(data[i])
		return data_fetch



	def connect(self):
		self.socket.settimeout(2)
		self.socket.connect((self.host, int(self.port)))
		self.socket.settimeout(None)



	def receive(self):
		data = self.socket.recv(1024).decode('UTF-8')
		if not data:
			return None
		else:
			return data.split(':', 1)



	def start_listening(self):
		threading.Thread(target=self.listening).start()



	def listening(self):
		while True:
			data = self.receive()

			if not data:
				self.close()
				break

			print('data :', data)

			data_type, msg = data

			if data_type == 'm':
				self.app.edit_output(msg)

			elif data_type == 'cr':
				print(data)
				print('message from server :', msg)
				self.join_room(msg)

			elif data_type == 'ecr':
				self.app.edit_output(msg)

			elif data_type == 'jr':
				self.set_room_name(msg)
				self.app.clear(self.app.display)
				self.app.msg_input.config(state='normal')
				self.app.create_button.config(state='disabled')
				self.app.root.bind('<Escape>', lambda event: self.leave_room())
				self.app.root.bind('<Return>', lambda event: self.send_message())

			elif data_type == 'ejr':
				self.app.edit_output(msg)

			elif data_type == 'r':
				if not d.load(msg):
					self.app.join_button.config(state='disabled')
				else:
					self.app.join_button.config(state='normal')
					self.app.room_name_list.selection_set(0)
				self.app.rooms_list.set(d.load(msg))



	def send(self, data_type, data):
		self.socket.send('{}:{}'.format(data_type, data).encode('UTF-8'))



	def send_message(self):

		msg = self.app.msg_input.get()

		if not msg or msg.isspace():
			return

		self.app.clear(self.app.msg_input)
		self.send('m', msg)



	def set_pseudo(self):
		self.pseudo = self.app.pseudo_input.get()
		self.send('p', self.pseudo)



	def set_gui(self):
		self.app.msg_input.config(state='disabled')
		self.app.root.bind('<Escape>', lambda event: self.quit())
		self.app.create_button.config(command=self.create_room)
		self.app.join_button.config(command=lambda: self.check_room_list())
		self.app.pseudo_button.config(command=lambda: self.set_pseudo())

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
		if not select_idcl:
			self.app.edit_output('No room is currently selected')
			return
		self.join_room(self.app.room_name_list.get(select_id))


	def join_room(self, name):
		print(name)
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

	data = d.load_data('client_data.json')

	if not data:
		data = {'host':'127.0.0.1','port':'4145'}
		d.write_data('client_data.json', data)

	if len(sys.argv) == 2:
		data['host'] = sys.argv[1]

	d.write_data('client_data.json', data)


	client = Client()

	try:
		client.connect()
	except:
		print('No server has been found at : {}, {}'.format(client.host, client.port))
		os._exit(1)

	client.start_listening()

	client.set_gui()

	client.app.root.mainloop()