import socket
import json
import hashlib
from time import sleep
class Server:
	def __init__(self, address, port):
		self.address=address
		self.port=port
		self.s=None
	def connect(self,s=None):
		if self.s is None:
			if s is None:
				self.s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			else:
				self.s=s
		self.s.connect((self.address,int(self.port)))
	def disconnect(self):
		self.s.close()
		self.s=None
	def __str__(self):
		return self.address+":"+self.port

class Komunikator:
	def __init__(self,user=None,hpasswd=None):
		self.servers=[]
		if user is None:
			user=input('Podaj login: ')
		if hpasswd is None:
			m=hashlib.md5()
			m.update(input("Podaj hasło:").encode("utf-8"))
			hpasswd=m.hexdigest()
		self.user=(user,hpasswd)
	def set_user(self,user,hpasswd):
		self.user=(user,hpasswd)
	def add_server(self,address,port):
		self.servers.append(Server(address,port))
	def send_via(self,target,msg,server_no=0):
		self.servers[server_no].connect()
		msg_structure={}
		msg_structure["login"]=self.user[0]
		msg_structure["hash"]=self.user[1]
		msg_structure["cmd"]="send"
		msg_structure["target"]=target
		msg_structure["msg"]=msg
		final_msg=json.dumps(msg_structure).encode("ascii")
		print(final_msg)
		total=0
		msglen=len(final_msg)
		while True:
			sent=self.servers[server_no].s.send(final_msg[total:])
			total+=sent
			if sent==0 or total>=msglen:
				break
		self.servers[server_no].disconnect()
		
	def recv_from(self,server_no=0):
		self.servers[server_no].connect()
		msg_structure={}
		msg_structure["login"]=self.user[0]
		msg_structure["hash"]=self.user[1]
		msg_structure["cmd"]="recv"
		final_msg=json.dumps(msg_structure).encode("ascii")
		total=0
		msglen=len(final_msg)
		while True:
			sent=self.servers[server_no].s.send(final_msg[total:])
			total+=sent
			if sent==0 or total>=msglen:
				break
		chunks=[]
		while True:
			chunk=self.servers[server_no].s.recv(10239)
			chunks.append(chunk)
			if len(chunk)==0:
				break
		self.servers[server_no].disconnect()
		return b''.join(chunks)	
		
	def register_on(self,server_no=0):
		self.servers[server_no].connect()
		msg_structure={}
		msg_structure["login"]=self.user[0]
		msg_structure["hash"]=self.user[1]
		msg_structure["cmd"]="register"
		final_msg=json.dumps(msg_structure).encode("ascii")
		total=0
		msglen=len(final_msg)
		while True:
			sent=self.servers[server_no].s.send(final_msg[total:])
			total+=sent
			if sent==0 or total>=msglen:
				break
		self.servers[server_no].disconnect()
	def menu(self):
		cmd=input('''
Podaj komendę:
	send by wysłać wiadomość,
	recv by odebrać wiadomości,
	register by zarejestrować się na serwerze.
	user by zmienić użytkownika
''')
		if(cmd=="send"):
			txt=input("Podaj treść wiadomości: ")
			to=input("Podaj odbiorcę: ")
			self.send_via(to,txt,0)
		elif(cmd=="recv"):
			msgs=json.loads(self.recv_from(0))
			for msg in msgs:
				print(msg["from"],msg["msg"])
		elif(cmd=="register"):
			self.register_on(0)
		elif(cmd=="user"):
			user=input("Podaj login: ")
			passwd=input("Podaj hasło: ")
			m=hashlib.md5()
			m.update(passwd.encode("ascii"))
			self.set_user(user,m.hexdigest())
		self.menu()
m=hashlib.md5()
m.update(b'123')
k=Komunikator("ja",m.hexdigest() )

k.add_server("192.168.100.182","20000")
k.menu()
