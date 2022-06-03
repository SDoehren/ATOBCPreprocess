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

    for pack in list(itertools.product(("good", "evil"), ("healthy", "ill"), ("noability", "unused", "used"),
                                       ("alive", "dead"))):
        filename = f"imgs/{role}-{'-'.join(pack)}.png"
        sqimage = Image.new('RGBA', (500, 500))
        print(filename)

        align = Image.open(f'tokenback\\{pack[1]}.png')
        align = align.resize((500, 500), Image.ANTIALIAS)
        sqimage.paste(align, (0, 0),align)

        if pack[3] == "dead":
            state = Image.open(f'tokenback\\{pack[3]}.png')
            state = state.resize((500, 500), Image.ANTIALIAS)
            sqimage.paste(state, (0, 0),state)

        health = Image.open(f'tokenback\\{pack[0]}.png')
        health = health.resize((500, 500), Image.ANTIALIAS)
        sqimage.paste(health, (0, 0),health)

        if pack[2] != "noability":
            ability = Image.open(f'tokenback\\{pack[2]}.png')
            ability = ability.resize((500, 500), Image.ANTIALIAS)
            sqimage.paste(ability, (0, 0),ability)



        vpos = int((500 - height) / 2)
        hpos = int((500 - width) / 2)
        sqimage.paste(im, (hpos, vpos),im)

        sqimage = sqimage.resize((200, 200), Image.ANTIALIAS)
        sqimage.save(filename, quality=85)



    #im.show()
    #exit()

print(widest)
print(tallest)