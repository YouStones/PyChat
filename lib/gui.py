import tkinter as tk
import tkinter.ttk as ttk
import re

font_families = ['Lucida Fax', 'Liberation Mono', 'Noto Sans CJK SC', 'Ubuntu Mono', 'Noto Mono']

class App():
	def __init__(self):
		self.root = tk.Tk()
		self.root.title("Pychat")
		self.root.configure(background='white')
		self.root.resizable(False, False)
		self.s = ttk.Style()
		self.create_frame()
		self.create_widget()
		self.show()
		self.set_style()

	def create_frame(self):

		### Main frames ###

			# Create main frames
			self.content = ttk.Frame(self.root, style='TFrame')
			self.border = ttk.Frame(self.root, style='Border.TFrame')
			self.menu = ttk.Frame(self.root, style='TFrame')

		### Menu frames ###

			# Create tab parent and tab
			self.tab_parent = ttk.Notebook(self.menu, style='TNotebook')

			self.setting_tab = ttk.Frame(self.tab_parent)
			self.join_tab = ttk.Frame(self.tab_parent)
			self.create_tab = ttk.Frame(self.tab_parent)

			# Add tabs to tab parent
			self.tab_parent.add(self.setting_tab, text='Setting', sticky="nswe")
			self.tab_parent.add(self.join_tab, text='Join', sticky="nswe")
			self.tab_parent.add(self.create_tab, text='Create', sticky="nswe")

			# Create structure frames
			self.setting_inputs = ttk.Frame(self.setting_tab)
			# self.join_inputs = ttk.Frame(self.join_tab)
			self.create_inputs = ttk.Frame(self.create_tab)


	def create_widget(self):

		### Setting tab ###

			# Pseudo label
			self.pseudo_label=ttk.Label(
				self.setting_inputs,
				text='Pseudo :')

			# Pseudo input
			self.pseudo = tk.StringVar()
			self.pseudo.trace('w', lambda *args, string_var=self.pseudo, len_max=16:
				self.check_len(string_var, len_max, *args))

			self.pseudo_input = ttk.Entry(
				self.setting_inputs,
				style='TEntry',
				width=16,
				textvariable=self.pseudo,
				font=('Liberation Mono', 11),
				validate='focusout'
				)

			self.pseudo_button = ttk.Button(
				self.setting_tab,
				style='TButton',
				text='Save'
				)

		### Join tab ###

			# Rooms list
			self.rooms_list = tk.StringVar(value=[])
			self.room_name_list = tk.Listbox(
				self.join_tab,
				listvariable=self.rooms_list,
				borderwidth=0,
				width=16,
				height=10
				)

			self.join_button = ttk.Button(
				self.join_tab,
				style='TButton',
				text='Join'
				)

		### Create tab ###

			# Room name label
			self.create_room_name_label = ttk.Label(
				self.create_inputs,
				text='Room name :')

			# Room name input
			self.create_room_name = tk.StringVar()
			self.create_room_name.trace('w', lambda *args, string_var=self.create_room_name, len_max=15:
				self.check_len(string_var, len_max, *args))

			self.create_room_name_input = ttk.Entry(
				self.create_inputs,
				style='TEntry',
				width=15,
				textvariable=self.create_room_name,
				font=('Liberation Mono', 11))

			# Max client label
			self.max_clients_label = ttk.Label(
				self.create_inputs,
				text='Max client :')

			# Max client input
			
			self.max_clients = tk.StringVar()
			self.max_clients.set(10)

			vcmd2 = (self.root.register(self.check_value), '%P', 2, 99)

			self.max_clients = tk.StringVar(value='10')

			self.max_clients_input = ttk.Entry(
				self.create_inputs,
				style='TEntry',
				width=2,
				textvariable=self.max_clients,
				font=('Liberation Mono', 11),
				validate='focusout',
				validatecommand=vcmd2
				)

			self.create_button = ttk.Button(
				self.create_tab,
				style='TButton',
				text='Create'
				)

		### Content ###

			# Room name
			self.room_name = tk.StringVar(value='[/]')
			self.room_name_display = ttk.Label(
				self.content,
				style='RoomName.TLabel',
				textvariable=self.room_name
				)

			# Display
			self.display = tk.Text(
				self.content,
				borderwidth=0,
				highlightthickness=0,
				wrap='word',
				width=50,
				height=20,
				padx=5,
				pady=5)

			# [>] signe
			self.write_sign = ttk.Label(
				self.content,
				style='WriteSign.TLabel',
				text='>'
				)

			# Message input
			self.msg = tk.StringVar()
			self.msg_input = ttk.Entry(
				self.content,
				style='TEntry',
				width=50,
				textvariable=self.msg,
				state='disabled',
				font=('Liberation Mono', 12)
			)

			self.display.config(state='disabled')
			# self.room_name_list.config(state='disabled')


	def show(self):

		### Show frames ###

			self.content.grid(column=2, row=0)
			self.border.grid(column=1, row=0, padx=(1,0), sticky='ns')
			self.menu.grid(column=0, row=0, sticky='ns')
			self.tab_parent.grid(column=0, row=0, sticky='nwse')

			self.setting_tab.columnconfigure(0, weight=1)
			self.setting_tab.rowconfigure(1, weight=1)
			self.join_tab.columnconfigure(0, weight=1)
			self.join_tab.rowconfigure(1, weight=1)
			self.create_tab.columnconfigure(0, weight=1)
			self.create_tab.rowconfigure(1, weight=1)

			self.setting_inputs.grid(column=0, row=0, pady=(10,0), padx=(15,15), sticky='w')
			# self.join_inputs.grid(column=0, row=0, pady=(10,0), padx=(15,0), sticky='w')
			self.create_inputs.grid(column=0, row=0, pady=(10,0), padx=(15,0), sticky='w')

		### Show widgets ###

			# Content
			self.room_name_display.grid(column=0, row=0, sticky='nswe', columnspan=2)
			self.display.grid(column=0, row=1, sticky='nswe', columnspan=2)
			self.write_sign.grid(column=0, row=2, sticky='ws')
			self.msg_input.grid(column=1, row=2, sticky='wse')

			# Setting tab
			self.pseudo_label.grid(column=0, row=0, sticky='w')
			self.pseudo_input.grid(column=0, row=1)
			self.pseudo_button.grid(column=0, row=1, sticky='s')

			# Join tab
			self.room_name_list.grid(column=0, row=1, pady=(20,0))
			self.join_button.grid(column=0, row=2, pady=(20,0))

			# Create tab
			self.create_room_name_label.grid(column=0, row=0, sticky='w')
			self.create_room_name_input.grid(column=0, row=1, sticky='w')
			self.max_clients_label.grid(column=0, row=2, sticky='w', pady=(5,0))
			self.max_clients_input.grid(column=0, row=3, sticky='w')
			self.create_button.grid(column=0, row=1, sticky='s')


	def edit_output(self, msg):
		self.display.config(state='normal')
		self.display.insert('end', msg+'\n')
		self.display.see('end')
		self.display.config(state='disabled')


	def clear(self, widget):
		widget.delete(0, 'end')


	def check_len(self, string_var, len_max, *args):
		if len(string_var.get()) > len_max:
			string_var.set(string_var.get()[:len_max])

	def check_value(self, value, min_value, max_value):
		if value == '' or value.isspace() or not value.isdigit():
			return False
		if int(value) > int(max_value): self.max_clients.set(max_value)
		if int(value) < int(min_value): self.max_clients.set(min_value)
		return True


	def check_regex(self, string_var, regex, *args):
		# ^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$
		return re.search(regex, string_var.get())


	def set_style(self):
		self.s.configure(".",
			background='white',
			font=('Liberation Mono', 11)
			)

		self.s.configure('TButton',
			padding=(10,5),
			width=0,
			focuscolor='white'
			)

		self.s.configure('TNotebook',
			borderwidth=0,
			bordercolor='white',
			background='white',
			tabmargins=(0,0,0,0)
			)

		self.s.configure('TNotebook.Tab',
			borderwidth=0,
			focuscolor='white',
			padding=(5,1),
			bevelamount=0,
			state='disabled')

		self.s.map('TNotebook.Tab',
			background=[
				('selected', 'white'),
				('!selected', 'grey85')],
			font=[
				('selected', ('Liberation Mono', 11)),
				('!selected', ('Liberation Mono', 11))])

		self.s.configure("TEntry",
			padding='5 5 5 5',
			borderwidth=0,
			highlightthickness=0
			)

		self.s.map('TEntry',
			fieldbackground=[
				('disabled', 'grey95'),
				('!disabled', 'grey95')],
			fieldforeground=[
				('disabled', 'black')]
			)

		self.s.configure('WriteSign.TLabel',
			background='grey95',
			padding=(5,5,3,4)
			)

		self.s.configure('RoomName.TLabel',
			background='grey85',
			padding=(0,2),
			font=('Liberation Mono', 12),
			anchor='center'
			)

		self.s.configure('Border.TFrame',
			background='grey85')

		self.s.configure('test.TFrame',
			background='red')