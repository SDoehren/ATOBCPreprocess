from PIL import Image
from os import listdir
from os.path import isfile, join
from copy import deepcopy
import itertools

mypath = r"D:\GitHub\townsquare\src\assets\icons"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

print(onlyfiles)

widest = 0
tallest = 999


first = True

for i in range(len(onlyfiles)):
    im = Image.open(f'{mypath}\\{onlyfiles[i]}')
    imageBox = im.getbbox()
    im = im.crop(imageBox)
    width, height = im.size
    ratio = width/height
    print(im.size, ratio, onlyfiles[i])
    if ratio > widest:
        widest = ratio
    if ratio < tallest:
        tallest = ratio

    if width>height:
        width = 350
        height = int(350/ratio)
    else:
        height = 350
        width = int(350*ratio)

    im = im.resize((width,height), Image.ANTIALIAS)

    role = onlyfiles[i].split(".")[0]

    """vpos = int((500 - height) / 2)
    hpos = int((500 - width) / 2)
    sqimage.paste(im, (hpos, vpos),im)
    sqimage = sqimage.resize((500, 500), Image.ANTIALIAS)"""

    im.save(f"imgs/{role}.png", quality=90)



    #im.show()
    #exit()

print(widest)
print(tallest)