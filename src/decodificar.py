"""
Unicamp - 13/04/2022
Author: André Igor Nóbrega da Silva
email: a203758@dac.unicamp.br
Simple Steganography exercise, as part of Introduction to Digital Image Processing Course
"""

import sys
import imageio as iio
import numpy as np
from utils import bits2text, uncrypt_text_from_image

class InputParameterError(Exception):
    "Raised when input parameter is not as expected"
    pass

def main():
    if len(sys.argv) != 4:
        raise InputParameterError('Error in decodificar.py:\n <P1> <P2> <P3> <P4>\nP1: Input image (with encrypted message)\nP2: Bits plane\nP3: Output text\n')

    if sys.argv[2] not in ['0','1','2']:
        raise InputParameterError('Bit plane must be integer value in the set [0,1,2]')

    # reading input encrypted image
    input_image = iio.imread(sys.argv[1])

    bit_plane_mapping = {'0': 7, '1': 6, '2': 5}
    bit_plane = bit_plane_mapping.pop(sys.argv[2])
    EOF_index = [np.array([])]

    print('Decoding image...\n')
    secret_message = ''

    # start decoding - looking for EOF and adding message
    while(EOF_index[0].size == 0):
        print('##################################################')
        print('Decoding image bit plane {}'.format(-bit_plane + 7))
        bit_plane_message, EOF_index = uncrypt_text_from_image(input_image, bit_plane)
        secret_message += bit_plane_message

        # breaking the loop if there is no more bit planes
        if not len(bit_plane_mapping):
            if (EOF_index[0].size ==0):
                print('Warning: end of message was not found in the 3 allowed bit planes!')
                print('Message is probably too big for image\n')
            break

        # getting next bit plane
        bit_plane = bit_plane_mapping.pop(list(bit_plane_mapping.keys())[0])
        
    print('Decoding ended - saving file in {}'.format('../output/' + sys.argv[3]))

    f = open('../outputs/' + sys.argv[3], "w")
    f.write(bits2text(secret_message))
    f.close()

if __name__ == '__main__':
    main()