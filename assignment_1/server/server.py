import httplib
import sys
import urllib
import sys
import array
import socket
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
########Globals
#port parameter on which client can connect
port = None
#file w/ setup of your board
board = None
oboard = None
#x and y coordinates of hit
x = None
y = None
#message to client whether it was a hit or miss
code = None
message = None
#number of hits each ship has recieved
chit = 0
bhit = 0
rhit = 0
shit = 0
dhit = 0
FAILURE = "\033[1;31;40m"
DEF_C = "\033[0;37;40m"
class Server(BaseHTTPRequestHandler):

    #when fire: send message to other server, get response back, update own board based on that info

    def headers(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self, code):
        self.headers(code)
        self.wfile.write(bytes(board, "utf8"))

    def do_POST(self, message, code):
        coor = urllib.parse.parse_qs(self.path)
        x = coor[0]
        y = coor[1]
        checkInput(x, y)
        self.headers(code)
        self.wfile.write(message.encode())

    def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()

    def checkInput(x, y):
        if x < 0 | x > 9 | y < 0 | y > 9:
            message = "HTTP Not Found"
            code = 404
            return message, code
        elif oboard[x-1][y-1] == 'X' | oboard[x-1][y-1] == '.':
            message = "HTTP Gone"
            code = 410
            return message, code
        else:
            checkBoard()

    def checkBoard():
        cell = oboard[x-1][y-1]
        if cell == 'C':
            chit = chit +1
            oboard[x-1][y-1] = 'X'
            if chit == 5:
                message = "hit=1&sink=C"
                code = 200
                #carrier sunk
            else:
                message = "hit=1"
                code = 200
                #carrier hit
        elif cell == 'B':
            bhit = bhit +1
            oboard[x-1][y-1] = 'X'
            if bhit == 4:
                message = "hit=1&sink=B"
                code = 200
                #battleship sunk
            else:
                message = "hit=1"
                code = 200
                #battleship hit
        elif cell == 'R':
            rhit = rhit +1
            oboard[x-1][y-1] = 'X'
            if rhit == 3:
                message = "hit=1&sink=R"
                code = 200
                #cruiser sunk
            else:
                message = "hit=1"
                code = 200
                #cruiser hit
        elif cell == 'S':
            shit = shit +1
            oboard[x-1][y-1] = 'X'
            if shit == 3:
                message = "hit=1&sink=S"
                code = 200
                #sub sunk
            else:
                message = "hit=1"
                code = 200
                #sub hit
        elif cell == 'D':
            dhit = dhit +1
            oboard[x-1][y-1] = 'X'
            if dhit == 2:
                message = "hit=1&sink=D"
                code = 200
                #destroyer sunk
            else:
                message = "hit=1"
                code = 200
                #destroyer hit
        else:
            oboard[x-1][y-1] = '.'
            message = "hit=0"
            code = 200
        return message, code
            #missed

    def show_board(which_board):
        g = open(which_board, 'r')
        b = g.read()
        message = b
        return message

    if __name__ == '__main__':
        if(len(sys.argv) != 3):
            print(FAILURE + 'incorrect number of arguments!' + DEF_C)
            sys.exit(1)
        port = sys.argv[1]
        board = sys.argv[2]
        oboard = []
        f = open(board, 'r')
        for line in f:
            oboard.append(list(line))
        run(port)
