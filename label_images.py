"""
Give it a directory with images, a file for writing labels, and the number of points.
Click on the image to place a point. The next click will place the next point until you reach the total number of points you want.
You can toggle individual points by pressing the number keys (1, 2, ..., 0), but keep in the mind, this will turn of the automation mentioned above.
Clicking outside of the image will remove whichever point if currently toggled.

Pressing 'enter' will move on to the next image.
If all num_points are there, it will record the labels (id 110,200 4,5) <- for num_points = 2.
Otherwise, it will ignore the image. So if you decide not to use the current image, just press 'enter' without selecting any points.

Press 'q' to close out of the application.

Options:
    -i N           will display every Nth image. Useful when labeling sequentual frames; lets you just label every Nth frame
    -s N          size of points (1-10)
    -status N   prints how many images are left after every 'N'th image
    -o N          if 1, overwrite the output file, else append (default)
    -f N           if 1, use the filename as the index (first column of output file), else use an index (default)

Usage:
$ python label_images.py images_dir output_file 5 {-status 5} {-i 10} {-s 5} {-o 1} {-f 1}
"""

from PIL import Image
import pylab as pl
import os

files = [] # list of images
save_target = '' # output file with labels
N = 0 # how many labels (points) to record

points = 0
img = 0
ms = 3 # size of point [1-10]
xL = 0
yL = 0

cur_point = 0 # current point (1-N), or 0 by default
print_after = 0 # status; if print_after = i, prints # of remaining images every ith image

iD = 0 # the current id for the row
inc = 1 # go through every "inc"th image - inc = 1 means go through every image
id_is_filename = False # False means use "iD" to the name column, else use the name of the image
overwrite = 'a+'

step = 5 # by how much to shift point when arrow keys are pressed

done = False
quit = False
automate = True # automatically goes to the next point after click unless you toggle a point

"""
Start labeling images
"""
def start():
    global img
    global iD

    count = 0
    total = len(files)
    labels_file = open(save_target, overwrite)
    for i in range(total):
        if print_after > 0 and i % print_after == 0:
            print total-1-i

        reset()

        # get image
        f = files[i]
        img = Image.open(f)

        fig = pl.figure()
        pl.imshow(img, cmap='gray')

        redraw()

        # bind listeners
        fig.canvas.mpl_connect('button_press_event', onclick)
        fig.canvas.mpl_connect('key_press_event', onkey)

        pl.show()

        flag = True
        while flag:
            if done: flag = False
            if quit:
                labels_file.close()
                return

        if isinstance(points, list):
            if not points:
                continue

            var = 0 # used in the "name" column to identify the row
            if id_is_filename: var = os.path.basename(f)[:f.rfind('.')]
            else: var = str(iD)
                
            line = '%s %s\n' % (var, ' '.join(str(elem) for elem in points))
            labels_file.write(line)

            iD += inc
            count += 1

    print 'filled out %d%%' % (count*100./total)
    labels_file.close()

"""
Reset the parameters.
"""
def reset():
    global cur_point
    global xL
    global yL
    global points
    global done
    global automate

    cur_point = 0
    xL = [-1]*N
    yL = [-1]*N
    points = 0
    automate = True
    done = False

"""
Trigger to escape loop and prepare to save the image (if the points are valid)
"""
def save(p):
    global points
    global done

    for n in p:
        if n < 0:
            points = []
            done = True
            return

    points = list(p)
    done = True

"""
Get the point and redraw.
"""
def onclick( e):
    global cur_point
    global xL
    global yL

    if automate:
        cur_point += 1

    if cur_point < 1 or cur_point > N: return

    x = e.xdata
    y = e.ydata
    if x != None and y != None:
        xL[cur_point-1] = x
        yL[cur_point-1] = y
        redraw()

"""
Save and go to the next image, quit, move point with arrow keys, and toggle individual points.
"""
def onkey(e):
    global quit
    global xL
    global yL
    global automate
    global cur_point

    if e.key == 'enter': # save and move on
        points = []
        for i in range(N):
            points.append(xL[i])
            points.append(yL[i])
        save(points)
        pl.close()

    elif e.key == 'q': # quit
        quit = True
        pl.close()

    elif e.key == 'up':
        yL[cur_point-1] -= step
        redraw()

    elif e.key == 'down':
        yL[cur_point-1] += step
        redraw()

    elif e.key == 'right':
        xL[cur_point-1] += step
        redraw()

    elif e.key == 'left':
        xL[cur_point-1] -= step
        redraw()
        
    else: # toggle points with numbers
        key = toint(e.key)
        if key < 1 or key > N: # for now, can't toggle Nth point if N > 10 - not enough keys!
            key = 0
        else: # when toggle, don't automate
            automate = False

        cur_point = key

"""
Draw the image with the points
"""
def redraw():
    newX = []
    newY = []
    for i in range(N):
        if xL[i] < 0 or yL[i] < 0: continue
        newX.append(xL[i])
        newY.append(yL[i])

    pl.clf()
    pl.imshow(img, cmap='gray')
    pl.plot(newX,newY,'bo',ms=ms)
    pl.draw()

def toint(s):
    try: return int(s)
    except: return 0

def main():
    import re
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs=2, help='input and output directories')
    parser.add_argument('N', type=int, help='number of points to label for each image')
    parser.add_argument('-i', type=int, dest='inc', default=1, const=1, nargs='?', help='displays every ith image') # if data consists of a bunch of sequentual frames, might be useful to skip several to reduce redundancies
    parser.add_argument('-status', type=int, dest='print_after', default=0, const=0, nargs='?', help='displays how many images are left to process after every ith image')
    parser.add_argument('-s', type=int, dest='ms', default=3, const=3, choices=range(1,11), nargs='?', help='specifies size of point (1-10)')
    parser.add_argument('-o', type=int, dest='overwrite', default=0, const=0, choices=[0,1], nargs='?', help='overwrite the file or append to it') # overwrite
    parser.add_argument('-f', type=int, dest='id_is_filename', default=0, const=0, choices=[0,1], nargs='?', help='if 0, will use integer ids for each row; if 1, will use the filename as the id')
    args = parser.parse_args()

    # get source and destination files
    global save_target
    img_path = os.path.normpath(args.files[0])
    save_target = args.files[1]

    global N
    N = args.N

    # get the images
    global files
    for entry in os.listdir(img_path):
        files.append(os.path.join(img_path, entry))

    # set size of point
    global ms
    ms = args.ms

    # get increment
    global inc
    inc = args.inc

    # overwite output file or no (default 'a+')
    global overwrite
    if args.overwrite:
        overwrite = 'w+'

    # set x and y points
    global xL
    global yL
    xL = [-1]*N
    yL = [-1]*N

    # print_after
    global print_after
    print_after = args.print_after

    # id_is_filename
    global id_is_filename
    id_is_filename = args.id_is_filename

    # find the starting index if the id (in the "name" column) is not the filename
    if not id_is_filename:
        global iD
        line = ''
        with open(save_target, 'r') as f:
            for line in f:
                pass

            # extract the last number and set iD to next one
            i = line.find(' ')
            if i  > 0:
                iD = int(line[:line.find(' ')]) + 1

    start()

if __name__ == '__main__':
    main()
