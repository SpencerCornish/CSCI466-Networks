############ Imports
import httplib
import sys
import urllib



############ Fun text formatters
TITLE = "\033[1;34;47m"
IMPORTANT = "\033[1;33;40m"
FAILURE = "\033[1;31;40m"
SUCCESS = "\033[1;32;40m"
DEF_C = "\033[0;37;40m"
############ Globals


LOCAL_IP = "127.0.0.1"
# IP Address
ip = None
# Port
port = None

conn = None

############ Function Definitions
def main():
    setup()


# The Setup parses the IP and port and establishes a connection
def setup():
    print TITLE + '\n\n**********Battleship Client**********\n\n' + DEF_C


    if(len(sys.argv) != 5):
        print(FAILURE + 'incorrect number of arguments!' + DEF_C)
        sys.exit(1)
    ip = sys.argv[1]
    port = sys.argv[2]
    paramList = {'x': sys.argv[3], 'y' : sys.argv[4]}
    encodedUrl = '/?' + urllib.urlencode(paramList)
    print encodedUrl
    # if(xCord > BOARD_WIDTH || xCord < 0)
    #     print(FAILURE + 'X input must be in between 0 and ' + BOARD_WIDTH + DEF_C)
    #     sys.exit(1)
    # if(yCord > BOARD_WIDTH || xCord < 0)
    #     print(FAILURE + 'Y input must be in between 0 and' + BOARD_LENGTH +  DEF_C)
    #     sys.exit(1)


    print 'Attempting to estabish a connection to '+ encodedUrl
    conn = httplib.HTTPConnection(host=ip, port=port)
    conn.request("GET", encodedUrl)
    r = conn.getresponse()
    print(SUCCESS + r.read() + DEF_C)



############ Main
main()
