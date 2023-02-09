#
# Author: Kılıçarslan SIMSIKI
#


from selenium_dependencies import *
from time import sleep
from collections import OrderedDict
import utility
from configparser import ConfigParser

def is_logged_out(driver):
    try:
        driver.find_elements(By.ID, "login_in")
    except:
        return False
    else:
        return True


def modem_logout(driver):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))).click()
    WebDriverWait(driver, 10).until(lambda d: Alert(d)).accept()
    sleep(0.5)


def modem_login(driver, ip):
    url = "http://" + ip + "/cgi-bin/luci"
    username = utility.username
    password = utility.password

    try:
        # print("Trying to log in...")
        driver.get(url)  # open the url
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.ID, "login_in").click()  # login button
        sleep(0.5)
        try:
            WebDriverWait(driver, 10).until(lambda d: Alert(d)).accept()
        except:
            # HACK
            pass
        # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div/form/div[3]/button[1]"))).click()
        # WebDriverWait(driver, 5).until(lambda driver: "http://192.168.1.1/cgi-bin/luci/admin/" != driver.current_url)
    except:
        print(f"Login failed for {ip}")
        return -1  # XXX GOTTA CHANGE
    else:
        print(f"Logged in successfully for {ip}")

def operation_controller(ip, mac, mode, x_hotel_name, read_queue, fields_to_change, thread_semaphore, wait_group):
    """This function is supposed to be threaded. Called for each ip address. Separates the program into read and modify subroutines.
    interface_operation_read returns the dictionary containing each field of the modem and queues it into read_queue that's passed
    from the caller.

    Args:
        ip (str): _description_
        mac (str): _description_
        mode (str): _description_
        x_hotel_name (str): _description_
        read_queue (Queue): _description_
        fields_to_change (dict): fields that need to be changed, used in modify mode.
        thread_semaphore (threading.Semaphore): semaphore needed to control number of active threads
        wait_group (WaitGroup): class used for custom join operations
    """
    # add each thread to the group
    wait_group.add(1)
    
    config = ConfigParser()
    config.read("Master-Modem-Odoo/required/credentials.ini")
    CHROME_DRIVER_PATH = config.get("chromedriver", "path")
    # start the semaphore
    with thread_semaphore:
        #options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # silent browser
        driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)
        # driver = webdriver.Chrome("Python/modem_master_odoo/support/chromedriver")
        modem_login(driver, ip)
        
        if mode == "read":
            # modem_read_result_dict = {}
            modem_read_result_dict = interface_operation_read(driver, x_hotel_name, mac)
            read_queue.put(modem_read_result_dict)
        elif mode == "modify":
            interface_operation_modify(driver, fields_to_change, ip)
        # current_url = driver.current_url
    # signal for finish
    wait_group.done()

