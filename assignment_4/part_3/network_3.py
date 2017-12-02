import json
import queue
import threading


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.in_queue = queue.Queue(maxsize)
        self.out_queue = queue.Queue(maxsize)

    ##get packet from the queue interface
    # @param in_or_out - use 'in' or 'out' interface
    def get(self, in_or_out):
        try:
            if in_or_out == 'in':
                pkt_S = self.in_queue.get(False)
                # if pkt_S is not None:
                #     print('getting packet from the IN queue')
                return pkt_S
            else:
                pkt_S = self.out_queue.get(False)
                # if pkt_S is not None:
                #     print('getting packet from the OUT queue')
                return pkt_S
        except queue.Empty:
            return None

    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param in_or_out - use 'in' or 'out' interface
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, in_or_out, block=False):
        if in_or_out == 'out':
            # print('putting packet in the OUT queue')
            self.out_queue.put(pkt, block)
        else:
            # print('putting packet in the IN queue')
            self.in_queue.put(pkt, block)


## Implements a network layer packet.
class NetworkPacket:
    ## packet encoding lengths
    dst_S_length = 5
    prot_S_length = 1

    ##@param dst: address of the destination host
    # @param data_S: packet payload
    # @param prot_S: upper layer protocol for the packet (data, or control)
    def __init__(self, dst, prot_S, data_S):
        self.dst = dst
        self.data_S = data_S
        self.prot_S = prot_S

    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()

    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst).zfill(self.dst_S_length)
        if self.prot_S == 'data':
            byte_S += '1'
        elif self.prot_S == 'control':
            byte_S += '2'
        else:
            raise('%s: unknown prot_S option: %s' %(self, self.prot_S))
        byte_S += self.data_S
        return byte_S

    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst = byte_S[0 : NetworkPacket.dst_S_length].strip('0')
        prot_S = byte_S[NetworkPacket.dst_S_length : NetworkPacket.dst_S_length + NetworkPacket.prot_S_length]
        if prot_S == '1':
            prot_S = 'data'
        elif prot_S == '2':
            prot_S = 'control'
        else:
            raise('%s: unknown prot_S field: %s' %(self, prot_S))
        data_S = byte_S[NetworkPacket.dst_S_length + NetworkPacket.prot_S_length : ]
        return self(dst, prot_S, data_S)




## Implements a network host for receiving and transmitting data
class Host:

    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.intf_L = [Interface()]
        self.stop = False #for thread termination

    ## called when printing the object
    def __str__(self):
        return self.addr

    ## create a packet and enqueue for transmission
    # @param dst: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst, data_S):
        p = NetworkPacket(dst, 'data', data_S)
        print('%s: sending packet' % (self))
        self.intf_L[0].put(p.to_byte_S(), 'out') #send packets always enqueued successfully

    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.intf_L[0].get('in')
        if pkt_S is not None:
            print('%s: received packet' % (self))

    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return



