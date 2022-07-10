from PIL import Image
from os import listdir
from os.path import isfile, join
from copy import deepcopy
import itertools



def imageondemand(targetfile):
    targetfile = targetfile[63:]
    print(targetfile)
    data = targetfile.split("/")[-1].split(".")[0].split("-")
    role,align,health,ability,alive,active = data

    mypath = r"D:\GitHub\townsquare\src\assets\icons"
    im = Image.open(f'{mypath}\\{role}.png')

    imageBox = im.getbbox()
    im = im.crop(imageBox)
    width, height = im.size
    ratio = width / height

    if width>height:
        width = 350
        height = int(350/ratio)
    else:
        height = 350
        width = int(350*ratio)

    im = im.resize((width, height), Image.ANTIALIAS)

    sqimage = Image.new('RGBA', (500, 500))

    health = Image.open(f'tokenback\\{health}.png')
    health = health.resize((500, 500), Image.ANTIALIAS)
    sqimage.paste(health, (0, 0), health)

    if alive == "dead":
        state = Image.open(f'tokenback\\dead.png')
        state = state.resize((500, 500), Image.ANTIALIAS)
        sqimage.paste(state, (0, 0), state)

    align = Image.open(f'tokenback\\{align}.png')
    align = align.resize((500, 500), Image.ANTIALIAS)
    sqimage.paste(align, (0, 0), align)

    if ability != "noability":
        ability = Image.open(f'tokenback\\{ability}.png')
        ability = ability.resize((500, 500), Image.ANTIALIAS)
        sqimage.paste(ability, (0, 0), ability)

    vpos = int((500 - height) / 2)
    hpos = int((500 - width) / 2)

    if alive == "dead":
        im2 = im.copy()
        im2.putalpha(180)
        im.paste(im2, im)
        sqimage.paste(im, (hpos, vpos), im)

    else:
        sqimage.paste(im, (hpos, vpos), im)

    sqimage = sqimage.resize((200, 200), Image.ANTIALIAS)
    if active == "inactive":
        im2 = sqimage.copy()
        im2.putalpha(127)
        sqimage.paste(im2, sqimage)
        sqimage.paste(sqimage, (0, 0), sqimage)


    fold = r'D:\PyCharm\BOTCwebsite2\app'
    filename = f"{fold}/{targetfile}"


    sqimage.save(filename, quality=85)

def basicimages():
    mypath = r"D:\GitHub\townsquare\src\assets\icons"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    mypath2 = r'D:\PyCharm/BOTCwebsite2/app\static/tokenimgs/'
    made = [f.split(".")[0] for f in listdir(mypath2) if isfile(join(mypath2, f))]
    widest = 0
    tallest = 999

    for i in range(len(onlyfiles)):
        if onlyfiles[i].split(".")[0] in made:
            continue

        im = Image.open(f'{mypath}\\{onlyfiles[i]}')
        imageBox = im.getbbox()
        im = im.crop(imageBox)
        width, height = im.size
        ratio = width/height
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

        filename = f"{mypath2}{role}.webp"

        sqimage = Image.new('RGBA', (350, 350))
        vpos = int((350 - height) / 2)
        hpos = int((350 - width) / 2)
        sqimage.paste(im, (hpos, vpos), im)

        sqimage.save(filename, quality=85)


