from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

from time import sleep

def modem_login_init():
    """function to set browser to run in background, initialize driver object

    Returns:
        Chrome driver: driver to return
    """
    
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument("--headless") # silent browser
    
    # our driver
    from selenium import webdriver
    driver = webdriver.Chrome("chromedriver", options=chrome_options)
    
    return driver
    
    
def modem_login(driver, ip, output, username="R3000admin", password="admin"):
    """function to read username and password and open the login screen to log into the site
    
    """  
    url = "http://" + ip + "/cgi-bin/luci"
    
    import os
    if os.stat("modem_settings.txt").st_size != 0:
        with open("modem_settings.txt") as file:
            username = file.readline().split('=')[1].strip('\n')
            password = file.readline().split('=')[1]
    else:
        with open("modem_settings.txt", 'w') as file:
            file.writelines("username="+username)
            file.writelines("password="+password)
    
    try:
        output.print("Trying to log in...")
        driver.get(url) # open the url
        
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.ID, "login_in").click() # login button
        #WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div/form/div[3]/button[1]"))).click()


        #WebDriverWait(driver, 5).until(lambda driver: "http://192.168.1.1/cgi-bin/luci/admin/" != driver.current_url)
    except:
        ############################# XXX
        output.print("Login failed!")
        ############################# XXX
        return -1 # XXX GOTTA CHANGE
   
    
    """current_url = driver.current_url"""
    
    interface_operation(driver, output)


def interface_operation(driver, output):
    """function that does the actual search operation inside the page

    Args:
        driver (_type_): _description_
        output (_type_): GUI log screen output object to pass through
    """

    ############################# XXX
    output.print("Logged in successfully!")
    ############################# XXX

    ############################# XXX
    output.print("Operation launched...")
    ############################# XXX
    
    try:
        # go to another page
        driver.find_element(By.LINK_TEXT, "Network").click()

        # go to another page
        driver.find_element(By.LINK_TEXT, "Time Synchronisation").click()

        # find the text field
        txt_field = driver.find_element(By.ID, "cbid.ntpclient.cfg04887d.manual_time")
        txt_field.click()
        txt_field.send_keys(Keys.CONTROL + "a") # select all
        txt_field.send_keys(Keys.DELETE) 
        txt_field.send_keys("2016-04-23 12:00:39") # change

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "cbi.apply"))).click() # Apply button
    except:
        output.print("Exception Occured. Operation failed...")
    

    ############################# XXX
    output.print("Operation successful!")
    ############################# XXX