def interface_operation_read(driver, x_hotel_name, mac):
    """function that does the actual search operation inside the page and retrieves elements

    Args:
        driver (_type_): _description_
        output (_type_): GUI log screen output object to pass through
    """
    
    # {"modem_image":False,"__last_update":False,"name":"protometa","x_uptime":False,"x_wireless_status":False,"x_channel":False,"x_mac":False,"x_device_info":False,"x_ip":False,"x_subnet":False,"x_dhcp":False,"x_enable_wireless":False,"x_enable_ssid1":False,"x_enable_ssid2":False,"x_enable_ssid3":False,"x_enable_ssid4":False,"x_manual_time":False,"x_new_password":False,"modem_id":False,"city":False,"live_status":"offline","last_action_user":3,"modem_status":False,"modem_home_mode":False,"customer_id":[[6,False,[]]],"modem_update":False,"modem_version":False}
    # "args" key of the dictionary has a list of dictionary. This dictionary will contain the fields of a record in Odoo.
    # obj_dict =  {"id":63,"jsonrpc":"2.0","method":"call","params":{"args":[{}],"model":"modem.profile","method":"create","kwargs":{"context":{"lang":"en_US","tz":"Europe/Istanbul","uid":2,"allowed_company_ids":[1]}}}}
    # ---------^
    # XXX START OF THE AUTOMATION XXX
    print(f"Read Operation launched for {mac}")
    
    modem_read_result_dict = {}

    # Network -> Uptime
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Status"))).click()
    sleep(0.5)

    x_uptime = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "uptime"))).text
    modem_read_result_dict['x_uptime'] = x_uptime

    # LAN Information -> Wireless Status & Channel & MAC & IP, device info
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "LAN Information"))).click()
    sleep(0.5)

    x_wireless_status = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "wlan-ifc-status"))).text
    modem_read_result_dict['x_wireless_status'] = x_wireless_status

    # channel may or may not be present, depending on wireless status(on/off)
    if x_wireless_status == "enable":
        x_channel = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.ID, "wlan-ifc-channel")))
        modem_read_result_dict['x_channel'] = x_channel.text
    else:
        modem_read_result_dict['x_channel'] = ""

    # x_mac = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ra0-ifc-mac"))).text

    # if x_mac == "00:00:00:00:00:00": # Fix the error on interface reading
    #    x_mac = mac
    modem_read_result_dict['x_mac'] = mac

    x_device_info = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "#maincontent > div > div:nth-child(4) > div > div:nth-child(3) > table"))).text
    modem_read_result_dict['x_device_info'] = x_device_info

    # Network: LAN Settings -> IP, Subnet, dhcp
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Network"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "LAN Settings"))).click()
    sleep(0.5)

    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#cbid\.dhcp\.dnsmasq_0\.ipaddr')))
    x_ip = field.get_attribute('value')
    modem_read_result_dict['x_ip'] = x_ip

    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#cbid\.dhcp\.dnsmasq_0\.netmask')))
    x_subnet = field.get_attribute('value')
    modem_read_result_dict['x_subnet'] = x_subnet

    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cbid\.dhcp\.dnsmasq_0\.dhcp_en")))
    x_dhcp = True if field.is_selected() else False
    modem_read_result_dict['x_dhcp'] = x_dhcp

    # Network: WLAN -> Enable Wireless
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "WLAN"))).click()
    sleep(1.5)

    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cbid\.wireless\.wifi_ctrl_0\.enabled")))
    x_enable_wireless = True if field.is_selected() else False
    modem_read_result_dict['x_enable_wireless'] = x_enable_wireless

    if x_enable_wireless == True:
        field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cbid\.wireless\.ra0\.enabled")))
        x_enable_ssid1 = True if field.is_selected() else False
        modem_read_result_dict['x_enable_ssid1'] = x_enable_ssid1

        field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cbid\.wireless\.ra1\.enabled")))
        x_enable_ssid2 = True if field.is_selected() else False
        modem_read_result_dict['x_enable_ssid2'] = x_enable_ssid2

        field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cbid\.wireless\.ra2\.enabled")))
        x_enable_ssid3 = True if field.is_selected() else False
        modem_read_result_dict['x_enable_ssid3'] = x_enable_ssid3

        field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cbid\.wireless\.ra3\.enabled")))
        x_enable_ssid4 = True if field.is_selected() else False
        modem_read_result_dict['x_enable_ssid4'] = x_enable_ssid4

        # Disable hidden ssid's
        hidden_ssid_disabled = False
        for i in range(4):
            field = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, f"#cbid\.wireless\.ra{i}\.hidden")))
            if field.is_selected() == True:
                field.click()
                hidden_ssid_disabled = True
        if hidden_ssid_disabled == True:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#maincontent > form > div.cbi-section > div > div > input:nth-child(1)"))).click()
            sleep(5)
    else:
        modem_read_result_dict['x_enable_ssid1'] = False
        modem_read_result_dict['x_enable_ssid2'] = False
        modem_read_result_dict['x_enable_ssid3'] = False
        modem_read_result_dict['x_enable_ssid4'] = False
    # Network: Time Synchronisation -> Manual Time
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Time Synchronisation"))).click()
    sleep(0.5)
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#cbid\.ntpclient\.cfg04887d\.manual_time')))
    x_manual_time = field.get_attribute('value')
    modem_read_result_dict['x_manual_time'] = x_manual_time

    # System: Administration -> New Password
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "System"))).click()
    sleep(0.5)
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pw1')))
    x_new_password = field.get_attribute('value')
    modem_read_result_dict['x_new_password'] = x_new_password

    modem_read_result_dict['x_hotel_name'] = x_hotel_name

    import datetime
    modem_read_result_dict['x_update_date'] = str(datetime.datetime.now())

    print(f"Read Operation Completed for {mac}")

    if not is_logged_out(driver):
        modem_logout(driver)
    # XXX END OF THE AUTOMATION XXX

    # modem_read_result = {}

    # for k, v in modem_read_result_dict.items():
    #     #obj_dict['params']['args'][0].update({k:v}) # add newly fetched fields into the main dict
    #     modem_read_result[k] = v
    # queue.put(obj_dict)
    # sleep(1)
    return modem_read_result_dict


