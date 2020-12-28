import pyvisa as visa
import PySimpleGUI as sg
import re, sys, os
from io import BytesIO
import win32clipboard
from PIL import Image, ImageTk
import base64
from time import sleep
import xlsxwriter as excel
import datetime as dt
import string
import pretty_errors

clipboard_history = []
def prepare_clipboard_data(pos = -1, img_list = clipboard_history):
    try:
        b64_str = img_list[pos]
    except IndexError:
        sg.popup(f'ERROR: No screenshot data currently present in clipboard history, did you take at least one picture?')
        b64_str = b'iVBORw0KGgoAAAANSUhEUgAAAQkAAADCCAIAAADVUqDwAAAHe0lEQVR4nO3dT0sbaQDH8acmDq4rFXquh6RVegh5C4JapQSEeMi9UEhBvKyHXDx68ZDdgxQaELznEEGQUrWBvoXgoShNXkEFQyphmsgeui2u+UWTmSSTyXw/9GRxHh3zNc/8e3z07elzA6DFmNdfADCkaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQaAPQwn3Z6Nbx43Skt9ts5pJX22e93SZwD943AI02AI02AI02AI02AK0v56mUSj2xfF0a1GiAa7xvABptABptANrAjjeGVXxtcnVl/GUkFP19Ib/SLJvmyfv6YaHR7wOkwY0es1IJ69ViKGpujfVruPKnmw9Hdv6s0cMBH+Ttnu/Ao29Pn/d8o+qekcEdi7eOLu83CacyE+tvrOi92yoXaxtpu5sv29vRxdfTyUC3Rqy/273OO7w3Z9i+d5cCOaeKr01+vnic7eAVE12YOjqeSsX8OHo4lZnqcKBbI05kD558zllxZ2M+xNs936XgtRHPTB/tTHT+cjERK3swlfLZ6Nb+cXdV3Nan16W3e757wWojnMpNH70Jdf+JVjZn+Wb0mLV/MbXk8j7oiJU9mN7qWR7e7nlnAtFG6NmcMcakco+zCw5+PMYYYxam9td8Mbq1fzC15HCYO0Jpt7+2vd3zLgWiDWOMSeWmswutH26Wi/XNZHVm9vLnv0SydlrRW1h6O+l4Fj6o0cNbx+3DqNi5TDWRvPw93MxsNZGp5YrN9hu0ssfOv+ufvN3zLgSjjejb6dbfW+ViLTF7NZ++vn3usnRmv16+TOypl0tkfNXRHGNgo8czf+pHyip2LlOdWa5tFxql/501apQK9nb6ama2utmukMjEbsb5mX5v97w7AWkjcufH0zzNVOfbnyIs7XzPid9hoZcJJ6+SAY0em9yVE/pKPbFc2y7cf+2ikU9fJTJ2Wf1f9M2E45mVt3venWC08X/2ZvLq9UOvle33dutHo1H3+6tfo6c21Cmgbi4rlQq1+YwY1xhr3cVbxy3e7vluDazGyMTRxYTjzz7NXL4u9OTrsDeTtY6ubRXs0x3r7tw9Eo4bNxek+jZ6bHJdzelzf3V5vbVQ21x50np4EF204jsur1V7u+cdCNb7Rsc/HmOMufna+uYeGXsxlKPHE+Otbxrlve8OVp/I79bFzMrtjN/bPe9MgNpo5rr48RhjGudtTpsM3+jh1cXWIw373Y6j+6POrt8VWz/qZsbv7Z53LDBtnGa8XMKnv6PHrJetp6eKdt7p9vIfeznj93bPuxCQNir1f3pzuDKUo8+NtU6oTtXru1MF+7T1g5Gwk4sM3u55VwJ/j/o98ulLx796Bzl6fLZ1QtX8eu5m8JuvFXP3rpPI2AtjBnM07O2e/4Xnxf3vRVS0ce5qGtM4rxhzd54WmosZ48vZkTMBmVONsvBc68FG5eaLu41+Kd9zI0lA0Aag0YbvjT0T7xv9eKb0v5tqA4M2AI02fE9eRXZ0vvUBLs99+Q5tABptjCTXdx/14byw79CG78m7j0Jzrm4N7Mt5Yb+hDf9T1yLcnVOSN2j15dzXMKMN/ytdiOt0SysuludQN2iVyzfON+hLtDECzm/EExcLluMHWVOiq+bJ0UBXBB0CtDECzuwTccjh9EFW+Qhh5cdhsA7EDW2MhsbhJzGtcrQGQnjrb/HcefmTt0vTeoI2RkLp6IdaIqTrRQHbrOLj9BFCf6ON0aAfZDVmYarzhZ/jGb0sZ3mvPgRPUwwebYwKvQZChws/x6ytduvVVuobQXzTML5Zg6fNX3LALWfXG3vj+vUdsbIHT9Yr9sn7+uH57aUNw/G1sdWVP9JtF6vtfhWf0cEzsSOktHO1GRWrS/0UjVjpHSvdzQZ9uwxCTzCnGi35dFWtmenEaabao/XyfIo2Rk1je7n9ws+dauaSlw8tzjnyaGME3bfw84PKxXpiNshTqd9oY0SVCrX52ermXheFlIv1zeTlfDqwB9939OXvxGLIxMKpxMSrxVD07qL/zXLFlCs/Pny080GfQbWiDUBjTgVotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFotAFo/wIpKtrkgIqs5wAAAABJRU5ErkJggg=='
    image = Image.open(BytesIO(base64.b64decode(b64_str)))
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    return (win32clipboard.CF_DIB, data)

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

