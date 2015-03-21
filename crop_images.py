"""
Give it a directory with images, a directory to put the cropped images in, and a size.
Click to draw a bounding box of the size you want.

You can click outside of the image (in the white space) to remove the box. When you press the enter key to go on to the next image, if no bounding box is detected,
the image will be skipped. Otherwise it will save the image, but will stay on the current image until you press 'c' to continue.
You can move the box around using the arrow keys - wraps around.

Press 'q' to close out of the application.

Optionally, you can tell it to print how many images are left after every 'i'th image.

If the image's name is test.jpg and you poke it 4 times ('enter' after each poke), the output directory will contain the files:
    0_test.jpg
    1_test.jpg
    2_test.jpg
    3_test.jpg

Usage:
$ python crop_images.py images_dir output_dir 50,50 {-status 5}
"""

from PIL import Image
import pylab as pl
import os

files = [] # list of images
save_target = '' # where to save cropped images to
size = (0, 0) # desired size
print_after = 0 # status; if print_after = i, prints # of remaining images every ith image

img = 0
img_name = ''
points = 0
x = -1
y = -1

done = False
quit = False

idx = 0 # becomes the prefix of the output file (e.g. 0_test.jpg, 1_test.jpg, etc.)

"""
Start the resizing operation.
"""
def start():
    global files
    global size
    global img
    global img_name

    total = len(files)
    w_c = float(size[0])
    h_c = float(size[1])

    for i in range(total):
        if print_after > 0 and i % print_after == 0:
            print '%d images left' % (total-1-i)

        reset()

        # get the image
        f = files[i]
        img = Image.open(f)
        img_name = os.path.basename(f)

        fig = pl.figure()
        redraw()

        # bind listeners
        fig.canvas.mpl_connect('button_press_event', onclick)
        fig.canvas.mpl_connect('key_press_event', onkey)

        pl.show()

        flag = True
        while flag:
            if done: flag = False
            if quit: return

        #if isinstance(points, list):
            #if not points: continue

            #if (img.size[0] != w_c or img.size[1] != h_c): # just in case
                #img = img.resize(size, Image.ANTIALIAS)

"""
Reset the parameters.
"""
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

"""
Saves the cropped image.
"""
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

"""
Get point and redraw.
"""
def onclick(e):
    global x
    global y

    x = e.xdata
    y = e.ydata
    if x != None and y != None:
        x = int(x)
        y = int(y)
        redraw()

"""
Go to next image, save cropped image, or quit.
"""
def onkey(e):
    global x
    global y

    w = img.size[0]
    h = img.size[1]

    if e.key == 'c': # continue
        global points
        global done

        #points = []
        done = True
        pl.close()

    elif e.key == 'enter': # save image
        save()

    # use arrow keys to move box around; will wrap around
    elif e.key == 'right':
        x += size[0]
        if x > w:
            x = size[0]/2.0
            y += size[1]

        if y > h: # if we wrapped past the last row
            x = w
            y = h - size[1]/2

        redraw()

    elif e.key == 'left':
        x -= size[0]
        if x < 0:
            x = w - size[0]/2
            y -= size[1]

        if y < 0:
            x = 0
            y = 0

        redraw()

    elif e.key == 'up':
        y -= size[1]
        if y < 0:
            y = h - size[1]/2
            x += size[0]

        if x > w:
            x = w - size[0]/2
            y = 0

        redraw()

    elif e.key == 'down':
        y += size[1]
        if y > h:
            y = size[1]/2
            x -= size[0]

        if x < 0:
            x = 0
            y = h - size[1]/2

        redraw()

    elif e.key == 'q': # quit
        global quit
        quit = True
        pl.close()

"""
Draw the image with the bounding box.
"""
def redraw():
    global points
    
    top = -1
    left = -1
    bottom = -1
    right = -1

    w = img.size[0]
    h = img.size[1]

    if x >= 0 and y >= 0 and x <= w and y <= h:
        # x,y point is the center of the rectangle; find boundary
        left = x - size[0]/2.0
        right = x + size[0]/2.0
        top = y - size[1]/2.0
        bottom = y + size[1]/2.0

        # make sure it doesn't go outside the frame by shifting the box if necessary
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

    # if you click outside of the image, top will be -1 and no bounding box will be drawn
    if top >= 0:
        pl.plot([left, right], [top, top], 'r', ms=10)
        pl.plot([left, right], [bottom, bottom], 'r', ms=10)
        pl.plot([left, left], [bottom, top], 'r', ms=10)
        pl.plot([right, right], [bottom, top], 'r', ms=10)

    pl.draw()

def main():
    import re
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs=2, help='input and output directories')
    parser.add_argument('size', help='new size')
    parser.add_argument('-status', type=int, dest='print_after', default=0, help='displays how many images are left to process after every ith image')
    args = parser.parse_args()

    # source and destination
    img_path = os.path.normpath(args.files[0])
    global save_target
    save_target = args.files[1]

    # get the images
    global files
    for entry in os.listdir(img_path):
        files.append(os.path.join(img_path, entry))

    # get size
    global size
    s = args.size.split(',')
    s = [re.findall('\d+', p) for p in s] # extract the numbers with regex
    size = (int(s[0][0]), int(s[1][0]))
    if size[0] < 1 or size[1] < 1:
        print 'Size is invalid: ' + size
        print 'Size should be 2 positive integers separated by a comma: (300,300); 300,300; ...'
        return

    # optional print_after
    global print_after
    print_after = args.print_after

    start()

if __name__ == '__main__':
    main()
