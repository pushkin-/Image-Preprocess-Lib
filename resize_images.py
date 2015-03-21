"""
Give it a directory with images, a directory to put the resized images in, and a size.
If the image already fits the aspect ratio, it will automatically resize it and move on.
Otherwise, you draw (by clicking) a bounding box around the part you want to keep (for the sake of preventing distortion).

You can click outside of the image (in the white space) to remove the box. When you press the enter key to go on to the next image, if no bounding box is detected,
the image will be skipped. Otherwise it will save the image.

Press 'q' to close out of the application.

Optionally, you can tell it to print how many images are left after every 'i'th image. Keeps you posted and maintains your sanity.
Have fun.

Usage:
$ python resize_images.py images_dir output_dir 800,600 {-status 5}
"""

from PIL import Image
import pylab as pl
import os

files = [] # list of images
save_target = '' # where to save resized images to
size = (0, 0) # desired size
print_after = 0 # status; if print_after = i, prints # of remaining images every ith image

img = 0
x = -1
y = -1
points = 0

done = False
quit = False

"""
Start the resizing operation.
"""
def start():
    global files
    global size
    global save_target
    global img
    global img_name

    complete = 0 # images resized
    viewed = 0 # images viewed
    total = len(files)
    w_c = size[0]
    h_c = size[1]

    for i in range(total):
        if print_after > 0 and i % print_after == 0:
            print '%d images left' % (total-1-i)

        reset()

        # get the image and size
        f = files[i]
        img = Image.open(f)
        img_name = os.path.basename(f)

        w = float(img.size[0])
        h = float(img.size[1])

        tol = 1e-3
        ratio_c = w_c/h_c
        ratio = float(w)/h
        if ratio_c-tol <= ratio <= ratio_c+tol: # already correct aspect ratio
            # resize and save
            img = img.resize(size, Image.ANTIALIAS)
            img.save(os.path.normpath(save_target + '/' + img_name))
            continue

        img.thumbnail((size[0]*2, size[1]*2), Image.ANTIALIAS) # resize, keeping aspect ratio
        w = img.size[0]
        h = img.size[1]

        if h_c*w/h < w_c+tol:
            h = int(w_c*h/w)
            w = int(w_c)

        else:
            w = int(h_c*w/h)
            h = int(h_c)

        img = img.resize((w, h), Image.ANTIALIAS) # one of the dimensions will match up perfectly - either w == size[0] or h == size[1]

        fig = pl.figure()
        redraw()

        # bind listeners
        fig.canvas.mpl_connect('button_press_event', onclick)
        fig.canvas.mpl_connect('key_press_event', onkey)

        pl.show()

        flag = True
        while flag: # ughh, I don't like this loop
            if done: flag = False
            if quit: return

        if isinstance(points, list):
            if len(points) > 0:
                img = img.crop((points[0], points[1], points[2], points[3]))
                if img.size[0] != w_c or img.size[1] != h_c: # just in case
                    img = img.resize(size, Image.ANTIALIAS)

                # save resized image
                img.save(os.path.normpath(save_target + '/' + img_name))
                complete += 1

        viewed += 1

    print 'cropped %d%% of images' % (complete*100./total)

"""
Reset the parameters.
"""
def reset():
    global x
    global y
    global points
    global done

    x = -1
    y = -1
    points = 0
    done = False

"""
Trigger to break out of loop and save the image (if all N points are valid).
"""
def save():
    global points
    global done

    for n in points:
        if n < 0:
            points = [] 
            done = True
            return

    done = True
 
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
Listen for enter (next image) and 'q' (quit).
"""
def onkey(e):
    global quit

    if e.key == 'enter':
        save()
        pl.close()

    elif e.key == 'q':
        quit = True
        pl.close()

"""
Draw the image with the bounding box.
"""
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
        pl.plot([left, right], [top, top], 'r')
        pl.plot([left, right], [bottom, bottom], 'r')
        pl.plot([left, left], [bottom, top], 'r')
        pl.plot([right, right], [bottom, top], 'r')

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
