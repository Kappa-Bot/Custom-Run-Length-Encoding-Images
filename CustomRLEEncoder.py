import numpy as np
import imageio

import sys
from os.path import isfile
import struct

def main(argv):
    ###################################################################
    ######################## START PARAMS READ ########################
    ###################################################################
    if len(argv) != 2:
        print("Usage: barcode_encoder.py <input_file> <output_file>")
        sys.exit(1)
    inBar, outBar = argv[0], argv[1]
    if not isfile(inBar):
        print("{} is not a valid file".format(inBar))
        sys.exit(2)
    ###################################################################
    ######################### END PARAMS READ #########################
    ###################################################################

    ###################################################################
    ######################## START DATA INIT ##########################
    ###################################################################
    #print("Going to encode {} to output file {}".format(inBar, outBar))
    bar = np.ascontiguousarray(imageio.imread(inBar), dtype = np.uint8)
    imHeight, imWidth = bar.shape[0], bar.shape[1]
    ###################################################################
    ######################### END DATA INIT ###########################
    ###################################################################

    ###################################################################
    ####################### START VRLE ENCODE #########################
    ###################################################################
    """ Perform a Vertical RLE
        vRLE contains the different rows (Symbols) found consecutively
        vCounts contains the counts of each correspondent row
    """
    vCount = np.zeros([imHeight], dtype = np.uint8)
    vRLE = np.zeros([imHeight, imWidth], dtype = np.uint8)
    idx = 0; run = 1
    for i in range(1, imHeight):
        if np.equal(bar.take(i, axis = 0),
                    bar.take(i - 1, axis = 0)).all():
            run += 1 # Consecutive match
        else:
            vCount[idx] = run # New row
            vRLE[idx] = bar.take(i - 1, axis = 0)
            run = 1; idx += 1
        if i == imHeight - 1: # Last case
            vCount[idx] = run
            vRLE[idx] = bar.take(0, axis = 0)
            idx += 1

    # At this point: idx = total number of different symbols
    vCount = np.ascontiguousarray(vCount[:idx], dtype = np.uint8)
    vRLE = np.ascontiguousarray(vRLE[:idx][:], dtype = np.uint8)
    imageio.imwrite("{}.png".format(outBar), vRLE)
    ###################################################################
    ######################## END VRLE ENCODE ##########################
    ###################################################################

    ###################################################################
    ##################### START HEADERS WRITE #########################
    ###################################################################
    #print("Creating file {}...".format(outBar), end='', flush=True)
    if not isfile(outBar):
        open(outBar, "x").close()
    f = open(outBar, "wb")
    #print("done!")

    f.write(struct.pack('i', imWidth)) # Height always = 125
    f.write(struct.pack('B', idx)) # idx always <= 125 => 7 bits...
    for i in range(idx): # Write Vertical RLE Counts
        f.write(struct.pack('B', vCount[i]))
    ###################################################################
    ####################### END HEADERS WRITE #########################
    ###################################################################

    ###################################################################
    ####################### START HRLE ENCODE #########################
    ###################################################################
    """ Perform a Horizontal RLE over the Vertical RLE Dictionary
        vRLE1D is the 1D-version of the Vertical RLE Dictionary
        Writes on file will be pairs:
            Symbol: 1Byte for the pixel value of the actual row
            Count: Indicates the repetition count for the Symbol
                1Byte for the count value
                If needs more than 1Byte of storage (value > 255):
                    - Write 0 (impossible case in conventional RLE)
                    - Write 2Bytes for the count
                    *This works since we always read in 
                        the pair order when decoding*
    """
    vRLE1D = vRLE.reshape(idx * imWidth)
    run = 1
    for i in range(idx * imWidth):
        if vRLE1D[i] == vRLE1D[i - 1]:
            run += 1 # Add count for the actual value
        else: # New Pixel Value
            # Write the value
            f.write(struct.pack('B', vRLE1D[i - 1]))

            # Write the count (1Byte(run) or 1Byte(0) + 2Bytes(run)
            if run > 255:
                f.write(struct.pack('B', 0))
                f.write(struct.pack('H', run))
            else:
                f.write(struct.pack('B', run))
            run = 1
        if i == (idx * imWidth - 1): # Last case
            # Write the value
            f.write(struct.pack('B', vRLE1D[i - 1]))

            # Write the count (1Byte(run) or 1Byte(0) + 2Bytes(run)
            if run > 255:
                f.write(struct.pack('B', 0))
                f.write(struct.pack('H', run))
            else:
                f.write(struct.pack('B', run))
            run = 1
    ###################################################################
    ######################## END HRLE ENCODE ##########################
    ###################################################################

if __name__ == "__main__":
    main(sys.argv[1:])
