import socket
import time
import os
import errno
import signal
import index

SERVER_ADDRESS = (HOST, PORT) = '', 8080
REQUEST_QUEUE_SIZE = 5

def grim_reaper(signum, frame):
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
        except OSError:
            return

        if pid == 0: # No more zombies
            return

def returnFile(filename):
	print("File:", filename, end="\n\n")
	try:
		reqFile= open('./' + filename, "r")
		http_response = reqFile.read()
		reqFile.close()
	except Exception as e:
		http_response = "<h1>404 Error. File not found!</h1>"
	return(http_response)

def infoFromURL(url, data):
	print("URL:", url)

	urllist = list(filter(bool, url.split('/')))
	info = ''
	if len(urllist) == 0:
		info = returnFile('index.html')
	elif urllist[0] == 'api':
		if urllist[1] == 'getRosterHTML':
			try:
				username = eval(data)['Username']
				password = eval(data)['Password']

				index.getCookies(username, password)
				for shift in index.getRoster():
					info += shift.html()
			except Exception as e:
				info = 'Error Occured: Believed cause incorrect data passed'
				print("Exception:", e)
	else:	
		info = returnFile(url)

	# filename = url if routes[url] == None else routes[url]
	return(info)

def handle_request(client_connection):
    request = client_connection.recv(1024).decode('utf-8')
    data = request.split('\r\n\r\n')[1]
    http_ok = b"HTTP/1.1 200 OK\n\n"

    urlRaw, httpRaw = request.split("\r\n", 1)

    url = urlRaw.split(' ')[1]

    http_response = infoFromURL(url, data)

    client_connection.sendall(http_ok + bytes(http_response, 'utf-8'))

def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port}'.format(port=PORT))

    signal.signal(signal.SIGCHLD, grim_reaper)

    while True:
        try:
            client_connection, client_address = listen_socket.accept()
        except IOError as e:
            code, msg = e.args
            # restart 'accept' if it was interrupted
            if code == errno.EINTR:
                continue
            else:
                raise

        pid = os.fork()
        if pid == 0:
            listen_socket.close()
            handle_request(client_connection)
            client_connection.close()
            os._exit(0)
        else:
            client_connection.close()

if __name__ == '__main__':
    serve_forever()
