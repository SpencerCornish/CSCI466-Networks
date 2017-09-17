import http.server
import BaseHTTPRequestHandler
import HTTPServer
import sys
import array

class server(BaseHTTPRequestHandler):
########Globals
#port parameter on which client can connect
port = None
#file w/ setup of your board
file = None
#x and y coordinates of hit
x = None
y = None
#message to client whether it was a hit or miss

#number of hits each ship has recieved
chit = 0
bhit = 0
rhit = 0
shit = 0
dhit = 0

#text file


def main():

    run()
#when fire: send message to other server, get response back, update own board based on that info

def headers(self, code):
    self.send_response(code)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

def do_GET(self, code):
    self.headers(code)
    self.wfile.write(bytes(file, "utf8"))

def do_POST(self, message, code):
    self.headers(code)
    self.wfile.write(message)

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

def checkInput(x, y):
    if x < 0 || x > 9 || y < 0 || y > 9:
        do_Post("", 404)



def checkBoard():
    f = open(file, 'r')
    row = file.readline(x-1)
    cell = row[y-1]
    if cell == 'C':
        chit++
        if chit == 5:
            do_Post("hit=1&sink=C", 200)
            #carrier sunk
        else:
            do_Post("hit=1", 200)
            #carrier hit
    else if cell == 'B':
        bhit++
        if bhit == 4:
            do_Post("hit=1&sink=B", 200)
            #battleship sunk
        else:
            do_Post("hit=1", 200)
            #battleship hit
    else if cell == 'R':
        rhit++
        if rhit == 3:
            do_Post("hit=1&sink=R", 200)
            #cruiser sunk
        else:
            do_Post("hit=1", 200)
            #cruiser hit
    else if cell == 'S':
        shit++
        if shit == 3:
            do_Post("hit=1&sink=S", 200)
            #sub sunk
        else:
            do_Post("hit=1", 200)
            #sub hit
    else if cell == 'D':
        dhit++
        if dhit == 2:
            do_Post("hit=1&sink=D", 200)
            #destroyer sunk
        else:
            do_Post("hit=1", 200)
            #destroyer hit
    else:
        do_Post("hit=0", 200)
        #missed
