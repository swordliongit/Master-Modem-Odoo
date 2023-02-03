#
# Author: Kılıçarslan SIMSIKI
#


import sys
from time import sleep
import tkinter
from tkinter import ttk
from threading import Thread, Event
from main import network_scan, modem_read_and_odoo_post, modem_configure
from utility import u_p_setter

# event_scan_or_fetch = Event()

# first_press = True
# XXX
# tkinter GUI application
# XXX


def modem_configure_caller():
    """This button function calls the function that modifies each modem

    """
 
    # global event_scan_or_fetch
    # event_scan_or_fetch.set()

    network_scan_caller_button.config(state="disable")
    modem_configure_caller_button.config(state="disable")
    modem_read_and_odoo_post_caller_button.config(state="disable")

    thread = Thread(target=modem_configure, args=(output, network_scan_caller_button,
                    modem_read_and_odoo_post_caller_button, modem_configure_caller_button))
    thread.start()
    output.update()


def network_scan_caller(output, target_ip):
    """This button function calls the function that scans the network for modems

    Args:
        output (_type_): tkinter.Text console
        target_ip (_type_): ip interval to scan
    """
    # modem_configure_caller_button.config(state="disable")
    network_scan_caller_button.config(state="disable")
    modem_configure_caller_button.config(state="disable")
    modem_read_and_odoo_post_caller_button.config(state="disable")

    # global event_scan_or_fetch
    # global first_press

    # if first_press:
    #     first_press = False
    # else:
    #     first_press = True
    #     event_scan_or_fetch.set()

    thread = Thread(target=network_scan, args=(output, target_ip))
    thread.start()
    output.update()

    # enable other 2 buttons after 5 seconds
    root.after(
        5000, lambda: modem_read_and_odoo_post_caller_button.config(state="enable"))
    root.after(5000, lambda: network_scan_caller_button.config(state="enable"))
    root.after(5000, lambda: modem_configure_caller_button.config(state="enable"))
    # network_scan(target_ip, output)


def modem_read_and_odoo_post_caller(output, x_hotel_name):
    """This button function calls the function that does web scraping that collects data from modem interfaces and
   posts this data to Odoo database  

    Args:
        output (_type_): _description_
        x_hotel_name (_type_): _description_
    """
    u_p_setter(username_input.get(), password_input.get())

    network_scan_caller_button.config(state="disable")
    modem_configure_caller_button.config(state="disable")
    modem_read_and_odoo_post_caller_button.config(state="disable")

    thread = Thread(target=modem_read_and_odoo_post, args=(output, x_hotel_name, network_scan_caller_button, modem_read_and_odoo_post_caller_button, modem_configure_caller_button))
    thread.start()
    output.update()


def GUI_init():
    pass


def on_closing():
    """Called when you press the X button to close the program
    """
    sleep(0.5)
    root.destroy()


root = tkinter.Tk()
root.title("Modem Master Program")

root.protocol("WM_DELETE_WINDOW", on_closing)
# root.grid_columnconfigure(0, weight=1)
# root.grid_columnconfigure(1, weight=1)
# root.grid_columnconfigure(2, weight=1)
# root.grid_rowconfigure(0, weight=1)
# root.grid_rowconfigure(1, weight=1)
# root.grid_rowconfigure(2, weight=1)

hotel_label = ttk.Label(root, text="Otel Adi Girin ------>")
hotel_label.grid(row=0, column=0, padx=10, pady=10)

hotel_name_input = ttk.Entry(root)
hotel_name_input.grid(row=0, column=1, padx=10, pady=10)

ip_label = ttk.Label(root, text="IP Araligini Girin ------>")
ip_label.grid(row=1, column=0, padx=10, pady=10)

ip_input = ttk.Entry(root)
ip_input.grid(row=1, column=1, padx=10, pady=10)

username_label = ttk.Label(root, text="Modem Kullanici Adi Girin ------>")
username_label.grid(row=2, column=0, padx=10, pady=10)

username_input = ttk.Entry(root)
username_input.grid(row=2, column=1, padx=10, pady=10)

password_label = ttk.Label(root, text="Modem Sifresini Girin ------>")
password_label.grid(row=3, column=0, padx=10, pady=10)

password_input = ttk.Entry(root)
password_input.grid(row=3, column=1, padx=10, pady=10)

# Buttons

network_scan_caller_button = ttk.Button(
    root, text="Simdi Ag Taramasi Yap", command=lambda: network_scan_caller(output, ip_input.get()))
network_scan_caller_button.grid(
    row=0, column=2, columnspan=2, padx=10, pady=10)

modem_read_and_odoo_post_caller_button = ttk.Button(
    root, text="Sonuclari Odoo'ya Gonder", command=lambda: modem_read_and_odoo_post_caller(output, hotel_name_input.get()))
modem_read_and_odoo_post_caller_button.grid(
    row=1, column=2, columnspan=2, padx=10, pady=10)

modem_configure_caller_button = ttk.Button(
    root, text="Web Ayarlarini Uygula", command=lambda: modem_configure_caller())
modem_configure_caller_button.grid(row=2, column=2, padx=10, pady=10)

# console
output = tkinter.Text(root)
output.grid(row=4, column=0, columnspan=2, padx=10, pady=10)


modem_configure_caller_button.config(state="disable")
modem_read_and_odoo_post_caller_button.config(state="disable")

root.mainloop()  # GUI launched

# root.after(0, GUI_init)
