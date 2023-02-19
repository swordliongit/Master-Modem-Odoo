#
# Author: Kılıçarslan SIMSIKI
#


from configparser import ConfigParser
from time import sleep
import customtkinter
from threading import Thread, Event
from main import network_scan, modem_read_and_odoo_post, modem_configure
from utility import u_p_setter
import json

customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("dark-blue")

class MmoGui(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # saved defaults
        self.defaults = {}
        # read the config file
        config = ConfigParser()
        config.read("../required/credentials.ini")
        self.SAVED_ENTRIES_PATH = config.get("entries", "path")
        
        self.grid_columnconfigure((0, 1, 2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=0)
        self.grid_rowconfigure(3, weight=1)

        # self.root = customtkinter.CTk()
        self.title("Master Modem Odoo")
        self.geometry(f"{860}x{780}")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # self.frame = customtkinter.CTkFrame(master=self)
        # self.frame.pack(pady=20, padx=20, fill="both", expand=True)
    
        # input frame start
        self.m_input_frame = customtkinter.CTkFrame(master=self)
        self.m_input_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.input_frame = customtkinter.CTkFrame(master=self.m_input_frame)
        self.input_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew")
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
        
        self.password_label= customtkinter.CTkLabel(
            master=self.input_frame, text="Modem Parolasini Girin:", font=("Roboto", 24))
        self.password_label.grid(row=3, column=0, pady=12, padx=10)
        self.password_input = customtkinter.CTkEntry(master=self.input_frame, placeholder_text="Parola", show="*")
        self.password_input.grid(row=3, column=1, pady=12, padx=10)
        
        #button frame start
        self.m_button_frame = customtkinter.CTkFrame(master=self)
        self.m_button_frame.grid(row=0, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.button_frame = customtkinter.CTkFrame(master=self.m_button_frame)
        self.button_frame.grid(row=0, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        # self.button_frame.grid_rowconfigure(4, weight=1)
        self.network_scan_caller_button = customtkinter.CTkButton(
            master=self.button_frame, text="Simdi Ag Taramasi Yap", command=self.network_scan_caller)
        self.network_scan_caller_button.grid(row=0, column=2, pady=12, padx=10)
        
        self.modem_read_and_odoo_post_caller_button = customtkinter.CTkButton(
            master=self.button_frame, text="Tarama Sonuclarini Odoo'ya Gonder", command=self.modem_read_and_odoo_post_caller)
        self.modem_read_and_odoo_post_caller_button.grid(row=1, column=2, pady=12, padx=10)
        
        self.modem_configure_caller_button = customtkinter.CTkButton(
            master=self.button_frame, text="Modem Ayarlarini Uygula", command=self.modem_configure_caller)
        self.modem_configure_caller_button.grid(row=2, column=2, pady=12, padx=10)
        
        # progress bar frame 
        self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.slider_progressbar_frame.grid(row=1, column=0, columnspan=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.progressbar = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar.grid(row=1, column=0, sticky="ew")
        self.progressbar.pack(fill="both", expand=True, padx=30, pady=10)
        
        #GUI console
        self.console_frame = customtkinter.CTkFrame(master=self)
        self.console_frame.grid(row=2, column=0, columnspan=3, rowspan=3, padx=(20, 20), pady=(20, 0), sticky="nsew")  
        self.gui_console = customtkinter.CTkTextbox(self.console_frame, font=("Roboto", 16))
        self.gui_console.grid(row=2, column=0, sticky="nsew")
        self.gui_console.pack(fill="both", expand=True, padx=20, pady=20)
        
        # initial values
        self.modem_configure_caller_button.configure(state="disabled")
        self.modem_read_and_odoo_post_caller_button.configure(state="disabled")
        self.progressbar.configure(mode="indeterminnate")
        # self.progressbar_1.start()
        
        
    def on_closing(self):
        """Called when you press the X button to close the program. Kills the GUI and the opened chromedriver threads
        """
        sleep(0.5)

        import psutil
        PROCNAME = "Master Modem Odoo.exe"
        DRIVER = "chromedriver.exe"
        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() == PROCNAME or proc.name() == DRIVER:
                proc.kill()
        sleep(1)
        self.destroy()
          
    def network_scan_caller(self):
        """This button function calls the function that scans the network for modems

        Args:
            self (MmoGui): Pass in self to access to variables
        """
        self.modem_configure_caller_button.configure(state="disabled")
        self.modem_read_and_odoo_post_caller_button.configure(state="disabled")
        
        # if the button is pressed and the entry is filled, save all of the entries
        if len(self.ip_input.get()) != 0:
            self.defaults["ip_input"] = self.ip_input.get()
            self.defaults["hotel_name_input"] = self.hotel_name_input.get()
            self.defaults["username_input"] = self.username_input.get()
            self.defaults["password_input"] = self.password_input.get()
            with open(self.SAVED_ENTRIES_PATH, "w") as jsonf:
                json.dump(self.defaults, jsonf, indent=5)
            thread = Thread(target=network_scan, args=(self, str(self.ip_input.get())))
            thread.start()
        else:
            self.gui_console.configure(state='normal')
            self.gui_console.insert(customtkinter.END, "Taramak icin IP adresi girin!\n")
            self.gui_console.configure(state='disabled')   
            
        self.gui_console.update()
        
        # self.progressbar_1.stop()
        # network_scan(target_ip, output)

    def modem_read_and_odoo_post_caller(self):
        """This button function calls the function that does web scraping that collects data from modem interfaces and
    posts this data to Odoo database  

        Args:
            self (MmoGui): Pass in self to access to variables
        """
        # set username and password of the modem interfaces through the corresponding fields
        u_p_setter(self.username_input.get(), self.password_input.get())

        state_list = [] 
        state_error = False
        # show error msgs as many as there are empty entries that are necessary
        if len(self.hotel_name_input.get()) == 0:
            state_error = True
            state_list.append("Otel adi girin!\n")
        if len(self.username_input.get()) == 0:
            state_error = True
            state_list.append("Modem kullanici adi girin!\n")
        if len(self.password_input.get()) == 0:
            state_error = True
            state_list.append("Modem parolasi girin!\n")
        # if there are no errors at all, launch the function
        if not state_error:
            thread = Thread(target=modem_read_and_odoo_post, args=(self, self.hotel_name_input.get()))
            thread.start() 
        else:
            # save the entries, so we can launch the gui with those saved entries already filled in
            self.defaults["hotel_name_input"] = self.hotel_name_input.get()
            self.defaults["username_input"] = self.username_input.get()
            self.defaults["password_input"] = self.password_input.get()
            with open(self.SAVED_ENTRIES_PATH, "w") as jsonf:
                json.dump(self.defaults, jsonf, indent=5)
            self.gui_console.configure(state='normal')
            for cmd in state_list:
                self.gui_console.insert(customtkinter.END, cmd)
            self.gui_console.configure(state='disabled') 
        
        self.gui_console.update()
    
    def modem_configure_caller(self):
        """This button function calls the function that modifies each modem
        """
        self.network_scan_caller_button.configure(state="disabled")
        self.modem_configure_caller_button.configure(state="disabled")
        self.modem_read_and_odoo_post_caller_button.configure(state="disabled")
        
        thread = Thread(target=modem_configure, args=(self,))
        thread.start()
        self.gui_console.update()
    
    
if __name__ == "__main__":
    # initate the gui
    MmoGui = MmoGui()
    # load saved settings
    with open(MmoGui.SAVED_ENTRIES_PATH, "r") as f:
        MmoGui.defaults = json.load(f)
    # if there are any saved settings, load them to the corresponding entries
    for k, v in MmoGui.defaults.items():
        match k:
            case "hotel_name_input":
                if len(v) != 0:
                    MmoGui.hotel_name_input.insert(customtkinter.INSERT, str(MmoGui.defaults["hotel_name_input"]))
            case "ip_input":
                if len(v) != 0:
                    MmoGui.ip_input.insert(customtkinter.INSERT, str(MmoGui.defaults["ip_input"]))
            case "username_input":
                if len(v) != 0:
                    MmoGui.username_input.insert(customtkinter.INSERT, str(MmoGui.defaults["username_input"]))
            case "password_input":
                if len(v) != 0:   
                    MmoGui.password_input.insert(customtkinter.INSERT, str(MmoGui.defaults["password_input"]))
    # start the gui
    MmoGui.mainloop()