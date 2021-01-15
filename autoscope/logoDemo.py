import pyvisa as visa
import PySimpleGUI as sg
import re, sys, os
from io import BytesIO
import win32clipboard
from PIL import Image, ImageTk, ImageFont, ImageDraw, ImageOps
import base64
from time import sleep
import xlsxwriter as excel
import datetime as dt
import string
import pretty_errors
import csv

def gen_logo():
    logo = Image.new("RGBA", (840,400), color = (0,0,0,255))
    draw = ImageDraw.Draw(logo)
    font = ImageFont.truetype("C:\\Users\\redacted\\Documents\\ez-sc\\VISA_rewrite\\base64_rewrite\\TTF\\VictorMono-Italic.ttf", 48)
    draw.text((260, 100), "Welcome to...", (255,255,255,255), font=font)
    logo.show()
gen_logo()
