############ Imports
import httplib




############ Globals

# IP Address
ip = None
# Port
port = None

conn = None

############ Function Definitions
def main():
    setup()

# The Setup prompts for IP/Port and establishes a connection
def setup():
    print("~~~~~~~~~~~~")
    print("~~~Client~~~")
    print("~~~~~~~~~~~~")
    print("~~~~~~~~~~~~")
    print("~~~~~~~~~~~~")
    ip = raw_input("IP: ")
    port = input("Port: ")
    conn = httplib.HTTPConnection(host=ip, port=port)
    conn.request("GET", "/index.html")
    r = conn.getresponse()

    print(r.read())

############ Main
main()
