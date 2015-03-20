from PIL import Image
import pylab as pl
import os

save_target = ''
files = []
N = 0

points = 0
img = 0
ms = 3
xL = 0
yL = 0

cur_point = 0
print_after = 0

iD = 0 # the current id for the row
inc = 1
id_is_filename = False
overwrite = 'a+'

step = 5 # by how much to shift point when arrow keys are pressed

done = False
quit = False
automate = True # automatically goes to the next point after click unless you toggle a point

def start():
    global img
    global iD

    count = 0
    total = len(files)
    labels_file = open(save_target, overwrite)
    for i in range(total):
        f = files[i]
        if print_after > 0 and i % print_after == 0:
            print total-1-i

        reset()

        img = Image.open(f)
        fig = pl.figure()
        pl.imshow(img, cmap='gray')

        redraw()

        fig.canvas.mpl_connect('button_press_event', onclick)
        fig.canvas.mpl_connect('key_press_event', onkey)

        pl.show()

        flag = True
        while flag:
            if done:
                flag = False
            if quit:
                labels_file.close()
                return

        if isinstance(points, list):
            if not points:
                continue

            var = 0
            if id_is_filename: var = os.path.basename(f)[:f.find('.')]
            else: var = str(iD)
                
            line = '%s %s\n' % (var, ' '.join(str(elem) for elem in points))
            labels_file.write(line)

            iD += inc
            count += 1

    print 'filled out %d%%' % (count*100./total)
    labels_file.close()

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

def onkey(e):
    global points
    global quit
    global xL
    global yL
    global automate
    global cur_point

    if e.key == 'enter':
        points = []
        for i in range(N):
            points.append(xL[i])
            points.append(yL[i])
        save(points)
        pl.close()

    elif e.key == 'q':
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
        
    else:
        key = toint(e.key)
        if key < 1 or key > N:
            key = 0
        else:
            automate = False

        cur_point = key

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
    parser.add_argument('files', nargs=3, help='input and output directories and number of labels to track')
    parser.add_argument('-i', type=int, dest='inc', default=1, const=1, nargs='?', help='displays every ith image') # if data consists of a bunch of sequentual frames, might be useful to skip several to reduce redundancies
    parser.add_argument('-status', type=int, dest='print_after', default=0, const=0, nargs='?', help='displays how many images are left to process after every ith image')
    parser.add_argument('-s', type=int, dest='ms', default=3, const=3, choices=range(1,11), nargs='?', help='specifies size of point (1-10)')
    parser.add_argument('-o', type=int, dest='overwrite', default=0, const=0, choices=[0,1], nargs='?', help='overwrite the file or append to it') # overwrite
    parser.add_argument('-f', type=int, dest='id_is_filename', default=0, const=0, choices=[0,1], nargs='?', help='if 0, will use integer ids for each row; if 1, will use the filename as the id')
    # what about indir and outdir
    args = parser.parse_args()
    required_params = args.files

    global save_target
    global N
    img_path = os.path.normpath(required_params[0])
    save_target = required_params[1]
    N = int(required_params[2])

    # get files
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
    xL = [-1]*N
    yL = [-1]*N

    # print_after
    global print_after
    print_after = args.print_after

    # id_is_filename
    global id_is_filename
    id_is_filename = args.id_is_filename

    # find the starting index
    if not id_is_filename:
        global iD
        line = ''
        with open(save_target, 'r') as f:
            for line in f:
                pass

            # extract the last number and set iD to next one
            if line: iD = int(line[:line.find(' ')]) + 1

    start()

if __name__ == '__main__':
    main()