import http.client
import sys
import urllib.request, urllib.parse, urllib.error
#import urllib.parse
#from urllib import urllib.parse
import sys
import array
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
########Globals
#port parameter on which client can connect
port = None
#file w/ setup of your board
board = None

#number of hits each ship has recieved
chit = 0
bhit = 0
rhit = 0
shit = 0
dhit = 0
FAILURE = "\033[1;31;40m"
DEF_C = "\033[0;37;40m"
class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        boardFile = "Error"
        if(self.path == '/own_board.html'):
                boardFile = displayBoard('my_board.txt')
        if(self.path == '/opponent_board.html'):
                boardFile = displayBoard('enemy_board.txt')
        prettyFile = '<html><body><h1><pre>' + boardFile + '</pre></h1></body></html>'
        self.wfile.write(prettyFile.encode())

    def do_POST(self):
        global myBoard
        myBoard = []
        f = open(board, 'r')
        for line in f:
            myBoard.append(list(line))
        f.close()
        coor = urllib.parse.parse_qs(self.path)
        xCoord = int(coor['x'][0])
        yCoord = int(coor['y'][0])
        returnMessage = checkInput(xCoord, yCoord)
        with open(board, 'w') as file:
            for line in myBoard:
                file.write(''.join(line))
        self.send_response(returnMessage[0])
        self.send_header('Content-Type', 'text')
        self.end_headers()
        self.wfile.write(returnMessage[1].encode())

def checkInput(xCoord, yCoord):
    if (xCoord < 0 or xCoord > 9 or yCoord < 0 or yCoord > 9):
        return [404, "HTTP Not Found"]
    elif ((myBoard[yCoord][xCoord] == 'X') or (myBoard[yCoord][xCoord] == '.')):
        return [410, "HTTP Gone"]
    else:
        return checkBoard(xCoord, yCoord)


def checkBoard(x, y):
    global chit
    global bhit
    global rhit
    global shit
    global dhit
    cell = myBoard[y][x]
    if cell == 'C':
        chit = chit +1
        myBoard[y][x] = 'X'
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
        myBoard[y][x] = 'X'
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
        myBoard[y][x] = 'X'
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
        myBoard[y][x] = 'X'
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
        myBoard[y][x] = 'X'
        if dhit == 2:
            message = "hit=1&sink=D"
            code = 200
            #destroyer sunk
        else:
            message = "hit=1"
            code = 200
            #destroyer hit
    else:
        myBoard[y][x] = '.'
        message = "hit=0"
        code = 200
    return [code, message]
        #missed

def displayBoard(which_board):
    boardFile = open(which_board, 'r')
    message = boardFile.read()
    return message

if __name__ == '__main__':
    if(len(sys.argv) != 3):
        print((FAILURE + 'incorrect number of arguments!' + DEF_C))
        sys.exit(1)
    port = sys.argv[1]
    board = sys.argv[2]
    server = HTTPServer(('', int(port)), Server)
    server.serve_forever()
