#  coding: utf-8 
import socketserver
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
        print("PATHJ: ", path)
        
        # Only method allowed is GET so if anything else send status code of 405
        if method != "GET":
            self.send_reply(405, "Method Not Allowed")
            return
        
        # we will be serving files from the www folder
        folder = "./www"
        
        folder_path = folder + path
        
        # handle non existing paths here (404)
        
        
        # read the file
        print("HERE", folder_path)
        with open(folder_path, 'rb') as f:
            content = f.read()
        
        # send response to client   
        self.send_reply(200, "OK", content)

    def send_reply(self, status_code, status_text, content=None):
        response = "HTTP/1.1 {} {}\r\n".format(status_code, status_text)
        self.request.sendall(response.encode('utf-8'))
        if content:
            self.request.sendall(content)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
