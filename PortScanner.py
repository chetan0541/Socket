import socket 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = 'http://scanme.nmap.org/'

def portscan (port):
    try:
        s.connect((server, port))
        return True
    except:
        return False

for p in range (1,80):
    if portscan(p):
        print('Port',p,'is open')
    else:
        print('Port',p,'is closed')


#Reference : https://pythonprogramming.net/python-port-scanner-sockets/ 
