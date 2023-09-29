#  coding: utf-8 
import socketserver
import os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        
        # decode the data we got and put it into a list
        decoded_request_list = self.data.decode('utf-8').split('\n')
        
        method_path_list = decoded_request_list[0].strip().split()
        
        if len(method_path_list) < 2: # requests should have at least 2 elements if it dosent it means its a bad request so return
            return
        
        method = method_path_list[0] # type of request [GET, POST, ect]
        path = method_path_list[1] # path that is requested
        
        # this will prevent weird paths that are not allowed such as /../../../../../../../../../../../../etc/group
        if ".." in path:
            response = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n404 Not Found"
            self.request.sendall(response.encode())
            return
        
        # Only method allowed is GET so if anything else send status code of 405
        if method != 'GET':
            # Return a 405 Method Not Allowed response
            response = "HTTP/1.1 405 Method Not Allowed\r\nConnection: close\r\n\r\n405 Method Not Allowed"
            self.request.sendall(response.encode())
            return
        
        try:
            # dealing with different paths and fixing them
            if path == '/':
                response = "HTTP/1.1 301 Moved Permanently\r\nLocation: /index.html\r\n\r\n"
                self.request.sendall(response.encode())
                path = '/index.html'  
            elif ('.html' in path or '.css' in path) and path.endswith('/'): # paths that are '.html' or '.css' should not end in '/'
                path = path[:-1]
                response = f"HTTP/1.1 301 Moved Permanently\r\nLocation: {path}\r\n\r\n"
                self.request.sendall(response.encode())
            elif not ('.html' in path or '.css' in path) and path.endswith('/'): # paths that are not '.html' or '.css' should go to /index.html
                path = path + 'index.html'
                response = f"HTTP/1.1 301 Moved Permanently\r\nLocation: {path}\r\n\r\n"
            elif not path.endswith('/') and not ('.html' in path or '.css' in path): # paths that are not '.html' or '.css' should end in '/' and should go to /index.html
                path = path + '/'
                response = f"HTTP/1.1 301 Moved Permanently\r\nLocation: {path}\r\n\r\n"
                self.request.sendall(response.encode())        
                path = path + 'index.html'       

            # read the file
            with open('./www' + path, 'rb') as file:
                response_data = file.read()
                file.close()
               
            # Before sending the HTTP response we need to figure out the mimetype
            if path.endswith('.html'):
                content_type = 'text/html'
            elif path.endswith('.css'):
                content_type = 'text/css'
                
            # Send HTTP response with the file data
            response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(response_data)}\r\nContent-Type: {content_type}\r\nConnection: close\r\n\r\n".encode() + response_data
            self.request.sendall(response)
        except FileNotFoundError:
            # Handle 404 Not Found
            response = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n404 Not Found"
            self.request.sendall(response.encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