def fetch_base64Image(inst=scope,placeholder=False):
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

def cropImage(b64_str, coords):
    image = Image.open(BytesIO(base64.b64decode(b64_str)))
    im = image.crop(coords)
    return ImageTk.PhotoImage(im)

pic = sg.Image(key='Display')
scaling_view = sg.Image(key='sc_view')
channel_view = sg.Image(key='ch_view')

sheets = {'Sheet1' : []}
currentSheet = 'Sheet1'
labels = ['Welcome!']
currentLabel = 'Welcome!'
box = scope.query('message:box?').replace('\n','').split(',')
label_xpos = box[0]
label_ypos = box[1]

def screenshot(sheet='Sheet1', keep = True, key = 'Display'):
    b64_str = fetch_base64Image()
    window[key].update(data=b64_str)
    clipboard_history.append(b64_str)
    if keep:
        sheets[sheet].append(b64_str)

def export():
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
            worksheet.insert_image(x, y, 'dummy.png', {'image_data' : decodeAndConvert_base64String(i, True)})
            x += 26
            if x >= 78:
                y += 14
                x = 0
    workbook.close()

def fetchLabelMenu():
    scope.write('select:CH1 0')
    scope.write('select:CH1 1')
    window['sc_view'].update(data = cropImage(fetch_base64Image(),(17, 419, 343, 459)))
    scope.write('fpanel:press CH1')
    scope.write('fpanel:press BMENU5')
    window['ch_view'].update(data = cropImage(fetch_base64Image(),(41,188,518,337)))
    scope.write('clearmenu')
    scope.write('clearmenu')

tab1_layout = [[sg.Button('Copy to Clipboard'), sg.Button('Export')],
        [pic],
        [sg.Button('Screenshot'), sg.Button('Next'), sg.Button('Toggle Label')],
        [sg.Button('Change Sheet Label'), sg.InputText(f'', key='-Sheet Label-', size=(15,1)), sg.Button('Change Image Label And Screenshot'), sg.InputText(f'', key='-Image Label-', size=(35,1))],
        [sg.Button('Adjust Label Position'), sg.In(label_xpos, key='xpos'), sg.In(label_ypos, key='ypos')],
        [sg.Text('Note: The following characters are forbidden: []:*?/\\')]]

tab2_layout =  [[]]

for i in range(1,5):
    tab2_layout += [sg.Text(f'CH{i} Label.    '), sg.In(key=f'CH{i}_Label')],
    tab2_layout += [sg.Text(f'CH{i} Scaling. '), sg.In(key=f'CH{i}_Scaling')],
tab2_layout += [[sg.Button('Apply Changes'), sg.Button('Fetch Current Settings'), sg.Button('Exit')]]
tab2_layout += [[scaling_view]]
tab2_layout += [[channel_view]]
tab2_layout += [[sg.T('Note: Sometimes, "Fetch Current Settings" must be clicked twice.')]]

layout = [[sg.TabGroup([[sg.Tab('Image Capture', tab1_layout),sg.Tab('Set Labels and Scaling', tab2_layout)]])]]
window = sg.Window('Window Title', layout, finalize=True)

window['Display'].update(data = decodeAndConvert_base64String(fetch_base64Image()))
window['sc_view'].update(data = decodeAndConvert_base64String(fetch_base64Image(placeholder=True)))
window['ch_view'].update(data = decodeAndConvert_base64String(fetch_base64Image(placeholder=True)))

while True:
    event, values = window.read()
    if event in (None, 'Cancel'):   # if user closes window or clicks cancel
        break

    if event == 'Copy to Clipboard':
        content = prepare_clipboard_data()
        send_to_clipboard(content[0], content[-1])

    if event == 'Export':
        export()

    if event == 'Screenshot':
        screenshot(currentSheet, keep = True)

    if event == 'Next':
        screenshot(keep = False)
        nextFlag = True

    if event == 'Toggle Label':
        flag = bool(int(scope.query('message:state?').replace('\n','')))
        scope.write(f'message:state {int(not flag)}')
        print(f'flag: {int(flag)} not flag: {int(not flag)}')
        screenshot(keep = False)

    if event == 'Change Image Label And Screenshot':
        currentLabel = values['-Image Label-']
        scope.write(rf'message:show "{currentLabel}"')
        screenshot(currentSheet, keep = True)

    if event == 'Change Sheet Label':
        if values['-Sheet Label-'] == '':
            values['-Sheet Label-'] = 'empty'
            window['-Sheet Label-'].update('empty')
        currentSheet = values['-Sheet Label-'] 
        sheets[currentSheet] = []

    if event == 'Adjust Label Position':
        scope.write(f"message:box {values['xpos']},{values['ypos']}")
        screenshot(keep = False)

    if event == 'Apply Changes':
        for i in range(1,5):
            label = values[f'CH{i}_Label']
            scaling = values[f'CH{i}_Scaling']
            scope.write(rf'CH{i}:label "{label}"')
            scope.write(f'CH{i}:scale {scaling}')
        fetchLabelMenu()

    if event == 'Fetch Current Settings':
        for i in range(1,5):
            window[f'CH{i}_Label'].update(scope.query(f'ch{i}:label?').replace('\n','').replace(r'"',''))
            window[f'CH{i}_Scaling'].update(scope.query(f'ch{i}:scale?').replace('\n',''))
        fetchLabelMenu()
