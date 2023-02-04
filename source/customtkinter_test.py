

import sys
from time import sleep
import tkinter
import customtkinter
from threading import Thread, Event
from main import network_scan, modem_read_and_odoo_post, modem_configure
from utility import u_p_setter


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")


class MMO(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.grid_columnconfigure((0, 1, 2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # self.root = customtkinter.CTk()
        self.title("Master Modem Odoo")
        self.geometry(f"{860}x{580}")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # self.frame = customtkinter.CTkFrame(master=self)
        # self.frame.pack(pady=20, padx=20, fill="both", expand=True)
    
        # input frame start
        self.m_input_frame = customtkinter.CTkFrame(master=self)
        self.m_input_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.input_frame = customtkinter.CTkFrame(master=self.m_input_frame)
        self.input_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        # self.frame.grid_rowconfigure(4, weight=1)
        self.hotel_label = customtkinter.CTkLabel(
            master=self.input_frame, text="Otel Adi Girin:", font=("Roboto", 24))
        self.hotel_label.grid(row=0, column=0, pady=12, padx=10)
        self.hotel_name_input = customtkinter.CTkEntry(master=self.input_frame, placeholder_text="Otel Adi")
        self.hotel_name_input.grid(row=0, column=1, pady=12, padx=10)
        
        self.ip_label= customtkinter.CTkLabel(
            master=self.input_frame, text="IP Araligini Girin:", font=("Roboto", 24))
        self.ip_label.grid(row=1, column=0, pady=12, padx=10)
        self.ip_input = customtkinter.CTkEntry(master=self.input_frame, placeholder_text="IP Araligi")
        self.ip_input.grid(row=1, column=1, pady=12, padx=10)
        
        self.username_label= customtkinter.CTkLabel(
            master=self.input_frame, text="Modem Kullanici Adi Girin:", font=("Roboto", 24))
        self.username_label.grid(row=2, column=0, pady=12, padx=10)
        self.username_input = customtkinter.CTkEntry(master=self.input_frame, placeholder_text="Kullanici Adi")
        self.username_input.grid(row=2, column=1, pady=12, padx=10)
        # input frame end
        
        
        #button frame start
        self.m_button_frame = customtkinter.CTkFrame(master=self)
        self.m_button_frame.grid(row=0, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.button_frame = customtkinter.CTkFrame(master=self.m_button_frame)
        self.button_frame.grid(row=0, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        # self.button_frame.grid_rowconfigure(4, weight=1)
        self.network_scan_caller_button = customtkinter.CTkButton(
            master=self.button_frame, text="Simdi Ag Taramasi Yap", command=lambda: self.network_scan_caller(self.GUI_console, self.ip_input.get()))
        self.network_scan_caller_button.grid(row=0, column=2, pady=12, padx=10)
        
        self.modem_read_and_odoo_post_caller_button = customtkinter.CTkButton(
            master=self.button_frame, text="Tarama Sonuclarini Odoo'ya Gonder", command=lambda: self.modem_read_and_odoo_post_caller(self.GUI_console, self.hotel_name_input.get()))
        self.modem_read_and_odoo_post_caller_button.grid(row=1, column=2, pady=12, padx=10)
        
        self.modem_configure_caller_button = customtkinter.CTkButton(
            master=self.button_frame, text="Tarama Sonuclarini Odoo'ya Gonder", command=lambda: self.modem_configure_caller())
        self.modem_configure_caller_button.grid(row=3, column=2, pady=12, padx=10)
        #button frame end
        
        #GUI console
        self.console_frame = customtkinter.CTkFrame(master=self)
        self.console_frame.grid(row=1, column=0, columnspan=3, padx=(20, 20), pady=(20, 0), sticky="nsew")  
        self.GUI_console = customtkinter.CTkTextbox(self.console_frame)
        self.GUI_console.grid(row=1, column=0, sticky="nsew")
        self.GUI_console.pack(fill="both", expand=True, padx=20, pady=20)
        # self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        # self.slider_progressbar_frame.grid(row=1, column=1, columnspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.modem_configure_caller_button.configure(state="disabled")
        self.modem_read_and_odoo_post_caller_button.configure(state="disabled")
        
    def on_closing(self):
        """Called when you press the X button to close the program
        """
        sleep(0.5)
        self.destroy()
        
        
    def network_scan_caller(self, output, target_ip):
        """This button function calls the function that scans the network for modems

        Args:
            output (_type_): tkinter.Text console
            target_ip (_type_): ip interval to scan
        """
        # modem_configure_caller_button.config(state="disable")
        self.network_scan_caller_button.configure(state="disabled")
        self.modem_configure_caller_button.configure(state="disabled")
        self.modem_read_and_odoo_post_caller_button.configure(state="disabled")

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
        self.after(
            5000, lambda: self.modem_read_and_odoo_post_caller_button.configure(state="enabled"))
        self.after(5000, lambda: self.network_scan_caller_button.config(state="enabled"))
        self.after(5000, lambda: self.modem_configure_caller_button.config(state="enabled"))
        # network_scan(target_ip, output)

if __name__ == "__main__":
    mmo = MMO()
    mmo.mainloop()