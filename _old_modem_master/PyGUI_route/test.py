with open("modem_settings.txt") as file:
    username = file.readline().split('=')[1].strip('\n')
    password = file.readline().split('=')[1]
        