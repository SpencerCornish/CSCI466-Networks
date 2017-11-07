'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import network_3
import link_3
import threading
from time import sleep

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 5 #give the network sufficient time to transfer all packets before quitting
fwdA = {1:2, 2:3}
fwdB = {1:1}
fwdC = {2:1}
fwdD = {1:2, 2:3}
if __name__ == '__main__':
    object_L = [] # keeps track of objects, so we can kill their threads

    # create network nodes
    client_1 = network_3.Host(1)
    object_L.append(client_1)

    client_2 = network_3.Host(2)
    object_L.append(client_2)

    server_1 = network_3.Host(3)
    object_L.append(server_1)

    server_2 = network_3.Host(4)
    object_L.append(server_2)

    router_a = network_3.Router(name='A', intf_count=4, max_queue_size=router_queue_size, forwarding_table=fwdA)
    router_b = network_3.Router(name='B', intf_count=2, max_queue_size=router_queue_size, forwarding_table=fwdB)
    router_c = network_3.Router(name='C', intf_count=2, max_queue_size=router_queue_size, forwarding_table=fwdC)
    router_d = network_3.Router(name='D', intf_count=4, max_queue_size=router_queue_size, forwarding_table=fwdD)

    object_L.append(router_a)
    object_L.append(router_b)
    object_L.append(router_c)
    object_L.append(router_d)

    # Create a Link Layer to keep track of links between network nodes
    link_layer = link_3.LinkLayer()
    object_L.append(link_layer)

    # Links for client 1-2
    link_layer.add_link(link_3.Link(client_1, 0, router_a, 0, 50))
    link_layer.add_link(link_3.Link(client_2, 0, router_a, 1, 50))

    # Links for Router A
    link_layer.add_link(link_3.Link(router_a, 2, router_b, 0, 50))
    link_layer.add_link(link_3.Link(router_a, 3, router_c, 0, 50))

    # Links for Router B
    link_layer.add_link(link_3.Link(router_b, 1, router_d, 0, 50))

    # Links for Router C
    link_layer.add_link(link_3.Link(router_c, 1, router_d, 1, 50))

    # Links for Router D
    link_layer.add_link(link_3.Link(router_d, 2, server_1, 0, 50))
    link_layer.add_link(link_3.Link(router_d, 3, server_2, 0, 50))


    #start all the objects
    thread_L = []

    # Start client 1-2
    thread_L.append(threading.Thread(name=client_1.__str__(), target=client_1.run))
    thread_L.append(threading.Thread(name=client_2.__str__(), target=client_2.run))

    # Start Routers
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    thread_L.append(threading.Thread(name=router_b.__str__(), target=router_b.run))
    thread_L.append(threading.Thread(name=router_c.__str__(), target=router_c.run))
    thread_L.append(threading.Thread(name=router_d.__str__(), target=router_d.run))

    # Start Servers
    thread_L.append(threading.Thread(name=server_1.__str__(), target=server_1.run))
    thread_L.append(threading.Thread(name=server_2.__str__(), target=server_2.run))

    # Start Link Layer
    thread_L.append(threading.Thread(name="Network", target=link_layer.run))

    for t in thread_L:
        t.start()


    #create some send events
    for i in range(1):
        client_1.udt_send(3, 'Turmoil has engulfed the Galactic Republic. The taxation of trade routes to .... %d' % i)



    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")



# writes to host periodically
