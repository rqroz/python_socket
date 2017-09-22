import os
import socket
import re
from funcs import *
from datetime import datetime

# DEFAULT VALUES
HOST = '' # Server IP
PORT = 8080 # Server Port
SERVER_CONN_TIMEOUT = 10 # Server connection timeout for clients
SERVER_NAME = 'CONNET' # Server Name 
CONNECTION_TYPE_CLOSE = 'close' # Connection Type for closing connection
METHOD_REGEX = '([A-Z]{3,4} (\/)?(\w{0,})(.html)? HTTP\/1.1)'
CONNECTION_REGEX = '(Connection: [a-z]+-?[a-z]+)'

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
					client_connection.settimeout(SERVER_CONN_TIMEOUT)

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