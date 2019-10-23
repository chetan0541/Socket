import socket 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       #Making a socket. socket_AFINET = address family IP4. socket.SOCK_STREAM = TCP protocol
server = 'scanme.nmap.org'

def portscan (port):
    try:
        s.connect((server, port))
        return True
    except:
        return False

for p in range (1,81):
    if portscan(p):
        print('Port',p,'is open')
    else:
        print('Port',p,'is closed')


#Reference : https://pythonprogramming.net/python-port-scanner-sockets/ 
