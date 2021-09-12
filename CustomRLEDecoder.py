import numpy as np
import imageio

import sys
from os.path import isfile
import struct

# Edgard you fucking tryharder bro this is something literally nobody asked for
#top    = [(255, imWidth + 12), (203, 1), (127, 1), (139, 1), (255, 1), (171, 1), (203, 1), (255, 2), (139, 1), (235, 1), (255, 4), (171, 1)]
#center = [(255, 24),  (151, 1), (0, 1),   (23, 1),  (255, 1), (87, 1),  (151, 1), (255, 2), (23, 1),  (215, 1), (255, 4), (87, 1)]
#bottom = [(255, 24),  (229, 1), (191, 1), (197, 1), (255, 1), (213, 1), (229, 1), (255, 2), (197, 1), (245, 1)]

def main(argv):
    ###################################################################
    ######################## START PARAMS READ ########################
    ###################################################################
    if len(argv) != 2:
        print("Usage: barcode_decoder.py <input_file> <output_file>")
        sys.exit(1)
    inBar, outBar = argv[0], argv[1]
    if not isfile(inBar):
        print("{} is not a valid file".format(inBar))
        sys.exit(2)
    #print("Going to decode {} to output file {}".format(inBar, outBar))
    ###################################################################
    ######################### END PARAMS READ #########################
    ###################################################################

    ###################################################################
    ####################### START HEADERS READ ########################
    ###################################################################
    #print("Reading file {}...".format(inBar), end='', flush=True)
    f = open(inBar, "rb")
    #print("done!")

    #print("Detecting...", end='', flush=True)
    imHeight = np.int(125)
    imWidth = struct.unpack('i', f.read(4))[0]
    idx = struct.unpack('B', f.read(1))[0]
    #print("Shape {}x{}...".format(imWidth, imHeight), end='', flush=True)

    vCount = np.zeros([idx], dtype = np.uint8)
    for i in range(idx):
        vCount[i] = struct.unpack('B', f.read(1))[0]
    ###################################################################
    ######################## END HEADERS READ #########################
    ###################################################################

    ###################################################################
    ######################## START HRLE DECODE ########################
    ###################################################################
    dBar1D = np.zeros([imWidth * idx], dtype = np.uint8)
    idy = -1
    buff = f.read(1)
    while buff:
        value = struct.unpack('B', buff)[0]
        run = struct.unpack('B', f.read(1))[0]
        if run == 0:
            run = struct.unpack('H', f.read(2))[0]
        for j in range(run):
            dBar1D[idy] = value
            idy += 1
        buff = f.read(1)
    ###################################################################
    ######################### END HRLE DECODE #########################
    ###################################################################

    ###################################################################
    ######################## START VRLE DECODE ########################
    ###################################################################
    dRLE = dBar1D.reshape([idx, imWidth])
    dBar = np.zeros([imHeight, imWidth], dtype = np.uint8)
    idy = 0
    for i in range(idx):
        line = dRLE.take(i, axis = 0)
        for count in range(vCount[i]):
            dBar[idy] = line
            idy += 1
    imageio.imwrite(outBar, dBar)
    ###################################################################
    ######################### END VRLE DECODE #########################
    ###################################################################

if __name__ == "__main__":
    main(sys.argv[1:])