def interface_operation_modify_compare(fetched_modem_list: list, fields_to_compare_list: list) -> OrderedDict:

    # fetched_modem_list = [{'x_ip': "192.168.5.1", ...}, {'x_ip: "192.168.5.2", ...}, ...]
    print("Comparing values..")

    fields_we_want = ['x_ip', 'x_subnet', 'x_dhcp', 'x_enable_wireless', 'x_enable_ssid1',
                      'x_enable_ssid2', 'x_enable_ssid3', 'x_enable_ssid4', 'x_manual_time',
                      'x_new_password']
    # e.g. modem = {'x_ip': "192.168.5.1", ...}
    for modem, fields_to_compare in zip(fetched_modem_list, fields_to_compare_list):
        filtered_modem = {key: modem[key] for key in fields_we_want}
        fields_to_change = OrderedDict()
        for k, v in filtered_modem.items():  # e.g. k = 'x_ip' v = "192.168.5.1"
            # if "192.168.5.1" != modem_read_result_dict['x_ip']
            if v != fields_to_compare[k]:
                # if a field is modified, add it into our dict
                fields_to_change[k] = v
        print(f"Modem {modem['x_mac']} change list: {list(fields_to_change)}")
        # This is a button so I can't check the state of it in the read operation
        if 'x_reboot' in modem and 'x_reboot' == True:
            fields_to_change['x_reboot'] = modem['x_reboot']
            # fields_to_change.move_to_end('x_reboot', last=True)
        yield fields_to_change  # modify for each modem

    print("Values compared..")


def interface_operation_modify(driver, fields_to_change: OrderedDict, ip_for_modify):
    print(f"Modify Operation launched for {ip_for_modify}")

    WLAN_task_list = []
    LAN_Settings_task_list = []
    x_manual_time = "" # if dhcp is modified, it will reset the manual time, so I have to handle this separately.
    for k, v in fields_to_change.items():
        match k:
            case 'x_ip':
                LAN_Settings_task_list.append({k: v})
            case 'x_subnet':
                LAN_Settings_task_list.append({k: v})
            case 'x_dhcp':
                LAN_Settings_task_list.append(k)
            case 'x_enable_wireless':
                WLAN_task_list.append(k)
                # WLAN_task_list.append(v)
            case 'x_enable_ssid1':
                WLAN_task_list.append(k)
            case 'x_enable_ssid2':
                WLAN_task_list.append(k)
            case 'x_enable_ssid3':
                WLAN_task_list.append(k)
            case 'x_enable_ssid4':
                WLAN_task_list.append(k)
            case 'x_manual_time':
                x_manual_time = v
            case 'x_new_password':
                modify_x_new_password(driver, v)
            case 'x_reboot':
                pass
            
    if len(WLAN_task_list) != 0:
        if 'x_enable_wireless' in WLAN_task_list:
            WLAN_task_list.remove('x_enable_wireless')
            WLAN_task_list.insert(0, 'x_enable_wireless')      
        modify_WLAN_task_control(driver, WLAN_task_list)
        
    if 'x_manual_time' in fields_to_change:
        if is_logged_out(driver):
            modem_login(driver, ip_for_modify)
        modify_x_manual_time(driver, x_manual_time)
        
    if 'x_reboot' in fields_to_change:
        if is_logged_out(driver):
            modem_login(driver, ip_for_modify)
        modify_x_reboot(driver)
        
    if len(LAN_Settings_task_list) != 0:
        if is_logged_out(driver):
            modem_login(driver, ip_for_modify)
        modify_LAN_task_control(driver, LAN_Settings_task_list)
        
    print(f"Modify operation completed for {ip_for_modify}")
    
    if is_logged_out(driver):
        return True
    else:
        modem_logout(driver)


