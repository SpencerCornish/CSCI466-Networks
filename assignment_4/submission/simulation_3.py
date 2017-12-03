import network_3
import link_3
import threading
from time import sleep
import sys

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 5   #give the network_3 sufficient time to execute transfers

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads at the end

    #create network_3 hosts
    host_1 = network_3.Host('H1')
    object_L.append(host_1)
    host_2 = network_3.Host('H2')
    object_L.append(host_2)
    host_3 = network_3.Host('H3')
    object_L.append(host_3)

    #create routers and cost tables for reaching neighbors
    cost_D = {'H1': {0: 1}, 'RB': {1: 2}, 'RC': {2: 1}, 'H2': {3: 1}} # {neighbor: {interface: cost}}
    router_a = network_3.Router(name='RA',
                              cost_D = cost_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_a)

    cost_D = {'RA': {0: 1}, 'RD': {1: 1}} # {neighbor: {interface: cost}}
    router_b = network_3.Router(name='RB',
                              cost_D = cost_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_b)

    cost_D = {'RA': {0: 1}, 'RD': {1: 1}}
    router_c = network_3.Router(name='RC',
                                cost_D = cost_D,
                                max_queue_size=router_queue_size)
    object_L.append(router_c)

    cost_D = {'RB': {0: 2}, 'RC': {1: 4}, 'H3': {2: 1}}
    router_d = network_3.Router(name='RD',
                                cost_D=cost_D,
                                max_queue_size=router_queue_size)
    object_L.append(router_d)

    #create a Link Layer to keep track of link_3s between network_3 nodes
    link_layer = link_3.LinkLayer()
    object_L.append(link_layer)

    #add all the link_3s - need to reflect the connectivity in cost_D tables above
    link_layer.add_link(link_3.Link(host_1, 0, router_a, 0))
    link_layer.add_link(link_3.Link(host_2, 0, router_a, 1))

    # Router A's Outbound Connections
    link_layer.add_link(link_3.Link(router_a, 2, router_b, 0))
    link_layer.add_link(link_3.Link(router_a, 3, router_c, 0))

    # Router B's Outbound Connections
    link_layer.add_link(link_3.Link(router_b, 1, router_d, 0))

    # Router C's Outbound Connections
    link_layer.add_link(link_3.Link(router_c, 1, router_d, 1))

    # Router D's Outbound Connections
    link_layer.add_link(link_3.Link(router_d, 2, host_3, 0))






    #start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run))

    for t in thread_L:
        t.start()

    ## compute routing tables
    for i in range(len(router_a.intf_L)):
        router_a.send_routes(i) #one update starts the routing process
    sleep(simulation_time)  #let the tables converge
    print("Converged routing tables")
    for obj in object_L:
        if str(type(obj)) == "<class 'network_3.Router'>":
            obj.print_routes()

    #send packet from host 1 to host 2
    host_1.udt_send('H3', 'MESSAGE_FROM_H1')

    # Sleep for half of the sim time, to wait to send a reply
    sleep(simulation_time / 2)

    # send reply from host 2 to host 1
    host_3.udt_send('H1', 'REPLY_FROM_H3')

    sleep(simulation_time / 2)


    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")
