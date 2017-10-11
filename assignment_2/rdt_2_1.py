import network_2_1
import argparse
from time import sleep
import hashlib
import time


class Packet:
    ## the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10
    ## length of md5 checksum in hex
    checksum_length = 32

    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S

    @classmethod
    def from_byte_S(self, byte_S):
        if Packet.corrupt(byte_S):
            raise RuntimeError('Cannot initialize Packet: byte_S is corrupt')
        #extract the fields
        seq_num = int(byte_S[Packet.length_S_length : Packet.length_S_length+Packet.seq_num_S_length])
        msg_S = byte_S[Packet.length_S_length+Packet.seq_num_S_length+Packet.checksum_length :]
        return self(seq_num, msg_S)


    def get_byte_S(self):
        #convert sequence number of a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        #convert length to a byte field of length_S_length bytes
        length_S = str(self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S)).zfill(self.length_S_length)
        #compute the checksum
        checksum = hashlib.md5((length_S+seq_num_S+self.msg_S).encode('utf-8'))
        checksum_S = checksum.hexdigest()
        #compile into a string
        return length_S + seq_num_S + checksum_S + self.msg_S


    @staticmethod
    def corrupt(byte_S):
        #extract the fields
        length_S = byte_S[0:Packet.length_S_length]
        seq_num_S = byte_S[Packet.length_S_length : Packet.seq_num_S_length+Packet.seq_num_S_length]
        checksum_S = byte_S[Packet.seq_num_S_length+Packet.seq_num_S_length : Packet.seq_num_S_length+Packet.length_S_length+Packet.checksum_length]
        msg_S = byte_S[Packet.seq_num_S_length+Packet.seq_num_S_length+Packet.checksum_length :]

        #compute the checksum locally
        checksum = hashlib.md5(str(length_S+seq_num_S+msg_S).encode('utf-8'))
        computed_checksum_S = checksum.hexdigest()
        #and check if the same
        return checksum_S != computed_checksum_S


