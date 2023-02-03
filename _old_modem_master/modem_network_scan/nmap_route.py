import nmap


"""target_mac = '<Enter MAC Adress>'

nm = nmap.PortScanner()

nm.scan(hosts='192.168.117.0/24', arguments='-PR')

host_list = nm.all_hosts()

print(host_list)"""


        
nm = nmap.PortScanner()
nm.scan(hosts='192.168.117.0/24', arguments='-sN')
for ip in nm.all_hosts():
    host = nm[ip]
    mac = "-"
    vendorName = "-"
    if 'mac' in host['addresses']:
        mac = host['addresses']['mac']
        if mac in host['vendor']:
            vendorName = host['vendor'][mac]

    status = host['status']['state']
    rHost = {'ip': ip, 'mac': mac, 'vendor': vendorName, 'status': status}
    print(rHost)