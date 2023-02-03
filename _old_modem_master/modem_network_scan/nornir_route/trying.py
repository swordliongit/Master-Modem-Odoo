# Import Python library
import networkscan
from nornir_route import main  
# def write_file(self, file_type=0, filename="inventory/hosts.yaml"):
#     """ Method to write a file with the list of the detected hosts """
        
        
    # Input:
    #
    # - file_type (integer, optional): 0, Nornir file (default value)
    #                                  1, Text file as output file
    # - filename (string, optional): the name of the file to be written ("hosts.yaml"
    #   is the default value)
    #
    # Ouput:
    # A text file with the list of detected hosts ("hosts.yaml" is the default value)
    # return 0 if no error occured
#!/usr/bin/env python3

# Main function
if __name__ == '__main__':

    # Define the network to scan
    my_network = "192.168.5.0/24"

    # Create the object
    my_scan = networkscan.Networkscan(my_network)

    # Display information
    print("Network to scan: " + str(my_scan.network))
    print("Prefix to scan: " + str(my_scan.network.prefixlen))
    print("Number of hosts to scan: " + str(my_scan.nbr_host))

    # Run the network scan
    print("Scanning hosts...")

    # Run the scan of hosts using pings
    my_scan.run()

    # Display information
    print("List of hosts found:")

    # Display the IP address of all the hosts found
    for i in my_scan.list_of_hosts_found:
        print(i)

    # Display information
    print("Number of hosts found: " + str(my_scan.nbr_host_found))

    # Write the file on disk
    res = my_scan.write_file()

    # Error while writting the file?
    if res:
        # Yes
        print("Write error with file " + my_scan.filename)

    else:
        # No error
        print("Data saved into file " + my_scan.filename)

    main()