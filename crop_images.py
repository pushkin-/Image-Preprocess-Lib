from PIL import Image
import pylab as pl
import os
import numpy as np
import cv2 as cv

files = []
save_target = ''
size = (0, 0)
print_after = 0

img = 0
img_name = ''
points = 0
x = -1
y = -1

done = False
quit = False

idx = 0

def start():
    global files
    global size
    global img
    global img_name

    total = len(files)
    w_c = float(size[0])
    h_c = float(size[1])

    for i in range(total):
        f = files[i]
        if print_after > 0 and i % print_after == 0:
            print '%d images left' % (total-1-i)

        reset()

        img = Image.open(f)
        img_name = os.path.basename(f)

        fig = pl.figure()
        redraw()

        fig.canvas.mpl_connect('button_press_event', onclick)
        fig.canvas.mpl_connect('key_press_event', onkey)

        pl.show()

        flag = True
        while flag:
            if done:
                flag = False
            if quit:
                return

        if isinstance(points, list):
            if len(points) == 0:
                continue

            # if (img.size[0] != w_c or img.size[1] != h_c): # just in case
            #     img = img.resize(size, Image.ANTIALIAS)

def reset():
    global x
    global y
    global points 
    global done
    global idx

    x = -1
    y = -1
    points = 0
    done = False
    idx = 0

def done_viewing():
    global done

    if isinstance(points, list):
        done = True

def save():
    global points

    for n in points:
        if n < 0:
            points = []
            return

    if isinstance(points, list):
        #global img
        global idx

        img_c = img.crop((points[0], points[1], points[2], points[3]))
        img_c.save(os.path.normpath(save_target +'/' + str(idx) +'_' + img_name))
        idx += 1

def onclick(e):
    global x
    global y

    x = e.xdata
    y = e.ydata
    if x != None and y != None:
        x = int(x)
        y = int(y)
        redraw()

def onkey(e):
    global x
    global y

    if e.key == 'c':
        global points
        global done

        points = []
        done = True
        pl.close()

    elif e.key == 'enter':
        save()

    elif e.key == 'right':
        w = img.size[0]
        h = img.size[1]

        x += size[0]
        if x > w:
            x = size[0]/2.0
            y += size[1]

        if y > h:
            x -= size[0]
            y -= size[1]
            return

        redraw()

    elif e.key == 'left':
        w = img.size[0]
        h = img.size[1]

        x -= size[0]
        if x < 0:
            x = w
            y -= size[1]

        if y < 0:
            x += 0
            y += 0
            return

        redraw()

    elif e.key == 'q':
        global quit
        quit = True
        pl.close()

def redraw():
    global points
    
    top = -1
    left = -1
    bottom = -1
    right = -1

    w = img.size[0]
    h = img.size[1]

    if x >= 0 and y >= 0 and x <= w and y <= h:
        left = x - size[0]/2.0
        right = x + size[0]/2.0
        top = y - size[1]/2.0
        bottom = y + size[1]/2.0

        if right > w:
            diff = right-w
            right -= diff
            left -= diff

        elif left < 0:
            diff = -1*left
            left = 0
            right += diff

        if top < 0:
            diff = -1*top
            top = 0
            bottom += diff

        elif bottom > h:
            diff = bottom-h
            bottom -= diff
            top -= diff

    points = map(int, [left, top, right, bottom]) # save points every time clicked
    pl.clf()
    pl.imshow(img, cmap='gray')
    space = 30
    pl.xlim([-space,w+space])
    pl.ylim([h+space,-space])

    if top >= 0:
        pl.plot([left, right], [top, top], 'r', ms=10)
        pl.plot([left, right], [bottom, bottom], 'r', ms=10)
        pl.plot([left, left], [bottom, top], 'r', ms=10)
        pl.plot([right, right], [bottom, top], 'r', ms=10)

    pl.draw()

def main():
    import re
    import sys

    # if 4 args passed, last one is print_after
    if len(sys.argv) == 5:
        global print_after
        print_after = sys.argv[-1]
    elif len(sys.argv) != 4:
        print 'USAGE: python crop_images.py pathOfImages pathOfCroppedImages cropSize {printAfter}'
        print 'Ex: python crop_images.py D:\\sourceDirectory D:\\resultDirectory 300,300'
        return

    global save_target
    img_path = os.path.normpath(sys.argv[1])
    save_target = sys.argv[2]

    global files
    for entry in os.listdir(img_path):
        files.append(os.path.join(img_path, entry))

    # add slash at end
    #if save_target[-1] != '/': save_target = save_target + '/'

    global size
    s = sys.argv[3].split(',')
    s = [re.findall('\d+', p) for p in s]
    size = (int(s[0][0]), int(s[1][0]))
    if (not s[0][0] or not s[1][0]):
        print 'Size is invalid: ' + size
        print 'Size should be 2 numbers separated by a comma (no space): (300,300) or 300,300'

    start()

if __name__ == '__main__':
    main()
