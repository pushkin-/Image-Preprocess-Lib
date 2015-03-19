import sys
from PIL import Image
import pylab as pl
import os
import numpy as np
import cv2 as cv

files = []
save_target = ''
size = (-1, -1)
print_after = 0

img = 0
x = -1
y = -1
points = 0

done = False
quit = False

def start():
    global files
    global size
    global save_target
    global img
    global img_name

    complete = 0
    viewed = 0
    total = len(files)
    w_c = size[0]
    h_c = size[1]

    for i in range(total):
        f = files[i]

        if print_after > 0 and i % print_after == 0:
            print '%d images left' % (total-1-i)

        reset()

        img = Image.open(f)
        w = float(img.size[0])
        h = float(img.size[1])

        img_name = os.path.basename(f)
        tol = 1e-3
        ratio_c = w_c/h_c
        ratio = float(w)/h
        if ratio_c-tol <= ratio <= ratio_c+tol: # correct ratio already
            # resize and save
            img = img.resize(size, Image.ANTIALIAS)
            img.save(os.path.normpath(save_target + '/' + img_name))
            continue

        img.thumbnail((size[0]*2, size[1]*2), Image.ANTIALIAS)
        w = img.size[0]
        h = img.size[1]

        if h_c*w/h < w_c+tol:
            h = int(w_c*h/w)
            w = int(w_c)

        else:
            w = int(h_c*w/h)
            h = int(h_c)

        img = img.resize((w, h), Image.ANTIALIAS)

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
            if len(points) > 0:
                img = img.crop((points[0], points[1], points[2], points[3]))
                if img.size[0] != w_c or img.size[1] != h_c: # just in case
                    img = img.resize(size, Image.ANTIALIAS)

                img.save(os.path.normpath(save_target + '/' + img_name))
                complete += 1

        viewed += 1

    print 'cropped %d%% of images' % (complete*100./total)

def reset():
    global x
    global y
    global points
    global done

    x = -1
    y = -1
    points = 0
    done = False

def save():
    global points
    global done

    for n in points:
        if n < 0:
            points = [] 
            done = True
            return

    done = True
 
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
    global quit

    if e.key == 'enter':
        save()
        pl.close()

    elif e.key == 'q':
        quit = True
        pl.close()

def redraw():
    global img
    global x
    global y
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
        pl.plot([left, right], [top, top], 'r')
        pl.plot([left, right], [bottom, bottom], 'r')
        pl.plot([left, left], [bottom, top], 'r')
        pl.plot([right, right], [bottom, top], 'r')

    pl.draw()

def main():
    import re

    # if 4 args passed, last one is print_after
    if len(sys.argv) == 5:
        global print_after
        print_after = sys.argv[-1]
    elif len(sys.argv) != 4:
        print 'USAGE: python crop_images.py pathOfImages pathOfCroppedImages cropSize {printAfter}'
        print 'Ex: python crop_images.py D:\\sourceDirectory D:\\resultDirectory 300,300'
        return

    img_path = os.path.normpath(sys.argv[1])
    global save_target
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