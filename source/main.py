#
# Author: Kılıçarslan SIMSIKI
#


from scapy_route import host_finder, host_writer, host_analyzer, ip_retriever
from utility import create_directory
from interface_operation import operation_controller, interface_operation_modify_compare
from http_request import odoo_login, send_datato_odoo, fetch_datafrom_odoo
import threading
from threading import Semaphore
from queue import Queue
from WaitGroup import WaitGroup
# import PySimpleGUI as sg # left this gui method due to its incapability in multithreaded environment


import tkinter  # capable of multithreaded work


# global because network scan writes into this and modem read reads from this separately.
needed_hosts = {}
# global because modem read fills it and modem configure consumes it separately.
modify_queue = Queue()


def network_scan(output, target_ip, fhfile="./hosts/found_hosts.json", mhfile="./hosts/modem_hosts.json"):
    """Controls scapy_route network scanning functions.

    Args:
        output (_type_): tkinter.Text console to pass into scapy_route functions for printing into GUI console.
        target_ip (str): ip interval to scan that's passed from the button function.
        fhfile (str, optional): found_hosts file that contains all the devices in the network. Defaults to "./hosts/found_hosts.json".
        mhfile (str, optional): modem_hosts file that contains all the devices that has a specific mac address. Defaults to "./hosts/modem_hosts.json".

    """
    mac_filter = ""
    # information retrieval - pre operation phase
    import os

    if os.stat("Python/modem_master_odoo/support/info.txt").st_size != 0:
        with open("Python/modem_master_odoo/support/info.txt") as file:
            # target_ip = file.readline().split('=')[1].strip('\n')   # ip range to scan
            mac_filter = file.readline().split('=')[1].strip('\n')  # mac filter to fetch
    else:
        with open("Python/modem_master_odoo/support/info.txt", 'w') as file:
            # Python/modem_master_odoo/support/info.txt
            # file.writelines("target=192.168.5.0/24")
            file.writeline("mac_filter=1c:18:4a")

    global needed_hosts

    create_directory("hosts/")  # create our directory for our host files
    target_ip = target_ip + "/24"
    hosts: list[dict[str, str]] = host_finder(
        target_ip, output)  # network scan
    host_writer(fhfile, hosts, output)  # write found hosts into fhfile
    # filter found hosts based on 1c:18:4a mac and return a list of them
    needed_hosts = host_analyzer(fhfile, mhfile, mac_filter)
    if not needed_hosts:
        print("No modems found!")
        return
    # return needed_hosts
    # print("---------------------------")
    output.config(state='normal')
    output.insert(tkinter.END, "---------------------------\n")
    output.insert(tkinter.END, "---------------------------\n")
    output.config(state='disabled')

def confirmation():
    """This function is not used. It was to prompt warning message before attempting to modify modems.
    Later replaced via buttons that need to be pressed to continue.
    """
    from tkinter import messagebox

    fetch_warning = messagebox.askokcancel(
        "Devam etmek icin modemleri kurgulayin, kurgulama bittiyse OK'a basin.")
    if fetch_warning:
        continue_execution = messagebox.askyesno(
            "Degistirilen ayarlari uygulamak icin devam etmek istiyor musunuz?")
        if not continue_execution:
            exit()


