#!/usr/bin/python3
import pyvisa as visa
import threading
import time, re
from io import BytesIO
from PIL import Image, ImageTk
import base64
import PySimpleGUI as sg
import pretty_errors


"""
    DESIGN PATTERN - Multithreaded Long Tasks GUI using shared global variables
    Presents one method for running long-running operations in a PySimpleGUI environment.
    The PySimpleGUI code, and thus the underlying GUI framework, runs as the primary, main thread
    The "long work" is contained in the thread that is being started. Communicating is done (carefully) using global variables
    There are 2 ways "progress" is being reported to the user. 
    You can simulate the 2 different scenarios that happen with worker threads.
    1.  If a the amount of time is known ahead of time or the work can be broken down into countable units, then a progress bar is used.  
    2.  If a task is one long chunk of time that cannot be broken down into smaller units, then an animated GIF is shown that spins as
    long as the task is running.
"""

def selectScope():
    entries = []
    newl_char = "\n"
    success = False
    for n,i in enumerate(rm.list_resources()):
        if re.search('TCPIP',i):
            entries.append(f'instrument:{i} index: {n}') 
    selection = sg.popup_get_text(f'{newl_char.join(entries)}','select a scope')
    while success == False:
        try:
            scope = rm.open_resource(rm.list_resources()[int(selection)])
            success = True
        except ValueError:
            selection = sg.popup_get_text(f'ERROR: Must type one of the indices listed here:\n{newl_char.join(entries)}','select a scope')
    sg.popup(f'Selected: {scope.query("*IDN?")}')
    return scope

def initializeScope(scope):
    scope.timeout = 10000 # ms
    scope.encoding = 'latin_1'
    scope.read_termination = '\n'
    scope.write_termination = None
    scope.write('*cls') # clear ESR
    scope.write('header OFF') # disable attribute echo in replies

def fetch_base64Image(inst,placeholder=False):
    buffered = BytesIO()
    if placeholder == False:
        inst.write('SAVE:IMAGE:FILEF png')
        inst.write('HARDCOPY START')
        raw_data = inst.read_raw()
        im = Image.open(BytesIO(raw_data))
        im.save(buffered, format='PNG')
        img_str = base64.b64encode(buffered.getvalue())
    else:
        placeholder = Image.new('RGB',(1,1), (255, 255, 255))
        placeholder.save(buffered, format='PNG')
        img_str = base64.b64encode(buffered.getvalue())
    return img_str

def decodeAndConvert_base64String(b64_str, memory_mode = False):
    image = Image.open(BytesIO(base64.b64decode(b64_str)))
    if memory_mode == False:
        return ImageTk.PhotoImage(image)
    if memory_mode == True:
        buffered = BytesIO()
        image.save(buffered, format='PNG')
        return buffered

def frame(inst):    
    inst.write('HARDCOPY START')
    # inst.write('SAVE:IMAGE')
    fr = ImageTk.PhotoImage(Image.open(BytesIO(inst.read_raw())))
    inst.write("*CLS")
    return fr

def updateScreen(inst, key, window):
    b64_str = fetch_base64Image(inst)
    
    #window.write_event_value(key, decodeAndConvert_base64String(b64_str, False))
    #window.write_event_value('-THREAD-', '*** The thread says.... "I am finished" **window[key].update(data=decodeAndConvert_base64String(b64_str, False))*')


def long_operation_thread(seconds, window, key, inst):
    """
    A worker thread that communicates with the GUI through a global message variable
    This thread can block for as long as it wants and the GUI will not be affected
    :param seconds: (int) How long to sleep, the ultimate blocking call
    """
    progress = 0
    print('Thread started - will sleep for {} seconds'.format(seconds))
    inst.write('SAVE:IMAGE:FILEF png')
    while True:
        #window[key].update(data=decodeAndConvert_base64String(fetch_base64Image(inst, False), False))
        window[key].update(data = frame(inst))
        #window.write_event_value(key, decodeAndConvert_base64String(fetch_base64Image(inst, False), False))
        # progress += 100 / (seconds * 10)
        # window.write_event_value('-PROGRESS-', progress)

    window.write_event_value('-THREAD-', '*** The thread says.... "I am finished" ***')

def the_gui():
    """
    Starts and executes the GUI
    Reads data from a global variable and displays
    Returns when the user exits / closes the window
    """

    sg.theme('Light Brown 3')

    pic = sg.Image(key='Display')

    layout =   [[pic],
                [sg.Text('Long task to perform example')],
              [sg.MLine(size=(80, 12), k='-ML-', reroute_stdout=True,write_only=True, autoscroll=True, auto_refresh=True)],
              [sg.Text('Number of seconds your task will take'),
               sg.Input(key='-SECONDS-', focus=True, size=(5, 1)),
               sg.Button('Do Long Task', bind_return_key=True),
               sg.CBox('ONE chunk, cannot break apart', key='-ONE CHUNK-')],
              [sg.Text('Work progress'), sg.ProgressBar(100, size=(20, 20), orientation='h', key='-PROG-')],
              [sg.Button('Click Me'), sg.Button('Exit')], ]

    window = sg.Window('Multithreaded Demonstration Window', layout, finalize=True)
    updateScreen(scope, 'Display', window)

    timeout = thread = None
    # --------------------- EVENT LOOP ---------------------
    while True:
        event, values = window.read(timeout=timeout)
        # print(event, values)
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event.startswith('Do') and not thread:
            print('Thread Starting! Long work....sending value of {} seconds'.format(float(values['-SECONDS-'])))
            timeout = 100 if values['-ONE CHUNK-'] else None
            thread = threading.Thread(target=long_operation_thread, args=(float(values['-SECONDS-']),window, 'Display', scope), daemon=True)
            thread.start()
            if values['-ONE CHUNK-']:
                sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white', time_between_frames=100)
        elif event == 'Click Me':
            print('Your GUI is alive and well')
        elif event == '-PROGRESS-':
            if not values['-ONE CHUNK-']:
                window['-PROG-'].update_bar(values[event], 100)
        elif event == '-THREAD-':            # Thread has completed
            thread.join(timeout=0)
            print('Thread finished')
            sg.popup_animated(None)                     # stop animination in case one is running
            thread, message, progress, timeout = None, '', 0, None     # reset variables for next run
            window['-PROG-'].update_bar(0,0)            # clear the progress bar
        if values['-ONE CHUNK-'] and thread is not None:
            sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white', time_between_frames=100)
    window.close()


if __name__ == '__main__':
    rm = visa.ResourceManager()
    scope = selectScope()
    initializeScope(scope)
    the_gui()
    print('Exiting Program')
