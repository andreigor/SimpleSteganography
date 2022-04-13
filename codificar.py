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
    data = data + '\0' # adding EOF signal
    bits_secret_message = text2bits(data)
    arr_secret_message = np.array([int(char) for char in bits_secret_message], dtype = np.uint8)
    
    return arr_secret_message

def encrypt_image_bit_plane(input_image: iio.core.util.Array , ascii_text: np.array, bitplane: str = '0'):
    """
    Encrypts an ASCII text into least significative bits of an image band.
    The order in which the image is filled is: columns -> rows, i.e. the message first occupies the
    whole first row, then the second and so forth.
    
    Parameters:
    input_image: image in which the text will be hided.
    ascii_text: a numpy array of 1s and 0s representing an ASCII text
    bit_plane: a integer representing which bit plane to encrypt the message. Could be 0 - least significative;
               1 - second least significative; 2 - third least significative
    
    Returns:
    output_image: image with hidden text
    remaining_text: the remaining message that wasn't able to fit in a single image bit plane
    """
    unpacked_bits_image = np.unpackbits(input_image, axis = 1)
    bit_plane_mapping = {7: '0', 6: '1', 5: '2', 4: '3', 3: '4', 2: '5' , 1: '6', 0: '7'}
    
    # temp variable that will be reshaped to store ascii_text
    temp = unpacked_bits_image[:, bitplane::8, :].copy()
    temp = temp.reshape(-1)
    
    # check to see if message fits in bit_plane
    image_available_space = np.prod(input_image.shape)
    if image_available_space < len(ascii_text):
        print("Warning: message didn't fit entirely in bit plane {}, with {} message bits remaining.".format(bit_plane_mapping[bitplane], len(ascii_text) - image_available_space))
        # filling available space
        temp[:] = ascii_text[:image_available_space]
        remaining_text = ascii_text[image_available_space:]
    else:
        print('Sucess: message fits entirely in bit plane {}'.format(bit_plane_mapping[bitplane]))
        temp[:len(ascii_text)] = ascii_text[:]
        remaining_text = np.array([-1])
    
    # returning temp original shape and assigning it to the original image
    temp = temp.reshape(unpacked_bits_image[:, bitplane::8, :].shape)
    unpacked_bits_image[:, bitplane::8, :] = temp
    
    output_image = np.packbits(unpacked_bits_image, axis = 1)
    
    return output_image, remaining_text
        
    
    
def main():
    if len(sys.argv) != 5:
        raise InputParameterError('Error in codificar.py:\n <P1> <P2> <P3> <P4>\nP1: Input image\nP2: Input text\nP3: Bits plane\nP4:Output image')

    if sys.argv[3] not in ['0','1','2']:
        raise InputParameterError('bit plane must be integer value in the set [0,1,2]')

    # reading input text and input image
    input_image = iio.imread(sys.argv[1])
    secret_message = read_input_txt(sys.argv[2])

    bit_plane_mapping = {'0': 7, '1': 6, '2': 5}
    chosen_bit_plane = bit_plane_mapping.pop(sys.argv[3])

    # filling bit plane chosen by user
    output_image, remaining_text = encrypt_image_bit_plane(input_image, secret_message, chosen_bit_plane)

    # filling remaining bit planes (if necessary) in a least significance bit order
    while(remaining_text[0] != -1):
        try:
            print('##################################################')
            print('Trying to fit remaining message in bit plane {} ...'.format((next(iter(bit_plane_mapping)))))
            output_image, remaining_text = encrypt_image_bit_plane(output_image, remaining_text, bit_plane_mapping.pop(list(bit_plane_mapping.keys())[0]))
        except StopIteration:
            print('3 bit planes were not enough to encrypt the entire message!')
            break
        
    
    # saving output image
    print("Saving output image as {}...".format(sys.argv[4]))
    iio.imwrite(sys.argv[4], output_image)
    

if __name__ == '__main__':
    main()