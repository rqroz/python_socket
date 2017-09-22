BASE_FILE_PATH = "files_container" # Base path for files
INDEX_PATH = "/index.html" # Index subpath file

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
		http_file_path = INDEX_PATH if (path == '/' or path == '/index.html') else path
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