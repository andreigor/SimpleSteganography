"""
Unicamp - 13/04/2022
Author: André Igor Nóbrega da Silva
email: a203758@dac.unicamp.br
Simple Steganography exercise, as part of Introduction to Digital Image Processing Course
"""

import sys
import imageio as iio
import numpy as np
from utils import read_input_txt, encrypt_image_bit_plane

class InputParameterError(Exception):
    "Raised when input parameter is not as expected"
    pass
    
def main():
    if len(sys.argv) != 5:
        raise InputParameterError('Error in codificar.py:\n <P1> <P2> <P3> <P4>\nP1: Input image\nP2: Input text\nP3: Bits plane\nP4:Output image')

    if sys.argv[3] not in ['0','1','2']:
        raise InputParameterError('bit plane must be integer value in the set [0,1,2]')

    # reading input text and input image
    output_image = iio.imread(sys.argv[1])
    remaining_text = read_input_txt(sys.argv[2])

    bit_plane_mapping = {'0': 7, '1': 6, '2': 5}
    bit_plane = bit_plane_mapping.pop(sys.argv[3])
    
    # filling bit plane chosen by user and then remaining bit planes (if necessary) in a least significance bit order
    while(remaining_text[0] != -1):
        print('##################################################')
        print('Trying to fit remaining message in bit plane {} ...'.format(-bit_plane + 7))
        output_image, remaining_text = encrypt_image_bit_plane(output_image, remaining_text, bit_plane)

        if not len(bit_plane_mapping):
            if remaining_text[0] != -1:
                print('3 bit planes were not enough to encrypt the entire message!\n')
            break

        bit_plane = bit_plane_mapping.pop(list(bit_plane_mapping.keys())[0])
 
    # saving output image
    print("Saving output image as {}".format('../outputs/' + sys.argv[4]))
    iio.imwrite('../outputs/' + sys.argv[4], output_image)
    
if __name__ == '__main__':
    main()