#!/usr/bin/python

import Tkinter
import tkFileDialog
import tkMessageBox
import time
from PIL import Image, ImageTk


mainWindow = Tkinter.Tk()


class App:

	## Member variables
	currentImage = None
	imageLabel = None
	numBitsBox = None
	useColour = Tkinter.IntVar()


	def __init__(self, master):

		## GUI elements
		frame = Tkinter.Frame(master)
		frame.pack()


		# Buttons
		openButton = Tkinter.Button(frame, text="Open...", command=self.openImage, name="openButton")
		openButton.pack(side=Tkinter.LEFT)

		encodeButton = Tkinter.Button(frame, text="Encode...", command=self.encodeImage, name="encodeButton")
		encodeButton.pack(side=Tkinter.LEFT)

		decodeButton = Tkinter.Button(frame, text="Decode", command=self.decodeImage, name="decodeButton")
		decodeButton.pack(side=Tkinter.LEFT)

		saveButton = Tkinter.Button(frame, text="Save...", command=self.saveImage, name="saveButton")
		saveButton.pack(side=Tkinter.LEFT)


		numBitsLabel = Tkinter.Label(frame, text="Number of bits:")
		numBitsLabel.pack(side=Tkinter.LEFT)

		self.numBitsBox = Tkinter.Spinbox(frame, from_=1, to_=3, width_=2, name="numBitsBox", \
										state="readonly", command=self.spinboxChanged)
		self.numBitsBox.pack(side=Tkinter.LEFT)


		colourLabel = Tkinter.Label(frame, text="Colour:")
		colourLabel.pack(side=Tkinter.LEFT, padx=(4,0))

		colourBox = Tkinter.Checkbutton(frame, variable=self.useColour, command=self.test)
		colourBox.pack(side=Tkinter.LEFT, padx=0)


		frame.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, padx=4, pady=2)


		# Frame for image
		lowerFrame = Tkinter.Frame(master)

		self.imageLabel = Tkinter.Label(lowerFrame, name="imageLabel")
		self.imageLabel.pack()

		# Go underneath the buttons, but still expand in both directions
		lowerFrame.pack(fill=Tkinter.BOTH)

	# end __init__()

	def test(self):
		print self.useColour.get()


	def openImage(self):
		pathToImage = tkFileDialog.askopenfilename()

		if pathToImage == "":
			print "Open cancelled"
			return

		print "Opening " + pathToImage
		self.currentImage = Image.open(pathToImage).convert('RGB')
		image = ImageTk.PhotoImage( self.currentImage )

		self.imageLabel.configure(image_ = image)
		self.imageLabel.image = image
		self.imageLabel.pack()



	def encodeImage(self):
		pathToImage = tkFileDialog.askopenfilename()

		if pathToImage == "":
			print "Open cancelled"
			return

		print "Opening " + pathToImage + " for encoding..."

		secretImage = Image.open(pathToImage).convert('RGB')

		secretWidth = secretImage.size[0]
		secretHeight = secretImage.size[1]
		secretPix = secretImage.load()

		currentWidth = self.currentImage.size[0]
		currentHeight = self.currentImage.size[1]
		currentPix = self.currentImage.load()


		# grayscale encoding -- MUCH more simple than colour
		if self.useColour.get() == 0:

			if secretWidth > currentWidth or secretHeight > currentHeight:
				tkMessageBox.showinfo("Incompatible images!", "The secret image must be smaller than the public image.")
				print "Secret image is bigger than target!"
				return

			# Center encoding within target image
			x0 = currentWidth/2 - secretWidth/2
			y0 = currentHeight/2 - secretHeight/2

			numBits = int(self.numBitsBox.get())
			exp = 8 - min(8,numBits*3)
			factor = 2**exp

			# for 1 bits: 1111 1110
			# for 2 bits: 1111 1100
			# for 3 bits: 1111 1000
			baseMask = (255 ^ (2**numBits - 1))


			#   -----------------------------------------
			# |       |   1-bit   |   2-bit   |   3-bit   |
			# | ----- | --------- | --------- | --------- |
			# | maskR | 0000 0100 | 0011 0000 | 1100 0000 |
			# | maskG | 0000 0010 | 0000 1100 | 0011 1000 |
			# | maskB | 0000 0001 | 0000 0011 | 0000 0111 |
			#   -----------------------------------------
			targetMaskR = (2**numBits - 1) << 2 * numBits
			targetMaskG = (2**numBits - 1) << numBits
			targetMaskB = 2**numBits - 1

			print "Encoding..."

			# loop for every pixel
			for x in range(0, secretWidth):
				for y in range(0, secretHeight):

					# currently using green only
					targetValue = int(secretPix[x,y][1] / factor)
					
					shiftedTargetR = (targetValue & targetMaskR) >> (2 * numBits)
					shiftedTargetG = (targetValue & targetMaskG) >> numBits
					shiftedTargetB = targetValue & targetMaskB

					r = baseMask | shiftedTargetR
					g = baseMask | shiftedTargetG
					b = baseMask | shiftedTargetB

					oldPixel = currentPix[x0+x,y0+y]

					# Can't forget both & and | here, since we want to both set and unset the proper bits
					pixel = (oldPixel[0] & r | shiftedTargetR, oldPixel[1] & g | shiftedTargetG,\
							 oldPixel[2] & b | shiftedTargetB)
					currentPix[x0+x, y0+y] = pixel

			# end pixel loops

		# end grayscale pixel assignment



		elif self.useColour.get() == 1:
			print "Using colour..."

			# This should be a multiple of 3 or weird things will happen below
			SIZE_BITS = 12

			widthBits = [None] * SIZE_BITS
			heightBits = [None] * SIZE_BITS

			widthMask = [None] * SIZE_BITS
			heightMask = [None] * SIZE_BITS


			# Convert width and height into 12 individual bit-values each
			for i in range(0, SIZE_BITS):
				widthBits[i]  = (2**(SIZE_BITS - 1 - i) & secretWidth)  >> (SIZE_BITS - 1 - i)
				heightBits[i] = (2**(SIZE_BITS - 1 - i) & secretHeight) >> (SIZE_BITS - 1 - i)

				widthMask[i] = 254 | widthBits[i]
				heightMask[i] = 254 | heightBits[i]

			pix = currentPix[0,0]
			currentPix[0,0] = (pix[0] & widthMask[0] | widthBits[0], pix[1] & widthMask[1] | widthBits[1],\
								pix[2] & widthMask[2] | widthBits[2])

			# Encode size data in public image
			for i in range(0, SIZE_BITS/3):
				pix = currentPix[i,0]
				currentPix[i,0] = (pix[0] & widthMask[3*i]     | widthBits[3*i],\
								   pix[1] & widthMask[3*i + 1] | widthBits[3*i + 1],\
								   pix[2] & widthMask[3*i + 2] | widthBits[3*i + 2])

				pix = currentPix[SIZE_BITS/3 + i, 0]
				currentPix[SIZE_BITS/3 + i, 0] = (pix[0] & heightMask[3*i]     | heightBits[3*i],\
									  pix[1] & heightMask[3*i + 1] | heightBits[3*i + 1],\
									  pix[2] & heightMask[3*i + 2] | heightBits[3*i + 2])


			# Pixels 0 through 7 now contain 12-bit dimensions data.
			
			

			#print widthBits
			#print heightBits




		# refresh image in label
		tkimage = ImageTk.PhotoImage(self.currentImage)
		self.imageLabel.configure(image=tkimage)
		self.imageLabel.image = tkimage # keep reference for tkimage version

		print "Done encoding."
		tkMessageBox.showinfo("Done Encoding", "Encoding is finished! Click Decode to view the "+\
				"secret image or click Save to save the result.")

	# end encodeImage()



	def decodeImage(self):
		w = self.currentImage.size[0]
		h = self.currentImage.size[1]

		pixels = self.currentImage.load()

		numBits = int(self.numBitsBox.get())
		exp = 8 - min(8,numBits*3)
		factor = 2**exp


		for x in range(0,w):
			for y in range(0,h):
				pix = pixels[x,y]
				pre = ((pix[0] & (2**numBits-1)) << 2*numBits) + \
				      ((pix[1] & (2**numBits-1)) << numBits) + \
				       (pix[2] & (2**numBits-1))
				
				gray = pre * factor
				pixels[x,y] = (gray, gray, gray)


		tkimage = ImageTk.PhotoImage(self.currentImage)
		self.imageLabel.configure(image=tkimage)
		self.imageLabel.image = tkimage

		print "Done decoding."


	def saveImage(self):
		pathToSave = tkFileDialog.asksaveasfilename(defaultextension=".PNG",filetypes=[("PNG Image","*.png")])

		if pathToSave == "":
			print "Save cancelled."
			return

		self.currentImage.save(pathToSave)


	def spinboxChanged(self):
		print self.numBitsBox.get()


mainWindow.title("SecretImage")

app = App(mainWindow)

mainWindow.mainloop()