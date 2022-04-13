import sys
import imageio as iio
import numpy as np
import matplotlib.pyplot as plt

class InputParameterError(Exception):
    "Raised when input parameter is not as expected"
    pass

def text2bits(text, encoding='utf-8', errors='surrogatepass'):
    """
    Converts a given text (string) to its binary representation in the ASCII code.
    Reference: https://stackoverflow.com/questions/7396849/convert-binary-to-ascii-and-vice-versa    
    """
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def bits2text(bits, encoding='utf-8', errors='surrogatepass'):
    """
    Converts a given bit sequence in ASCII code into a string.
    Reference: https://stackoverflow.com/questions/7396849/convert-binary-to-ascii-and-vice-versa
    """
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'

def read_input_txt(input_txt):
    with open (input_txt, "r") as myfile:
        data=myfile.readlines()

    data = ''.join(data)
    bits_secret_message = text2bits(data)
    arr_secret_message = np.array([int(char) for char in bits_secret_message], dtype = np.uint8)
    
    return arr_secret_message

def main():
    if len(sys.argv) != 4:
        raise InputParameterError('Error in decodificar.py:\n <P1> <P2> <P3> <P4>\nP1: Input image (with encrypted message)\nP2: Bits plane\nP3: Output text\n')

    if sys.argv[2] not in ['0','1','2']:
        raise InputParameterError('Bit plane must be integer value in the set [0,1,2]')

    # reading input encrypted image
    input_image = iio.imread(sys.argv[1])

    # searching for EOF in first bit plane (specified by user)
    bit_plane_mapping = {'0': 7, '1': 6, '2': 5}
    bit_plane_index = bit_plane_mapping.pop(sys.argv[2])

    print('Decoding image...')
    unpacked_bits_image = np.unpackbits(input_image, axis = 1)
    bit_plane_message = np.packbits(unpacked_bits_image[:,bit_plane_index::8,:].reshape(-1))
    EOF_index = np.where(bit_plane_message == 0)
    
    
    secret_message = ''
    while(EOF_index[0].size == 0 and len(bit_plane_mapping)):
        secret_message += ''.join(str(v) for v in list(unpacked_bits_image[:, bit_plane_index::8, :].reshape(-1)))
        bit_plane_index = bit_plane_mapping.pop(list(bit_plane_mapping.keys())[0])
        bit_plane_message = np.packbits(unpacked_bits_image[:, bit_plane_index::8, :])
        EOF_index = np.where(bit_plane_message == 0)
    
    if (EOF_index[0].size == 0):
        print('Warning: the image probably occupies the 3 allowed bit planes - it was not possible to perform full decoding!')
        secret_message += ''.join(str(v) for v in list(unpacked_bits_image[:, bit_plane_index::8, :].reshape(-1)))
    else:
        secret_message += ''.join(str(v) for v in list(unpacked_bits_image[:, bit_plane_index::8, :].reshape(-1)[:EOF_index[0][0]*8]))

    print('Decoding ended - saving file in {}'.format(sys.argv[3]))

    f = open(sys.argv[3], "w")
    f.write(bits2text(secret_message))
    f.close()

    

if __name__ == '__main__':
    main()