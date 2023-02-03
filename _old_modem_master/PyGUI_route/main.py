from scapy_route import host_finder, host_writer, host_analyzer, ip_retriever
from utility import create_directory
from mission import modem_login_init, modem_login
import threading

def main(output):
    
    fhfile = "hosts/found_hosts.json" # found hosts file
    mhfile = "hosts/modem_hosts.json" # modem hosts file   
    
    # information retrieval - pre operation phase
    import os
    if os.stat("info.txt").st_size != 0:
        with open("info.txt") as file:
            target_ip = file.readline().split('=')[1].strip('\n')   # ip range to scan
            mac_filter = file.readline().split('=')[1].strip('\n')  # mac filter to fetch
    else:
        with open("info.txt", 'w') as file:
            file.writelines("target=192.168.5.0/24")
            file.writelines("mac_filter=1c:18:4a")

    # start of main operation
    ########################
    
    create_directory("./hosts/") #create our directory for our host files

    hosts = host_finder(target_ip, output) # network scan

    host_writer(fhfile, hosts, output) # write found hosts into fhfile

    needed_hosts = host_analyzer(fhfile, mhfile, mac_filter) # filter found hosts based on 1c:18:4a mac and return a list of them
    
    ########################
    # host operation finished, time to log into many modem interfaces at the same time

    driver = modem_login_init() #initialize the chrome driver

    ip_list = []
    for ip in ip_retriever(needed_hosts): # yield ips of the filtered hosts one by one
        ip_list.append(ip)

    threads = []
    
    for ip in ip_list: # call multiple versions of the function simultaneously
        t = threading.Thread(target=modem_login, args=(driver, ip, output))
        threads.append(t)
        t.start()
        
    for t in threads: # wait for all threads to finish
        t.join()