def modem_read_and_odoo_post(output, x_hotel_name, network_scan_caller_button, modem_read_and_odoo_post_caller_button, modem_configure_caller_button):
    """Function route:
    1 - Retrieve ip addresses of the devices that we need.
    2 - Read all of the modem interfaces multithreaded by calling the operation_controller sub routine for each ip address.
    3 - Post the resulting data to Odoo backend. Handled by the controller 'modem_data_send' in Odoo's backend.

    Args:
        output (_type_): tkinter.Text console to pass into scapy_route functions for printing into GUI console.
        x_hotel_name (str): hotel name that's passed from the tkinter GUI and then passed into Odoo by passing it into the json data dictionary.
        network_scan_caller_button: button that's passed from tkinter GUI that we need to enable/disable for our specific operations.
        modem_configure_caller_button: button that's passed from tkinter GUI that we need to enable/disable for our specific operations.
    """
    global needed_hosts

    ip_list = []
    mac_list = []
    # yield ips of the filtered hosts one by one
    for ip, mac in ip_retriever(needed_hosts):
        ip_list.append(ip)
        mac_list.append(mac)
    ########################
    """
    READ OPERATION START
    """
    output.config(state='normal')
    output.insert(
        tkinter.END, "Modem analizi basladi. Bu islem zaman alabilir, lutfen bekleyin...\n")
    output.config(state='disabled')

    mode = "read"
    # threads = []
    # read_queue = Queue()
    # # call multiple versions of the function simultaneously
    # for ip, mac in zip(ip_list, mac_list):
    #     t = threading.Thread(target=operation_controller, args=(
    #         ip, mac, mode, x_hotel_name, read_queue, ""))
    #     threads.append(t)
    #     t.start()
    # for t in threads:
    #     t.join()

    # XXX TEST
    threads = []
    read_queue = Queue()
    
    thread_limit = 25
    thread_semaphore = Semaphore(thread_limit)
    # from WaitGroup import WaitGroup
    wait_group_r = WaitGroup()
    
    for ip, mac in zip(ip_list, mac_list):
        t = threading.Thread(target=operation_controller, args=(
            ip, mac, mode, x_hotel_name, read_queue, "", thread_semaphore, wait_group_r))
        threads.append(t)
        t.start()
    for t in threads:
        wait_group_r.wait()
    # XXX TEST  
    """
    READ OPERATION END
    """

    """
    ODOO POST START
    """
    global modify_queue

    odoo_login()

    # json format. This will be handled by the modem_data_send controller in modem/controller.py
    modem_read_result_list = {"modems": []}
    while not read_queue.empty():
        modem_read_result_list["modems"].append(read_queue.get())
    # populate modify_queue with the results from the read_queue
    for read_modem in modem_read_result_list["modems"]:
        modify_queue.put(read_modem)

    send_datato_odoo(modem_read_result_list)

    output.config(state='normal')
    output.insert(tkinter.END, "Veriler Odoo'ya gonderildi!..\n")
    output.config(state='disabled')
    """
    ODOO POST END
    """
    ############################

    # import tkinterthread
    # tkinterthread.call_nosync(confirmation)
    network_scan_caller_button.config(state="normal")
    modem_configure_caller_button.config(state="normal")
    modem_read_and_odoo_post_caller_button.config(state="normal")

    output.config(state='normal')
    output.insert(tkinter.END, 
                  "Degisiklik yaptiginiz ayarlari uygulamak icin\n'Web Ayarlarini Uygula Butonuna' basin."+
                  "Tekrar ag taramasi yapmak icin\n'Ag Taramasi' butonuna basin.\n")
    output.config(state='disabled')
    
    print("---------------------------")
    output.config(state='normal')
    output.insert(tkinter.END, "---------------------------\n")
    output.insert(tkinter.END, "---------------------------\n")
    output.config(state='disabled')
    # while not event_scan_or_fetch.is_set():
    #     pass

    # event_scan_or_fetch.clear()


