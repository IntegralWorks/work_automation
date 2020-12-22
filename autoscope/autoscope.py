import pyvisa as visa
import PySimpleGUI as sg
import re, io, sys, os
import win32clipboard
from PIL import Image
import xlsxwriter as excel
import datetime as dt
import string
import pretty_errors

def send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard() #https://stackoverflow.com/questions/34322132/copy-image-to-clipboard
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()

rm = visa.ResourceManager()
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
    scope.write(rf'message:show "Welcome!"')
    return scope

scope = selectScope()

def fetchImage(inst=scope):
    inst.write('SAVE:IMAGE:FILEF png')
    inst.write('HARDCOPY START')
    raw_data = inst.read_raw()
    im = Image.open(io.BytesIO(raw_data))
    im.save("tmp.png")
    im.close()
    #pic = io.BytesIO()

fetchImage()
placeholder = Image.new('RGB',(1,1), (255, 255, 255))
placeholder.save('tmp2.png')
pic = sg.Image('tmp.png',key='Display')
scaling_view = sg.Image('tmp2.png',key='sc_view')
channel_view = sg.Image('tmp2.png',key='ch_view')

sheet = 'Sheet1' #starting sheet value
sheets = {}
sheets[sheet] = []  #images go here -- new sheet? new set of images
label = 'Welcome!' #starting label value

def imageAppender(l):
    data = io.BytesIO()
    image = Image.open('tmp.png')
    image.save(data, format='png')
    l.append(data)

def screenshot(sheet='Sheet1', keep = True):
    fetchImage()
    pic.Update('tmp.png')
    if keep:
        imageAppender(sheets[sheet])

def export(label = 0):
    try:
        sheets[sheet]
    except IndexError:
        sg.Popup('Data not found--take a screenshot first')
        return
    timestamp = f'{dt.datetime.now().strftime("%x")}_{dt.datetime.now().strftime("%X")}'
    timestamp = timestamp.replace(":","-").replace("/","-")
    workbook = excel.Workbook(timestamp+'.xlsx')
    for k in sheets.keys():
        worksheet = workbook.add_worksheet(k)
        x = 0
        y = 0
        alphabet = list(string.ascii_uppercase)
        for i in sheets[k]:
            #worksheet.insert_image(f'{alphabet[index]}{counter}', filename, {'image_data' : i})
            worksheet.insert_image(x, y, 'dummy.png', {'image_data' : i})
            x += 26
            if x >= 78:
                y += 14
                x = 0
    workbook.close()


def fetchLabelMenu():
    l = []
    scope.write('select:CH1 0')
    scope.write('select:CH1 1')
    fetchImage()
    image = Image.open('tmp.png')
    im = image.crop((17, 419, 343, 459))
    im.save('tmp2.png')
    image.close()
    im.close()
    scaling_view.update('tmp2.png')
    scope.write('fpanel:press CH1')
    scope.write('fpanel:press BMENU5')
    fetchImage()
    image = Image.open('tmp.png')
    im = image.crop((41,188,518,337))
    im.save('tmp3.png')
    channel_view.update('tmp3.png')
    scope.write('clearmenu')
    scope.write('clearmenu')

tab1_layout = [[sg.Button('Copy to Clipboard'), sg.Button('Export')],
        [pic],
        [sg.Button('Screenshot'), sg.Button('Next')],
        [sg.Button('Change Sheet Label'), sg.InputText(f'', key='-Sheet Label-', size=(15,1)), sg.Button('Change Image Label And Screenshot'), sg.InputText(f'', key='-Image Label-', size=(35,1))],
        [sg.Text('Note: The following characters are forbidden: []:*?/\\')]]

tab2_layout =  [[]]

window_elems = {}
for i in range(1,5):
    tab2_layout += [sg.Text(f'CH{i} Label.    '), sg.In(key=f'CH{i}_Label')],
    tab2_layout += [sg.Text(f'CH{i} Scaling. '), sg.In(key=f'CH{i}_Scaling')],
tab2_layout += [[sg.Button('Apply Changes'), sg.Button('Fetch Current Settings'), sg.Button('Exit')]]
tab2_layout += [[scaling_view]]
tab2_layout += [[channel_view]]

layout = [[sg.TabGroup([[sg.Tab('Image Capture', tab1_layout),sg.Tab('Set Labels and Scaling', tab2_layout)]])]]
window = sg.Window('Window Title', layout)

for i in range(1,5):
    window_elems[f'CH{i}_Label'] = window.Element(f'CH{i}_Label')
    window_elems[f'CH{i}_Scaling'] = window.Element(f'CH{i}_Scaling')

while True:
    event, values = window.read()
    if event in (None, 'Cancel'):   # if user closes window or clicks cancel
        try:
            os.remove('tmp.png')
            os.remove('tmp2.png')
            os.remove('tmp3.png')
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
        screenshot(sheet, keep = True)
        pic.Update('tmp.png')

    if event == 'Next':
        screenshot(keep = False)
        pic.Update('tmp.png')

    if event == 'Change Image Label And Screenshot':
        label = values['-Image Label-']
        scope.write(rf'message:show "{label}"')
        screenshot(sheet, keep = True)
        pic.Update('tmp.png')

    if event == 'Change Sheet Label':
        if values['-Sheet Label-'] == '':
            values['-Sheet Label-'] = 'empty'
        sheet = values['-Sheet Label-'] 
        sheets[sheet] = []
        print(sheet)

    if event == 'Apply Changes':
        for i in range(1,5):
            label = values[f'CH{i}_Label']
            scaling = values[f'CH{i}_Scaling']
            scope.write(rf'CH{i}:label "{label}"')
            scope.write(f'CH{i}:scale {scaling}')
        fetchLabelMenu()

    if event == 'Fetch Current Settings':
        for i in range(1,5):
            window_elems[f'CH{i}_Label'].update(scope.query(f'ch{i}:label?').replace('\n','').replace(r'"',''))
            window_elems[f'CH{i}_Scaling'].update(scope.query(f'ch{i}:scale?').replace('\n',''))
        fetchLabelMenu()
    print(values)
    print(window_elems)
