import asyncio
import os
import sys
import lib.gui as gui
import lib.data as d
import argparse

class Client(asyncio.Protocol):
	def __init__(self, on_con_lost, app, data):
		self.on_con_lost = on_con_lost
		self.app = app
		self.pseudo = None
		self.room_name = None
		self.data = data


	def connection_made(self, transport):
		self.transport = transport
		self.init_gui()


	def send(self, data_type, data):
		self.transport.write('{}:{}'.format(data_type, data).encode('UTF-8'))


	def data_received(self, data):
		raw_data = data.decode()

		while raw_data:
			data_len, raw_data = raw_data.split(':', 1)
			data = raw_data[:int(data_len)-1]
			raw_data = raw_data[int(data_len)-1:]
			data_type, data = data.split(':', 1)
			self.data_handler(data_type, data)


	def data_handler(self, data_type, data):
		if data_type == 'm':
			self.display(data)

		elif data_type == 'ep':
			self.display(data)

		elif data_type == 'cr':
			self.join_room(data)

		elif data_type == 'ecr':
			self.display(data)

		elif data_type == 'jr':
			self.focus_on_room(data)

		elif data_type == 'ejr':
			self.display(data)

		elif data_type == 'ur':
			self.update_room(data)

		else:
			print('Unrecognized data received : {}:{}'.format(data_type, data))


	def display(self, message):
		self.app.display(message)


	def set_pseudo(self):
		self.pseudo = self.app.pseudo_input.get()
		self.send('p', self.pseudo)


	def create_room(self):
		if not self.pseudo:
			self.app.edit_output('Please choose a pseudo in "Setting" tab')
			return
		self.send('cr', '{}/{}'.format(self.app.create_room_name.get(), self.app.max_clients.get()))


	def join_room(self, name):
		if not self.pseudo:
			self.app.edit_output('Please choose a pseudo in "Setting" tab')
			return
		self.send('jr', '{}'.format(name))


	def update_room(self, data):
		if not d.json2dic(data):
			self.app.join_button.config(state='disabled')
		else:
			self.app.join_button.config(state='normal')
			self.app.room_name_list.selection_set(0)

		rooms = d.json2dic(data)
		rooms_list = ['{0} [{1}/{2}]'.format(*i) for i in rooms]
		self.app.rooms_list.set(rooms_list)


	def request_room(self):
		self.send('ur', '')


	def focus_on_room(self, name):
		self.room_name = name
		self.app.set_room_name(self.room_name)
		self.app.msg_input.config(state='normal')
		for i, item in enumerate(self.app.tab_parent.tabs()): 
			self.app.tab_parent.tab(item, state='disabled')


	def init_gui(self):
		self.app.msg_input.config(state='disabled')
		self.app.root.protocol("WM_DELETE_WINDOW", lambda: self.transport.close()) 
		self.app.root.bind('<Escape>', lambda e: self.transport.close())
		self.app.create_button.config(command=self.create_room)
		self.app.join_button.config(command=self.check_rooms)
		# self.app.pseudo_button.config(command=self.save_pseudo)

		vcmd1 = (self.app.root.register(self.set_pseudo))
		self.app.pseudo_input.config(validatecommand=vcmd1)

		default_pseudo = d.fetch(self.data, 'pseudo')
		if default_pseudo:
			self.app.pseudo.set(default_pseudo)
			self.set_pseudo()

	def check_rooms(self):
		select_id = self.app.room_name_list.curselection()
		if not select_id:
			self.app.display('No room is currently selected')
			return
		self.join_room(self.app.room_name_list.get(select_id).rsplit(' [', 1)[0])


	def connection_lost(self, exc):
		print('et ?')
		print('The host closed the connection', exc)
		self.on_con_lost.set_result(True)


async def main():
	loop = asyncio.get_running_loop()

	on_con_lost = loop.create_future()
	app = gui.App()

	try:

		data = d.load('data.json')
		if not data:
			data = {'host':'127.0.0.1','port':'4145'}
			d.save('data.json', data)
		parser = argparse.ArgumentParser(description="A python client for chatting between Umons students")
		parser.add_argument('-i', '--ip',
							type=str,
							nargs='?',
							const=data['host'],
							default=data['host'],
							help="Set the host's ip for this session")
		parser.add_argument('-p', '--port',
							type=str,
							nargs='?',
							const=data['port'],
							default=data['port'],
							help="Set the host's port for this session")
		args = parser.parse_args()
		data['host'], data['port'] = args.ip, args.port

		transport, protocol = await loop.create_connection(lambda: Client(on_con_lost, app, data), data['host'], data['port'])

		async_tk = loop.create_task(updater(app.root, 1/120))

		try:
			await on_con_lost
		finally:
			print('con is lost')
			if not transport.is_closing():
				transport.close()
			async_tk.cancel()
			app.root.destroy()

	except ConnectionRefusedError:
		print("Can't connect to server {} on {}".format(data['host'], data['port']))

async def updater(root, interval):
	while True:
		root.update()
		await asyncio.sleep(interval)

asyncio.run(main())
	
# 	def set_room_name(self, name):
		# self.room_name = name
		# if not name:
		# 	self.app.room_name.set('Bienvenue dans Pychat !')
		# else:
		# 	self.app.room_name.set('[{}]'.format(name))



# 	def save_pseudo(self):
# 		default_data = d.load('data.json')
# 		default_data['pseudo'] = self.app.pseudo_input.get()
# 		d.save('data.json', default_data)
# 		self.set_pseudo()

