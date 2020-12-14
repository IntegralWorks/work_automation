import sys,os
import mss #screenshot library
import mss.tools
import PySimpleGUI as sg
import win32clipboard
from PIL import Image
import io
import matplotlib.pyplot as plt
import xlsxwriter as excel

#py something.py 2 201 320 800 480 Sheet1 Label1

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
            [sg.Button('Change Image Label'), sg.InputText(f'{sys.argv[6]}', key='-Image Label-'), sg.Button('Change Sheet Label'), sg.InputText(f'{sys.argv[7]}', key='-Sheet Label-')]]

    window = sg.Window('Window Title', layout)

    images = [[]]
    index = 0
    sheets = [sys.argv[6]] #starting sheet value
    labels = [sys.argv[7]] #starting label value

    def screenshot(index=0, label='Sample', keep = True):
        sct_img = sct.grab(monitor)
        mss.tools.to_png(sct_img.rgb, sct_img.size, output='tmp.png')
        if keep:
            plt.imshow(Image.open('tmp.png'))
            plt.axis('off')

            plt.text(0.6, 0.7, f"{label}", size=50, rotation=15.,
             ha="center", va="center",
             bbox=dict(boxstyle="round",
                       ec=(1., 0.5, 0.5),
                       fc=(1., 0.8, 0.8),
                       )
             )

            
            pic = io.BytesIO()
            plt.savefig(pic, pad_inches = 0, bbox_inches = 'tight', format='png')
            images[index].append(pic)

    def export(index = 0):
        try:
            image[0][0]
        except NameError:
            sg.Popup('Data not found--take a screenshot first')
            return
        counter = 1
        filename = 'dummy.png'
        workbook = excel.Workbook('_'.join(sheets)+'.xlsx')
        for k in sheets:
            worksheet = workbook.add_worksheet(k)
            for i in images[index]:
                worksheet.insert_image(f'A{counter}', filename, {'image_data' : i})
                counter +=31
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
            screenshot(index, labels[index], keep = True)
            pic.Update('tmp.png')

        if event == 'Next':
            screenshot(index, labels[index], keep = False)
            pic.Update('tmp.png')

        if event == 'Change Image Label':
            pass
        if event == 'Change Sheet Label':
            pass
