# python_socket

### Methods accepted: 
* HEAD
* GET
### Headers processed: 
* Connection
### Connection types: 
* 'close'
* 'keep-alive'

### Example
#### Terminal (Starting server):
```
$ telnet localhost 8080
```

#### Telnet (with server running): 
* GET example with keep-alive connection type  
  Request:  
  ```
    >> GET / HTTP/1.1
    >> Connection: keep-alive
  ```
  Expected Response:  
  ```
    HTTP/1.1 200 OK 

    <html>
      <head>
        <meta charset="utf-8">
        <title>CONNET</title>
      </head>
      <body>
        <section id="sobre" class="bg-light-gray">
          main page
      </body>
    </html>
  ```
  The connection will be opened and accepting other requests for SERVER_CONN_TIMEOUT seconds.  
  The client_connection's timeout will be reset to SERVER_CONN_TIMEOUT at each request if the Connection header is sent. Otherwise it will default to 'close'.    

* HEAD example with default (close) connection type

  ![alt HEAD](request_samples/HEAD_Example.png)
