import sys,os
import mss #screenshot library
import mss.tools
import PySimpleGUI as sg
import win32clipboard
from PIL import Image
import io
import matplotlib
matplotlib.use('Cairo') #resolves backend performance issues
import matplotlib.pyplot as plt
import xlsxwriter as excel
import string
import datetime as dt
import pretty_errors

#py something.py 2 201 320 800 480 Sheet1 Label1 //for the validation lab
#py something.py 2 201 275 800 480 Sheet1 Label1 //for the CPN lab

def send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard() #https://stackoverflow.com/questions/34322132/copy-image-to-clipboard
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()

with mss.mss() as sct:
    # Get information of monitor n
    monitor_number = int(sys.argv[1])
    mon = sct.monitors[monitor_number]

    # The screen part to capture
    monitor = {
        "top": mon["top"] + int(sys.argv[2]),  # px from the top
        "left": mon["left"] + int(sys.argv[3]),  # px from the left
        "width": int(sys.argv[4]),
        "height": int(sys.argv[5]),
        "mon": monitor_number,
    }
    
    pic = sg.Image('welcome.png')

    layout = [ [sg.Button('Copy to Clipboard'), sg.Button('Export')], 
            [pic], 
            [sg.Button('Screenshot'), sg.Button('Next')],
            [sg.Button('Change Sheet Label'), sg.InputText(f'{sys.argv[6]}', key='-Sheet Label-', size=(15,1)), sg.Button('Change Image Label'), sg.Button('Change and Screenshot'), sg.InputText(f'{sys.argv[7]}', key='-Image Label-', size=(40,1))],
            [sg.Text('Note: The following characters are forbidden: []:*?/\\')] ]
            #[sg.Text('Column', size=(15, 1)), sg.Spin(values=[i for i in range(1, 1000)], initial_value=1, size=(6, 1))] ]

    window = sg.Window('Window Title', layout)

    sheet = sys.argv[6] #starting sheet value
    sheets = {}
    sheets[sheet] = []  #images go here -- new sheet? new set of images
    label = sys.argv[7] #starting label value

    def screenshot(label='Sample', sheet = sys.argv[6], keep = True):
        sct_img = sct.grab(monitor)
        mss.tools.to_png(sct_img.rgb, sct_img.size, output='tmp.png')
        if keep:
            plt.imshow(Image.open('tmp.png'))
            plt.axis('off')
            plt.text(378, 30, label, size=5, rotation=0,
             ha="center", va="center",
             bbox=dict(boxstyle="round",
                       ec=(1., 0.5, 0.5),
                       fc=(1., 0.8, 0.8),
                       )
             )
            pic = io.BytesIO()
            plt.savefig(pic, pad_inches = 0, bbox_inches = 'tight', format='png', dpi=400)
            sheets[sheet].append(pic)
            plt.close()

    def export(label = 0):
        try:
            sheets[sys.argv[6]][0]
        except IndexError:
            sg.Popup('Data not found--take a screenshot first')
            return

        filename = 'dummy.png'
        timestamp = f'{dt.datetime.now().strftime("%x")}_{dt.datetime.now().strftime("%X")}'
        timestamp = timestamp.replace(":","-").replace("/","-")
        workbook = excel.Workbook(timestamp+'.xlsx')
        for k in sheets.keys():
            worksheet = workbook.add_worksheet(k)
            counter = 0
            index = 0
            column = 0
            alphabet = list(string.ascii_uppercase)
            for i in sheets[k]:
                #worksheet.insert_image(f'{alphabet[index]}{counter}', filename, {'image_data' : i})
                worksheet.insert_image(counter, column, filename, {'image_data' : i})
                counter += 60
                if counter > 179:
                    column += 32
                    counter = 0
        workbook.close()


    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):   # if user closes window or clicks cancel
            try:
                os.remove('tmp.png')
            except FileNotFoundError:
                pass
            break

        if event == 'Copy to Clipboard':
            try:
                image = Image.open('tmp.png')
                output = io.BytesIO()
                image.convert("RGB").save(output, "BMP")
                data = output.getvalue()[14:]
                output.close()
                send_to_clipboard(win32clipboard.CF_DIB, data)
            except FileNotFoundError:
                sg.Popup('Data not found--take a screenshot first')

        if event == 'Export':
            export()

        if event == 'Screenshot':
            screenshot(label, sheet, keep = True)
            pic.Update('tmp.png')

        if event == 'Next':
            screenshot(keep = False)
            pic.Update('tmp.png')

        if event == 'Change Image Label':
            label = values['-Image Label-']
            print(label)
        if event == 'Change and Screenshot':
            label = values['-Image Label-']
            print(label)
            screenshot(label, sheet, keep = True)
            pic.Update('tmp.png')
        if event == 'Change Sheet Label':
            sheet = values['-Sheet Label-'] 
            sheets[sheet] = []
            print(sheet)
