import sys
import imageio as iio
import numpy as np
import matplotlib.pyplot as plt

class InputParameterError(Exception):
    "Raised when input parameter is not as expected"
    pass

def main():
    # if len(sys.argv) != 3:
    #     raise InputParameterError('Error in codificar.py:\n <P1> <P2> <P3> <P4>\nP1: input image\nP2: input text\nP3: bits plane\nP4:output image')

    # Reading image as numpy array
    # input_image = iio.imread(sys.argv[1])
    # a = np.array(input_image, dtype = np.uint8)
    a = 
    # print image dimensions and type
    # show image
    plt.imshow(input_image, cmap='gray')
    plt.show()
    # save image in PNG format
    iio.imwrite(sys.argv[2], input_image)

if __name__ == '__main__':
    main()