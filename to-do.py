import sys
import mss
import mss.tools
import PySimpleGUI as sg
from io import BytesIO
import win32clipboard
from PIL import Image
import xlsxwriter as xw
import pretty_errors

output_list = []
output_index = 0

spreadsheet_dict = {
    f"{sys.argv[7]}": {
        "images": [],
        "coordinates": [(0,0)],
        "label": [f'{sys.argv[6]}']
    }
}


def send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard() #https://stackoverflow.com/questions/34322132/copy-image-to-clipboard
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()

def screenshot(monitor, output_list, output_index): #it's best to think of this as an int function with void subroutines...only makes sense in Pythonlandia
    output_list.append("sct-mon{mon}_{top}x{left}_{width}x{height}_{index}.png".format(**monitor))
    sct_img = sct.grab(monitor)
    mss.tools.to_png(sct_img.rgb, sct_img.size, output=output_list[output_index])
    output_index += 1
    return output_index

def newSheet(d, im, xy, label, title):
    d[title] = {
        "images": [im],
        "coordinates": [xy],
        "label": [label]
    }

def updateSheet(d, im, xy, label, title):    
    d[title]["images"].append(im)
    d[title]["coordinates"].append( (d[title]["coordinates"][-1][0]+xy[0],d[title]["coordinates"][-1][1]+xy[1]) )
    d[title]["label"].append(label)

def saveSpreadsheet(d):
    workbook = xw.Workbook('WIP.xlsx')
    for k in d.keys():
        worksheet = workbook.add_worksheet(k)
        for n in range(0, len(d[k]['label'])-1):
            worksheet.insert_image(d[k]['coordinates'][n][0], d[k]['coordinates'][n][1], d[k]['images'][n])
            worksheet.write_string(d[k]['coordinates'][n][0], d[k]['coordinates'][n][1]+32, d[k]['label'][n])
    workbook.close()



with mss.mss() as sct:

    # Get information of monitor 
    monitor_number = int(sys.argv[1])
    mon = sct.monitors[monitor_number]

    # The screen part to capture
    monitor = {
        "top": mon["top"] + int(sys.argv[2]),  # px from the top
        "left": mon["left"] + int(sys.argv[3]),  # px from the left
        "width": int(sys.argv[4]),
        "height": int(sys.argv[5]),
        "mon": monitor_number,
        "index": output_index
    }

    output_index = screenshot(monitor, output_list, output_index)
    monitor['index'] = output_index
    spreadsheet_dict[f'{sys.argv[7]}']["images"].append(output_list[0])
    image_elem = sg.Image(filename=output_list[0])
    

layout = [
        [sg.Button('Copy to clipboard'), sg.Button('Early Export')],
        [image_elem],
        [sg.Button('Screenshot'), sg.Button('Skip'), sg.Button('New Sheet')],
        [sg.Text('Spreadsheet attributes:'), sg.Text('X'), sg.InputText('0', key='-X-'), sg.Text('Y'), sg.InputText('0', key='-Y-'), sg.Text('Sheet Label'), sg.InputText(f'{sys.argv[6]}', key='-Image Label-'), sg.Text('Sheet Label'), sg.InputText(f'{sys.argv[7]}', key='-Sheet Label-')],
        [sg.Text('X offset'), sg.InputText('0', key='-X offset-'), sg.Text('Y offset'), sg.InputText('31', key='-Y offset-'), sg.Text('(Note: offset is the value each screenshot is placed away from the previous image)')]
]

# Create the Window
window = sg.Window('Window Title', layout)

#initialize spreadsheet
#workbook = xw.Workbook('tentative.xlsx')
#worksheet = workbook.add_worksheet[sheet]

label = f'{sys.argv[6]}'
sheet = f'{sys.argv[7]}'
sheets = [sheet]

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    print(spreadsheet_dict)

    if event in (None, 'Cancel'):   # if user closes window or clicks cancel
        print(spreadsheet_dict)
        break

    if values['-Sheet Label-'] in sheets:
        flag = False
    else:
        flag = True
        sheets.append(values['-Sheet Label-'])

    label = values['-Image Label-']
    sheet = values['-Sheet Label-']

    if event == 'Copy to clipboard':
        image = Image.open(output_list[output_index])
        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()

        send_to_clipboard(win32clipboard.CF_DIB, data)

    if event == 'Screenshot':
        output_index = screenshot(monitor, output_list, output_index)
        monitor['index'] = output_index
        image_elem.Update(output_list[output_index-1])
        
        #save to spreadsheet goes here
        #def updateSheet(d, im, xy, label, title)
        updateSheet(spreadsheet_dict, output_list[output_index-1], (float(values['-X-']) + float(values['-X offset-']) , float(values['-Y-']) + float(values['-Y offset-'])), label, sheet)

    if event == 'New Sheet':
        newSheet(spreadsheet_dict, output_list[output_index-1], (float(values['-X-']) + float(values['-X offset-']) , float(values['-Y-']) + float(values['-Y offset-'])), label, sheet)
        print(f'{values["-Sheet Label-"]} set')

    if event == 'Next':
        output_index = screenshot(monitor, output_list, output_index)
        monitor['index'] = output_index
        image_elem.Update(output_list[output_index]-1)

    if event == 'Early Export':
        saveSpreadsheet(spreadsheet_dict)


window.close()
