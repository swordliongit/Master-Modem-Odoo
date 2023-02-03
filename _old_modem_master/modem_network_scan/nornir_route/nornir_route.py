from nornir import InitNornir
from nornir_utils.plugins.functions import print_title, print_result
from nornir_napalm.plugins.tasks import napalm_get


# Main function
def main():

    # Create a Nornir object
    nr = InitNornir(config_file="config.yaml")

    # Run Nornir task (here getting the ARP table of the devices)
    result = nr.run(task=napalm_get,name=" ARP table ", getters=["arp_table"])

    # Display the result
    print_title("Display ARP table of the network devices")
    print_result(result)
