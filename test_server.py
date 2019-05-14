
import http.server
import ssl
import socket
import json
import copy
import urllib.parse

import gobattlesim.application


app = gobattlesim.application.GoBattleSimApp()
app.bind_game_master("data/GAME_MASTER.json")



class MyRequestHandler(http.server.SimpleHTTPRequestHandler):


    def do_POST(self):
        length = int(self.headers['content-length'])        
        data_string = self.rfile.read(length)
        client_req = json.loads(data_string.decode())

        resp_json = app.handle_request(client_req)

        try:
            resp_json = app.handle_request(client_req)
            self.send_response(200)
        except Exception as e:
            print(str(e))
            resp_json = {
                "errorMessage": str(e)
            }
            self.send_response(400)
            
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.flush_headers()
        
        self.wfile.write(json.dumps(resp_json).encode())
        

def start():
    
    HOST, PORT = '127.0.0.1', 5000

    server = http.server.HTTPServer((HOST, PORT), MyRequestHandler)
    #server.socket = ssl.wrap_socket(server.socket, certfile='./server.pem', server_side=True)
    server.serve_forever()



if __name__ == "__main__":
    start()



    
