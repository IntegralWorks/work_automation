import mss #screenshot library
import mss.tools
import os #standard library, OS calls
from time import sleep #standard library, implements delay
from PIL import Image #loads images
from PIL import ImageOps #inverts them
import shutil #for moving files
import moviepy.editor as mp #for converting gif to mp4

def makeDirectory(): #returns string (of directory name)
    print("please run this script from where you want to save the screenshots. ")
    name = input("type folder name, e.g. CN107; this will also be the base name of the screenshots\n")
    directory = os.getcwd() + "\\" + name #becomes C:\~\dir\name
    os.mkdir(directory)
    return directory,name

def takeScreenshot(directory,name): #takes in String directory as argument returns list
    num = int(input("Type in how many screenshots you want to take\n"))
    delay = float(input("Type in how many milliseconds of delay you want between screenshots\n"))

    print("this is a debug message. directory is: " + directory + ".\n")
    print("this is a debug message. name is : " + name + "\n")

    delay = delay / 1000

    with mss.mss() as sct:
        # Get information of monitor n
        monitor_number = 1
        mon = sct.monitors[monitor_number]

        # The screen part to capture
        monitor = {
            "top": mon["top"] + 150,  # 150px from the top
            "left": mon["left"] + 300,  # 300px from the left
            "width": 840,
            "height": 530,
            "mon": monitor_number,
        }

        outputs = [0] * num
        im_gif = Image.new('RGB', (monitor["width"], monitor["height"]))
        gif_Array = []
        

        for i in range(0,num):
            iter_str = str(i) + "_"
            outputs[i] = iter_str + name + ".png".format(**monitor)
            ###outputs[i] = iter_str + name + "sct-mon{mon}_{top}x{left}_{width}x{height}.png".format(**monitor)
            sct_img = sct.grab(monitor)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=outputs[i])
            print(outputs[i] + "\n")
            shutil.move(os.getcwd() + "\\" + outputs[i], directory)
            if i>0:
                im = Image.open(directory + "\\" + outputs[i-1])
                gif_Array.append(im)
                im_inv = ImageOps.invert(im)
                im_inv.save("INV_" + outputs[i-1])
                shutil.move(os.getcwd() + "\\" + "INV_" + outputs[i-1], directory)
            if i==num:
                im = Image.open(directory + "\\" + outputs[i-1])
                gif_Array.append(im)
                im_inv = ImageOps.invert(im)
                im_inv.save("INV_" + outputs[i-1])
                shutil.move(os.getcwd() + "\\" + "INV_" + outputs[i-1], directory)
                #catching up 
            sleep(delay)

        im = Image.open(directory + "\\" + outputs[i])
        gif_Array.append(im)
        im_inv = ImageOps.invert(im)
        im_inv.save("INV_" + outputs[i])
        shutil.move(os.getcwd() + "\\" + "INV_" + outputs[i], directory)
        im_gif.save(directory + "\\" + name + '.gif', save_all=True, append_images=[i for i in gif_Array])
        clip = mp.VideoFileClip(directory + "\\" + name + '.gif')
        clip.write_videofile(directory + "\\" + name + '.mp4')
        print("Finished!")

hackyTuple = makeDirectory()
takeScreenshot(hackyTuple[0],hackyTuple[1])
