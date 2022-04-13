import numpy as np
import imageio as iio
 

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

def encrypt_image_bit_plane(input_image: iio.core.util.Array , ascii_text: np.array, bitplane: int = 7):
    """
    Encrypts an ASCII text into an image bit plane.
    The order in which the image is filled is: bands -> columns -> rows, i.e. the message first occupies the
    3 bands of first column and first row, then the 3 bands of second column and first row and so forth.

    Parameters:
    input_image: image in which the text will be hided.
    ascii_text: a numpy array of 1s and 0s representing an ASCII text
    bit_plane: a integer representing which bit plane to encrypt the message. Could be 7 - least significative;
               6 - second least significative; 5 - third least significative
    
    Returns:
    output_image: image with hidden text
    remaining_text: the remaining message that wasn't able to fit in a single image bit plane
    """
    unpacked_bits_image = np.unpackbits(input_image, axis = 1)
    
    # temp variable that will be reshaped to store ascii_text
    temp = unpacked_bits_image[:, bitplane::8, :].copy()
    temp = temp.reshape(-1)
    
    # check to see if message fits in bit_plane
    image_available_space = np.prod(input_image.shape)
    if image_available_space < len(ascii_text):
        print("Warning: message didn't fit entirely in bit plane {}, with {} message bits remaining.\n".format(-bitplane + 7, len(ascii_text) - image_available_space))
        # filling available space
        temp[:] = ascii_text[:image_available_space]
        remaining_text = ascii_text[image_available_space:]
    else:
        print('Sucess: message fits entirely in bit plane {}\n'.format(-bitplane + 7))
        temp[:len(ascii_text)] = ascii_text[:]
        remaining_text = np.array([-1])
    
    # returning temp original shape and assigning it to the original image
    temp = temp.reshape(unpacked_bits_image[:, bitplane::8, :].shape)
    unpacked_bits_image[:, bitplane::8, :] = temp
    
    output_image = np.packbits(unpacked_bits_image, axis = 1)
    
    return output_image, remaining_text

def uncrypt_text_from_image(input_image: iio.core.util.Array, bit_plane: int = 7):
    """
    Uncrypts a sequence of bits representing a sequence ASCII characters from
    an input image bit plane.
    The order in which the text is obtained is: bands -> columns -> rows.

    Parameters:
    input_image: image with hidden text
    bit_plane: a integer representing the bit plane in wich the message is hidden.
               Could be 7 - least significative;
               6 - second least significative; 
               5 - third least significative
    
    Returns:
    secret_message: sequence of ASCII characters representing the decoded secret message
    EOF_index: index of EOF character.
    """
    # unpacking bits from image
    unpacked_bits_image = np.unpackbits(input_image, axis = 1)

    # selecting chosen bit plane
    bit_plane_message = np.packbits(unpacked_bits_image[:,bit_plane::8,:].reshape(-1))

    # searching for end of file indicator ('\0')
    EOF_index = np.where(bit_plane_message == 0)
    
    if (EOF_index[0].size == 0):
        print("Logging: the message ending is not in bit plane {}\n".format(-bit_plane + 7))
        secret_message = ''.join(str(v) for v in list(unpacked_bits_image[:, bit_plane::8, :].reshape(-1)))
    else:
        print("Logging: end of message found in bit plane {}\n".format(-bit_plane + 7))
        secret_message = ''.join(str(v) for v in list(unpacked_bits_image[:, bit_plane::8, :].reshape(-1)[:EOF_index[0][0]*8]))

    return secret_message, EOF_index