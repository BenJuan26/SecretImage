# SecretImage #
Hides an entire grayscale image within another image.

## Prereqs ##
Python image library `Pillow` (maintained fork of `PIL`) must be installed. It can be installed using `pip`:  

	pip install Pillow

## How does it work? ##
SecretImage uses the concept of [steganography](https://en.wikipedia.org/wiki/Steganography) to encode the values of the secret image into the values of the public image. The number of bits used for encoding will affect how much the public image is changed. For 1 bit, the human eye cannot see the difference between adjacent values of an 8-bit image, so the encoded image would go completely unnoticed. The disadvantage of using few bits is that the secret image is low-quality. For simple things like text, this isn't a big deal, but to encode higher quality images, more bits are required. 2 bits is a happy medium between the quality of the resulting image and the effect on the public image. Using 3 bits results in a full 8-bit grayscale decoded image but will affect the public image much more. Hard contrast lines in the secret image might begin to show in the public image in this case.