#
# Author: Kılıçarslan SIMSIKI
#


# """import subprocess
#  = subprocess.check_(("arp", "-a"))

# print(.decode("ascii"))"""


import json
# import tkinter
import customtkinter
# from Master_Modem_Odoo import MmoGui

def host_finder(target_ip: str, MmoGui) -> list[dict[str, str]]:
    """
    This function sends packages to each host in the network and fetches their ip and mac addresses

    Returns:
        returns a list of dictionaries of host info
    """
    from scapy.all import ARP, Ether, srp

    # XXX
    # print("\n" + "#"*15 + "\nSearching the network...\n" + "#"*15 + "\n")
    MmoGui.gui_console.configure(state='normal')
    MmoGui.gui_console.insert(customtkinter.END, "\n" + "#"*15 +
                  "\nAg taraniyor...\n" + "#"*15 + "\n")
    MmoGui.gui_console.configure(state='disabled')
    # XXX
    # target_ip = "192.168.5.0/24"
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
    # XXX
    # print("Found hosts!")
    MmoGui.gui_console.configure(state='normal')
    MmoGui.gui_console.insert(customtkinter.END, "Aygitlar bulundu!\n")
    MmoGui.gui_console.configure(state='disabled')
    # XXX

    return clients


def host_writer(fhfile: str, clients: list, MmoGui):
    """
    This function writes found list of dictionaries from the network scan result, into a json file

    Args:
        fhfile (file): found hosts file
        clients (list): result of network scan data
    """
    # print clients
    # XXX
    # print("Available devices in the network:")
    # print("IP" + " "*20+"MAC")
    MmoGui.gui_console.configure(state='normal')
    MmoGui.gui_console.insert(customtkinter.END, "Agdaki mevcut aygitlar:\n")
    MmoGui.gui_console.insert(customtkinter.END, "IP" + " "*20+"MAC\n")
    MmoGui.gui_console.configure(state='disabled')
    # XXX
    with open(fhfile, "w") as file:
        json.dump(clients, file, indent=5)

    for client in clients:
        # file.write(f"{client['ip']:16}    {client['mac']}\n")
        # XXX
        # print("{:16}      {}\n".format(client['ip'], client['mac']))
        MmoGui.gui_console.configure(state='normal')
        MmoGui.gui_console.insert(customtkinter.END, "{:16}      {}\n".format(
            client['ip'], client['mac']))
        MmoGui.gui_console.configure(state='disabled')
        # XXX

    MmoGui.gui_console.configure(state='normal')
    MmoGui.gui_console.insert(customtkinter.END, "Ag taramasi bitti.\n")
    MmoGui.gui_console.configure(state='disabled')


def host_analyzer(fhfile: str, mhfile: str, mac_filter: str) -> dict:
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
        host_list = json.loads(file.read())  # read the hosts file
        filtered_data = [d for d in host_list if d["mac"].find(
            mac_filter) == 0]  # find our specific mac
        with open(mhfile, "w") as file:
            # write the filtered data into modem hosts file
            json.dump(filtered_data, file, indent=5)
        with open(mhfile, "r") as file:
            # return the data from modem hosts file
            return json.loads(file.read())


def ip_retriever(filtered_hosts: dict):
    """This generator sends items values of elements with 'ip' keys to the caller.
    For performance purposes, it sends them one by one.

    Args:
        filtered_hosts (dict): _description_

    Yields:
        str: ip and mac values
    """
    for host in filtered_hosts:
        yield host['ip'], host['mac']
        # mac is for faulty mac that sometimes shows in modem's web interface.
        # this will make it possible to change it later when it's doing a read operation.