def modem_configure(output, network_scan_caller_button, modem_read_and_odoo_post_caller_button, modem_configure_caller_button):
    """Function route:
    1 - Fetch all of the modems from Odoo.
    2 - Map each fetched modem's ip to the ips of needed devices so we know which ip to enter if the ip was modified from Odoo's interface.
    3 - Pass the fetched data to the sub routine interface_operation_modify_compare that compares the read data with the data from Odoo fetch and yields which fields to change.
    4 - Modify all of the modems based on the compare results by starting operation_controller sub routine for each modem that's to be modified.

    Args:
        output (_type_): tkinter.Text console to pass into scapy_route functions for printing into GUI console.
        x_hotel_name (str): hotel name that's passed from the tkinter GUI and then passed into Odoo by passing it into the json data dictionary.
        network_scan_caller_button: button that's passed from tkinter GUI that we need to enable/disable for our specific operations.
        modem_configure_caller_button: button that's passed from tkinter GUI that we need to enable/disable for our specific operations.

    """

    """
    FETCH START
    """
    output.config(state='normal')
    output.insert(tkinter.END, "Odoo'dan veri toplaniyor...\n")
    output.config(state='disabled')

    odoo_login()
    fetched_modem_list: list = fetch_datafrom_odoo()
    # if the ips are changed from Odoo interface, we can't go to those changed ip addresses to change the ip address.
    # we have to first go to the original ip address of the devices and THEN change it.
    # If we match the fetched modems using their mac addresses with the mac addresses from the network scan result, we can
    # then create a list of ips from the network scan result. This new list will contain previous ips of these modified devices.
    global needed_hosts

    ips_of_modified_modems = []
    sorted_fetched_modem_list = []
    sorted_fetched_modem_list = sorted(fetched_modem_list, key=lambda x: x['x_ip'])
    modem_mapping = {modem['x_mac']: modem['x_ip'] for modem in sorted_fetched_modem_list}
    ips_of_modified_modems = [host['ip'] for host in needed_hosts if host['mac'] in modem_mapping]

    """
    FETCH END
    """

    """
    MODIFY OPERATION START
    """
    mode = "modify"
    global modify_queue

    output.config(state='normal')
    output.insert(tkinter.END, "Modem konfigurasyonu basladi. Bu islem zaman alabilir, lutfen bekleyin...\n")
    output.config(state='disabled')
    
    backup_read_modems_list = []
    while not modify_queue.empty():
        backup_read_modems_list.append(modify_queue.get())
    for modem in backup_read_modems_list:
        modify_queue.put(modem)
    
    try:
        if len(fetched_modem_list) == 0 or len(backup_read_modems_list) == 0:
            raise Exception("No changes were made!")
    except Exception as e:
        print(e.args[0])
        output.config(state='normal')
        output.insert(tkinter.END, "Modemlerde degisiklik yapilmadi veya Odoo'ya veri gönderilmedi.\n"
                      "Lütfen Odoo'ya verileri gonderin ve daha sonra modemlerde degisiklik yapin.\n")
        output.config(state='disabled')
    else:
        read_modems_list = []
        while not modify_queue.empty():
            read_modems_list.append(modify_queue.get())
        # get rid of modems in read modem list that don't have their ips in the ips of modified modems list, so
        # we don't compare modems that's in the read result but not in the fetched modem list coming from Odoo.
        for modem in read_modems_list:
            if not modem['x_ip'] in ips_of_modified_modems:
                read_modems_list.remove(modem)
        sorted_read_modems_list = sorted(read_modems_list, key=lambda x: x['x_ip'])
        fields_to_change_list = []
        for fields_to_change in interface_operation_modify_compare(sorted_fetched_modem_list, sorted_read_modems_list):
            fields_to_change_list.append(fields_to_change)
        # from concurrent.futures import ThreadPoolExecutor
        # with ThreadPoolExecutor() as executor:
        #     f = executor.map(modem_login_init, ips_of_modified_modems, "", mode, None, None, fields_to_change)
        # from WaitGroup import WaitGroup
        threads = []
        thread_limit = 25
        thread_semaphore = Semaphore(thread_limit)
        wait_group_w = WaitGroup()
        for ip, fields_to_change in zip(ips_of_modified_modems, fields_to_change_list):
            t = threading.Thread(target=operation_controller, args=(
                ip, "", mode, "", None, fields_to_change, thread_semaphore, wait_group_w))
            threads.append(t)
            t.start()
        for t in threads:  # wait for all threads to finish
            wait_group_w.wait()
            
        output.config(state='normal')
        output.insert(tkinter.END, "Modem konfigurasyonu bitti..\n")
        output.insert(
            tkinter.END, "Verileri Odoo'ya göndermek için 'Sonuclari Odoo'ya Gonder' butonuna basin.\n")
        output.config(state='disabled')
    finally:
        modem_read_and_odoo_post_caller_button.config(state="normal")
        network_scan_caller_button.config(state="normal")
        modem_configure_caller_button.config(state="normal")
        print("---------------------------")
        output.config(state='normal')
        output.insert(tkinter.END, "---------------------------\n")
        output.insert(tkinter.END, "---------------------------\n")
        output.config(state='disabled')
    """
    MODIFY OPERATION END
    """