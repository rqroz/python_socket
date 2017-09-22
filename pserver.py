import os
import socket
import re
from datetime import datetime

# DEFAULT VALUES
HOST = '' # Server IP
PORT = 8080 # Server Port
SERVER_NAME = 'CONNET' # Server Name 
BASE_FILE_PATH = "files_container" # Base path for files
INDEX_PATH = "/index.html" # Index subpath file
CONNECTION_TYPE_CLOSE = 'close' # Connection Type for closing connection
METHOD_REGEX = '([A-Z]{3,4} (\/)?(\w{0,})(.html)? HTTP\/1.1)'
CONNECTION_REGEX = '(Connection: [a-z]+-?[a-z]+)'

# Returns a file opened by a given path and the corresponding status according with the existing of the file
def get_file(path, status):
	try:
		http_file = open(BASE_FILE_PATH+path, "r")
	except Exception as e:
		print("Could not resolve file... " + str(e))
		http_file = open(BASE_FILE_PATH+'/404.html', 'r')
		status = 404

	return http_file, status

# Returns the file opened with the subpath given, the header text (first line in the http response), and the http status 
def get_objects(path, status):
	http_file_path, text = None, None
	if status == 200 and path: # If path is defined and status is 200, define success parameters
		http_file_path = INDEX_PATH if (file_path == '/' or file_path == '/index.html') else file_path
		text = "HTTP/1.1 200 OK \r\n\r\n"
	elif status == 400: # This case occurs when status != 200 (defaults for 400)
		http_file_path = '/400.html'
		text = "HTTP/1.1 400 Client Error \r\n\r\n"

	if http_file_path and text:
		_file, status = get_file(http_file_path, status) # Gets file object and updates status according to the existence of the file
		text = "HTTP/1.1 404 Not Found \r\n\r\n" if status == 404 else text # Updates text variable if the file was not found
		return _file, status, text
	else:
		return None, None, None

# Returns the size of an opened file
def opened_file_size(file):
	file.seek(0, 2)
	return file.tell()

# Read multiple lines from socket
def readlines(sock, recv_buffer=4096, delim='\n'):
	buffer = ''
	data = True
	while data:
		try:
			# Get current line of data sent by the client
			data = sock.recv(recv_buffer)
			# Store the corresponding string into buffer
			buffer += data.decode("utf-8")
		except: 
			# If tried to recv() after sock.timeout or could not decode the data, exit
			return
		else:
			# If buffer is not "\n" nor a string composed only by white spaces, yield the written string
			# without the new line character
			if buffer.find(delim) > 1 and not buffer.isspace():
				lines = buffer.split('\r\n')
				yield [x for x in lines if x != '']

				if 'GET' in buffer and 'Connection' in buffer:
					print("leaving readlines()...")
					break
				else:
					buffer = ''
			else:
				# Otherwise exit
				return
	return

# cria o socket com IPv4 (AF_INET) usando TCP (SOCK_STREAM)
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# vincula o socket com a porta (faz o "bind" do IP do servidor com a porta)
listen_socket.bind((HOST, PORT))

# "escuta" pedidos na porta do socket do servidor
listen_socket.listen(1)

# imprime que o servidor esta pronto para receber conexoes
print('Servidor HTTP aguardando conexoes na porta ' + str(PORT) + '...')

while True:
    # aguarda por novas conexoes
	client_connection, client_address = listen_socket.accept()
	while client_connection.fileno() != -1: # fileno() returns -1 for dead sockets
		# Default Server Connection Type
		connection_type = CONNECTION_TYPE_CLOSE
		# Default Server Response Status
		status = 0
		# Requested File Path
		file_path = None
		# Requested HTTP Method
		method = None
		# Request lines array
		request = []

		# Read each line until an empty line is entered
		for lines in readlines(client_connection):
			request += lines

		method_line = next((sub for sub in request if re.match(METHOD_REGEX, sub)), None)
		connection_line = next((sub for sub in request if re.match(CONNECTION_REGEX, sub)), None)
		
		print('request: ' + str(request))
		print('method_line: ' + str(method_line))
		print('connection_line: ' + str(connection_line))

		# If method_line was resolved
		if method_line:
			# Get the method, file path and http version as expected
			method, file_path, http_version = method_line.split(" ", 2)
			# In case connection_line was resolved
			if connection_line:
				# Split the string and check if it conforms with "Connection: (connection_type)"
				connection_specifier, connection_type = connection_line.split(" ", 1)
				if connection_specifier == 'Connection:' and connection_type == 'keep-alive':
					client_connection.settimeout(10)

			# Status previously set to 200 if method is GET or HEAD,
			# but can change to 404 depending on file_path value (see get_objects function)
			status = 200 if (method == 'GET' or method == 'HEAD') else 400

		# retrieve desired file, status and header text based on status and file_path
		http_file, status, header = get_objects(file_path, status)

		if http_file and header and status:
			if method == 'HEAD' and status == 200:
				# Time stamp from the file since last modification (last save)
				time_stamp = os.path.getctime(http_file.name)
				# Datetime object storing the date represented with time_stamp
				file_date = datetime.fromtimestamp(time_stamp)
				# Data attributes to be appended to http_response
				data = {
					'Date': file_date,
					'Server': SERVER_NAME,
					'Content-Length': opened_file_size(http_file),
					'Connection': connection_type,
					}

				# http_response  = header + data dictionary (string with format: "key: value\r\n") + "\r\n"
				http_response = header
				for key, value in data.items():
					http_response += str(key) + ": " + str(value) + "\r\n"
				http_response +=  "\r\n"
			else:
				# Default Response
				http_response = header + http_file.read() + "\r\n"
		else:
			http_response = ""

	    # Encode the generated http_response string
		response = bytes(http_response, encoding='utf-8')
		# Send the response to the client
		client_connection.send(response)

	    # Closes the connection if the desired connection type is 'close'
		if connection_type == CONNECTION_TYPE_CLOSE or connection_type != 'keep-alive':
			client_connection.close()


# encerra o socket do servidor
listen_socket.close()