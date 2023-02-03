
import PySimpleGUI as sg
from main import main
import threading

def maincaller(output):

    main(output) # XXX MAIN CALL -->> PROGRAM STARTS HERE !!!
    window.refresh()    

def button_function(output):  #Call main function while still being able to log into screen
    
    thread = threading.Thread(target=maincaller, args=(output,))
    thread.start()
    
    print("Button clicked!")

layout = [
    [sg.Button("Start", key="button", button_color=('white', 'green'), size=(10, 2)), sg.Text("<-- Start auto config")],
    [sg.Multiline(size=(160, 80), key="output")]
]

window = sg.Window("Modem Configuration Program", layout, size=(700, 600))

window.finalize()

button = window.Element("button")
button.set_tooltip("Click this button to start configuring modems")
output = window.Element("output") #sg.Multiline

while True:
    event, values = window.read()
    if event == "button":
        button_function(output)
    elif event == sg.WIN_CLOSED:
        break

window.close()