## Implements a multi-interface router
class Router:

    ##@param name: friendly router name for debugging
    # @param cost_D: cost table to neighbors {neighbor: {interface: cost}}
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, cost_D, max_queue_size):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.intf_L = [Interface(max_queue_size) for _ in range(len(cost_D))]
        #save neighbors and interfeces on which we connect to them
        self.cost_D = cost_D    # {neighbor: {interface: cost}}
        #TODO: set up the routing table for connected hosts
        self.rt_tbl_D = {dest:{self.name: cost for key,cost in cost_D[dest].items()} for dest in cost_D}
        self.rt_tbl_D[self.name] = {self.name: 0}
        print('%s: Initialized routing table' % self)
        self.print_routes()


    ## called when printing the object
    def __str__(self):
        return self.name

    def set_tables(self):
        self.rt_tbl_D[0] = self.cost_D.get('H1')

    ## look through the content of incoming interfaces and
    # process data and control packets
    def process_queues(self):
        for i in range(len(self.intf_L)):
            pkt_S = None
            #get packet from interface i
            pkt_S = self.intf_L[i].get('in')
            #if packet exists make a forwarding decision
            if pkt_S is not None:
                p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                if p.prot_S == 'data':
                    self.forward_packet(p,i)
                elif p.prot_S == 'control':
                    self.update_routes(p, i)
                else:
                    raise Exception('%s: Unknown packet type in packet %s' % (self, p))


    ## forward the packet according to the routing table
    #  @param p Packet to forward
    #  @param i Incoming interface number for packet p
    def forward_packet(self, p, i):
        try:
            final_destination = ''
            # Start the best cost very high, as to prevent issues later
            best_cost = 1000

            # Check if our packet_dest is not a neighbor
            if p.dst not in self.cost_D:
                router_list = []
                for key in self.cost_D:
                    if key.startswith("R"):
                        router_list.append(key)
                for router in router_list:
                    #  get the route cost from the routing table
                    route_cost = self.rt_tbl_D[router][self.name] + self.rt_tbl_D[p.dst][router]
                    if route_cost < best_cost:
                        best_cost = route_cost
                        final_destination = router
            else:
                # When ur neighbor is the final destination
                final_destination = p.dst
                print("neighbor is final destination")

            # Get the interface number
            output_interface = list(self.cost_D[final_destination].keys())[0]
            self.intf_L[output_interface].put(p.to_byte_S(), 'out', True)
            print('%s: forwarding packet from interface %d to %d' % \
                (self, i, output_interface))
        except queue.Full:
            print('%s: packet "%s" lost on interface %d' % (self, p, i))
            pass


    ## send out route update
    # @param i Interface number on which to send out a routing update
    def send_routes(self, i):
        #research showed json.dumps is a good serializer to use so we don't have to write our own
        routes = json.dumps(self.rt_tbl_D)
        packet_body = self.name + routes
        p = NetworkPacket(0, 'control', packet_body)
        try:
            print('%s: sending routing update from interface %d' % (self, i))
            self.intf_L[i].put(p.to_byte_S(), 'out', True)
        except queue.Full:
            print('%s: packet "%s" lost on interface %d' % (self, p, i))
            pass


    ## forward the packet according to the routing table
    #  @param p Packet containing routing information
    def update_routes(self, p, i):
        packet = str(p)
        source_start_len = NetworkPacket.prot_S_length + NetworkPacket.dst_S_length
        source_end_len = source_start_len + 2
        source_router = packet[source_start_len : source_end_len]
        vector = json.loads(packet[source_end_len:])

        #  Load up the aggregate list of keys
        keys = self.rt_tbl_D.keys() | vector.keys()

        router_list = []
        for key in keys:
            # Add Routers to the router_list
            if key.startswith("R"):
                router_list.append(key)
        for key in keys:
            if key not in vector:
                vector[key] = {source_router: 1000}

            if key not in self.rt_tbl_D:
                self.rt_tbl_D[key] = {self.name : 1000}

            self.rt_tbl_D[key][source_router] = vector[key][source_router]

        for dest_key in keys:
            for router in router_list:
                route_vector = self.rt_tbl_D[router]
                dest_vector = self.rt_tbl_D[dest_key]

                if router == dest_key:
                    continue

                if router not in dest_vector:
                    dest_vector[router] = 1000

                bellman_ford = route_vector[self.name] + dest_vector[router]
                if bellman_ford < dest_vector[self.name]:
                    dest_vector[self.name] = bellman_ford
                    for port in range(len(self.intf_L)):
                        self.send_routes(port)
        print('%s: Received routing update from interface %d' % (self, i))



    ## Print routing table
    def print_routes(self):

        # Print the current Router
        print('%s: sending packet' % (self))


        #  Print the headerline
        border=''
        for dest in self.rt_tbl_D.keys():
            border += '--------'
        print(border)
        # print the first row (Self, and destinations)
        des = "|" + self.name + "   |   "
        for dest in self.rt_tbl_D.keys():
            des += dest + " |   "
        print(des)

        selfcosts1 = ' |  ' + self.name + '   |    '
        body = ''
        for key in self.rt_tbl_D[self.name].keys():
            for _ in range(len(self.rt_tbl_D)+1):
                body += "------|"
            body += "\n|"

            body += key + "   |   "
            for _, v in self.rt_tbl_D.items():
                if key in v:
                    val = v[key]
                    if val == 1000:
                        val = 'X'
                body += str(val) + "  |   "
            body += '\n'
        print(body)
        print(border)


    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.process_queues()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return
