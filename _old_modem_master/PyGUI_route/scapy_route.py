
"""import subprocess
output = subprocess.check_output(("arp", "-a"))

print(output.decode("ascii"))"""

import json

def host_finder(target_ip, output):
    """
    This function sends packages to each host in the network and fetches their ip and mac addresses

    Returns:
        returns a list of dictionaries of host info
    """
    from scapy.all import ARP, Ether, srp

    ############################# XXX
    output.print("\n" + "#"*15 + "\nSearching the network...\n" + "#"*15 + "\n")
    ############################# XXX

    #target_ip = "192.168.5.0/24"
    # IP Address for the destination
    # create ARP packet
    arp = ARP(pdst=target_ip)
    # create the Ether broadcast packet
    # ff:ff:ff:ff:ff:ff MAC address indicates broadcasting
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    # stack them
    packet = ether/arp

    result = srp(packet, timeout=3, verbose=0)[0]

    # a list of clients, we will fill this in the upcoming loop
    clients = []

    for sent, received in result:
        # for each response, append ip and mac address to `clients` list
        clients.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    ############################# XXX
    output.print("Found hosts!")    
    ############################# XXX
    
    return clients


def host_writer(fhfile, clients, output):
    """
    This function writes found list of dictionaries from the network scan result, into a json file

    Args:
        fhfile (file): found hosts file
        clients (list): result of network scan data
    """

    # print clients
    ############################# XXX
    output.print("Available devices in the network:")
    output.print("IP" + " "*22+"MAC")
    ############################# XXX
    
    with open(fhfile, "w") as file:
        json.dump(clients, file, indent=5)       
               
    for client in clients:
        #file.write(f"{client['ip']:16}    {client['mac']}\n")
        ############################# XXX
        output.print("{:16}      {}\n".format(client['ip'], client['mac']))
        ############################# XXX
 
def host_analyzer(fhfile, mhfile, mac_filter):
    """
    This function takes a found hosts file and fetches only necessary mac addresses, then dumps them
    into another file.

    Args:
        fhfile (file): found hosts file
        mhfile (file): modem hosts file

    Returns:
        list: list of dictionaries fetched from the modem hosts file
    """
    
    with open(fhfile) as file:
        host_list = json.loads(file.read()) #read the hosts file
        
        filtered_data = [d for d in host_list if d["mac"].find(mac_filter) == 0] #find our specific mac
        
        with open(mhfile, "w") as file:
            json.dump(filtered_data, file, indent=5) # write the filtered data into modem hosts file
            
        with open(mhfile, "r") as file:
            return json.loads(file.read())   # return the data from modem hosts file

def ip_retriever(filtered_hosts):
    for host in filtered_hosts:
        yield host['ip']