def modify_x_reboot(driver):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, 'System'))).click()
    sleep(0.5)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, 'Reboot'))).click()
    sleep(0.5)
    # reboot button
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#maincontent > div > div:nth-child(2) > div > div > div:nth-child(3) > div > input'))).click()
    WebDriverWait(driver, 10).until(lambda d: Alert(d)).accept()
    sleep(60)


def modify_LAN_task_control(driver, LAN_Settings_task_list):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Network"))).click()
    sleep(0.5)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "LAN Settings"))).click()
    sleep(0.5)

    for field in LAN_Settings_task_list:
        if isinstance(field, dict):
            if 'x_ip' in field:
                modify_x_ip(driver, field['x_ip'])
            if 'x_subnet' in field:
                modify_x_subnet(driver, field['x_subnet'])
        if field == 'x_dhcp':
            modify_x_dhcp(driver)

    # Apply button
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#maincontent > form > div.cbi-section > div > div > input:nth-child(1)"))).click()
    WebDriverWait(driver, 10).until(lambda d: Alert(d)).accept()
    sleep(60)


def modify_x_ip(driver, v):
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#cbid\.dhcp\.dnsmasq_0\.ipaddr')))
    field.clear()
    field.send_keys(v)


def modify_x_subnet(driver, v):
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#cbid\.dhcp\.dnsmasq_0\.netmask')))
    field.clear()
    field.send_keys(v)


def modify_x_dhcp(driver):
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#cbid\.dhcp\.dnsmasq_0\.dhcp_en')))
    field.click()


def modify_WLAN_task_control(driver, WLAN_task_list):
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.LINK_TEXT, "Network"))).click()
    sleep(0.5)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "WLAN"))).click()
    sleep(1.5)
    # x_enable_wireless = True if True in WLAN_task_list else False
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cbid\.wireless\.wifi_ctrl_0\.enabled")))
    x_enable_wireless = True if field.is_selected() else False
    
    for field in WLAN_task_list:
        match field:
            case 'x_enable_wireless':  
                field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cbid\.wireless\.wifi_ctrl_0\.enabled")))
                field.click()
                x_enable_wireless = True if field.is_selected() else False
            case 'x_enable_ssid1':
                if x_enable_wireless:
                    modify_x_enable_ssid1(driver) 
            case 'x_enable_ssid2':
                if x_enable_wireless:
                    modify_x_enable_ssid2(driver)
            case 'x_enable_ssid3':
                if x_enable_wireless:
                    modify_x_enable_ssid3(driver)
            case 'x_enable_ssid4':
                if x_enable_wireless:
                    modify_x_enable_ssid4(driver)
    # Apply button
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#maincontent > form > div.cbi-section > div > div > input:nth-child(1)"))).click()
    sleep(5)


def modify_x_enable_ssid1(driver):
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cbid\.wireless\.ra0\.enabled")))
    field.click()
       
       
def modify_x_enable_ssid2(driver):
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cbid\.wireless\.ra1\.enabled")))
    field.click()
     
     
def modify_x_enable_ssid3(driver):
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cbid\.wireless\.ra2\.enabled")))
    field.click()
    
    
def modify_x_enable_ssid4(driver):
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cbid\.wireless\.ra3\.enabled")))
    field.click()


def modify_x_manual_time(driver, v):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Network"))).click()
    sleep(0.5)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Time Synchronisation"))).click()
    sleep(0.5)
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#cbid\.ntpclient\.cfg04887d\.manual_time')))
    field.clear()
    field.send_keys(v)
    # Apply button
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#maincontent > form > div.cbi-section > div > div > input:nth-child(1)"))).click()
    sleep(5)
    # if is_logged_out(driver):
    #     modem_login(driver, ip_for_modify)


def modify_x_new_password(driver, v):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "System"))).click()
    sleep(0.5)
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pw1')))
    field.click()
    field.send_keys(v)