class RDT:
    ## latest sequence number used in a packet
    seq_num = 1
    ## buffer of bytes read from network
    byte_buffer = ''

    def __init__(self, role_S, server_S, port):
        self.network = network_2_1.NetworkLayer(role_S, server_S, port)

    def disconnect(self):
        self.network.disconnect()

    def rdt_1_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S())

    def rdt_1_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S
        #keep extracting packets - if reordered, could get more than one
        while True:
            #check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                return ret_S #not enough bytes to read packet length
            #extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S #not enough bytes to read the whole packet
            #create packet from buffer content and add to return string
            p = Packet.from_byte_S(self.byte_buffer[0:length])
            ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
            #remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            #if this was the last packet, will return on the next iteration


    def rdt_2_1_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        #while seq_num has not increased
        while True:
            self.network.udt_send(p.get_byte_S())
            #response from reciever
            rmessage = ''
            #while the response is nothing
            while True:
                rmessage = self.network.udt_receive()
                if(rmessage != ''):
                    break;
            #find length of the rmessage we recieved
            mlength = int(rmessage[:Packet.length_S_length])
            #find byte buffer by going from the length of the message to the end of the packet
            self.byte_buffer = rmessage[mlength:]
            #if packet is corrupt, set buffer to ''
            if Packet.corrupt(rmessage[:mlength]):
                self.byte_buffer = ''
            #if packet is not corrupt
            if not Packet.corrupt(rmessage[:mlength]):
                #turn bytes into the packet and store in array
                packet = Packet.from_byte_S(rmessage[:mlength])
                #check to see if packet's sequence number is behind, send ACK packet if behind
                if packet.seq_num < self.seq_num:
                    ackpacket = Packet(packet.seq_num, "1")
                    self.network.udt_send(ackpacket.get_byte_S())
                #check if its an ACK packet. Add to sequence num if it is
                elif packet.msg_S == "1":
                    self.seq_num +=1
                    break;
                #check if its a NAK packet.
                elif packet.msg_S == "0":
                    self.byte_buffer = ''

    def rdt_2_1_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer = self.byte_buffer + byte_S

        while True:
            # check if we have received enough bytes
            if len(self.byte_buffer) < Packet.length_S_length:
                break  # not enough bytes to read packet length

            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                break  # not enough bytes to read the whole packet

            # Check for corrupt packet
            if Packet.corrupt(self.byte_buffer):
                resp = Packet(self.seq_num, "0")
                self.network.udt_send(resp.get_byte_S())
            else:

                # Cache the packet
                packet = Packet.from_byte_S(self.byte_buffer[0:length])

                # Check for ACK or NACK
                if (packet.msg_S == '0' or packet.msg_S == '1'):
                    self.byte_buffer = self.byte_buffer[length:]
                    continue

                # Check for desynced packet
                if packet.seq_num < self.seq_num:
                    resp = Packet(packet.seq_num, "1")
                    self.network.udt_send(resp.get_byte_S())

                # If all is good
                elif packet.seq_num == self.seq_num:
                    resp = Packet(packet.seq_num, "1")
                    self.network.udt_send(resp.get_byte_S())
                    self.seq_num = self.seq_num + 1
                # For if the packet number is greater than ours, really shouldn't happen
                else:
                    print("Unexpected error!")

                # Null checker for ret_S
                if ret_S is None:
                    ret_S = packet.msg_S
                else:
                    ret_S = ret_S + packet.msg_S

            # Purge the buffer
            self.byte_buffer = self.byte_buffer[length:]

        return ret_S

    def rdt_3_0_send(self, msg_S):
        #current time
        t = None;
        p = Packet(self.seq_num, msg_S)
        while True:
            self.network.udt_send(p.get_byte_S())
            rmessage = ''
            #get current time
            t = time.time()
            while True:
                #timeout if waiting more than 4 seconds
                if(time.time() < (5 + t)):
                    break;
                rmessage = self.network.udt_receive()
                #if response is not empty
                if(rmessage != ''):
                    break;
                #find length of the rmessage we recieved
                mlength = int(rmessage[:Packet.length_S_length])
                #find byte buffer by going from the length of the message to the end of the packet
                self.byte_buffer = rmessage[mlength:]
                #if packet is corrupt, set buffer to ''
                if Packet.corrupt(rmessage[:mlength]):
                    self.byte_buffer = ''
                #if packet is not corrupt
                if not Packet.corrupt(rmessage[:mlength]):
                    #turn bytes into the packet and store in array
                    packet = Packet.from_byte_S(rmessage[:mlength])
                    #check to see if packet's sequence number is behind, send ACK packet if behind
                    if packet.seq_num < self.seq_num:
                        ackpacket = Packet(packet.seq_num, "1")
                        self.network.udt_send(ackpacket.get_byte_S())
                    #check if its an ACK packet. Add to sequence num if it is
                    elif packet.msg_S == "1":
                        self.seq_num +=1
                        break;
                    #check if its a NAK packet.
                    elif packet.msg_S == "0":
                        self.byte_buffer = ''

    def rdt_3_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer = self.byte_buffer + byte_S

        while True:
            # check if we have received enough bytes
            if len(self.byte_buffer) < Packet.length_S_length:
                break  # not enough bytes to read packet length

            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                break  # not enough bytes to read the whole packet

            # Check for corrupt packet
            if Packet.corrupt(self.byte_buffer):
                resp = Packet(self.seq_num, "0")
                self.network.udt_send(resp.get_byte_S())
            else:

                # Cache the packet
                packet = Packet.from_byte_S(self.byte_buffer[0:length])

                # Check for ACK or NACK
                if (packet.msg_S == '0' or packet.msg_S == '1'):
                    self.byte_buffer = self.byte_buffer[length:]
                    continue

                # Check for desynced packet
                if packet.seq_num < self.seq_num:
                    resp = Packet(packet.seq_num, "1")
                    self.network.udt_send(resp.get_byte_S())

                # If all is good
                elif packet.seq_num == self.seq_num:
                    resp = Packet(packet.seq_num, "1")
                    self.network.udt_send(resp.get_byte_S())
                    self.seq_num = self.seq_num + 1
                # For if the packet number is greater than ours, really shouldn't happen
                else:
                    print("Unexpected error!")

                # Null checker for ret_S
                if ret_S is None:
                    ret_S = packet.msg_S
                else:
                    ret_S = ret_S + packet.msg_S

            # Purge the buffer
            self.byte_buffer = self.byte_buffer[length:]

        return ret_S


if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description='RDT implementation.')
    parser.add_argument('role', help='Role is either client or server.', choices=['client', 'server'])
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    rdt = RDT(args.role, args.server, args.port)
    if args.role == 'client':
        rdt.rdt_2_1_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_2_1_receive())
        rdt.disconnect()


    else:
        sleep(1)
        print(rdt.rdt_2_1_receive())
        rdt.rdt_2_1_send('MSG_FROM_SERVER')
        rdt.disconnect()
