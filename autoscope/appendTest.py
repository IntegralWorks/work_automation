from PIL import Image
import io
import xlsxwriter as excel
import datetime as dt
import numpy

l = []

def imageAppender(l):
    data = io.BytesIO()
    image = Image.open('tmp.png')
    image.save(data, format='png')
    l.append(data)

def generateRandomImage():
    data = io.BytesIO()
    imarray = numpy.random.rand(100,100,3) * 255
    im = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
    im.save('result.png')
    image = Image.open('result.png')
    image.save(data, format='png')
    return data

def generateSpreadsheet(l):
    timestamp = f'{dt.datetime.now().strftime("%x")}_{dt.datetime.now().strftime("%X")}'
    timestamp = timestamp.replace(":","-").replace("/","-")
    workbook = excel.Workbook(timestamp+'.xlsx')
    worksheet = workbook.add_worksheet('Sheet1')
    x = 1
    y = 1
    for i in l:
        worksheet.insert_image(x,y,'dummy.png', {'image_data' : i})
        x += 20
        if x >= 61:
            y += 3
            x = 1
    workbook.close()
        

imageAppender(l)
for i in range(0,10):
    l.append(generateRandomImage())
generateSpreadsheet(l)
