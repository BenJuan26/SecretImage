#!/usr/bin/python

import Tkinter
import tkFileDialog
import tkMessageBox
from PIL import Image, ImageTk

class App:

	## Member variables
	currentImage = None
	imageLabel = None
	numBitsBox = None


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

		numBitsLabel = Tkinter.Label(frame, text="Number of bits:", padx=3)
		numBitsLabel.pack(side=Tkinter.LEFT)

		self.numBitsBox = Tkinter.Spinbox(frame, from_=1, to_=3, width_=4, name="numBitsBox", \
										state="readonly", command=self.spinboxChanged)
		self.numBitsBox.pack(side=Tkinter.LEFT)

		frame.pack(side=Tkinter.TOP, fill=Tkinter.BOTH)


		# Frame for image
		lowerFrame = Tkinter.Frame(master)

		self.imageLabel = Tkinter.Label(lowerFrame, name="imageLabel")
		self.imageLabel.pack()

		# Go underneath the buttons, but still expand in both directions
		lowerFrame.pack(fill=Tkinter.BOTH)

	# /__init__()


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

		if secretWidth > currentWidth or secretHeight > currentHeight:
			tkMessageBox.showinfo("Incompatible images!", "The secret image must be smaller than the target image.")
			print "Secret image is bigger than target!"
			return

		# Center encoding within target image
		x0 = currentWidth/2 - secretWidth/2
		y0 = currentHeight/2 - secretHeight/2

		numBits = int(self.numBitsBox.get())
		exp = 8 - min(8,numBits*3)
		factor = 2**exp

		for x in range(0, secretWidth):
			for y in range(0, secretHeight):
				# currently using green only
				targetValue = int(secretPix[x,y][1] / factor)
				
				# for 1 bits: 1111 1110
				# for 2 bits: 1111 1100
				# for 3 bits: 1111 1000
				baseMask = (255 & ~(2**numBits - 1))


				#       |   1-bit   |   2-bit   |   3-bit
				# ----- | --------- | --------- | ---------
				# maskR | 0000 0100 | 0011 0000 | 1100 0000
				# maskG | 0000 0010 | 0000 1100 | 0011 1000
				# maskB | 0000 0001 | 0000 0011 | 0000 0111
				# -----------------------------------------
				targetMaskR = (2**numBits - 1) << 2 * numBits
				targetMaskG = (2**numBits - 1) << numBits
				targetMaskB = 2**numBits - 1

				shiftedTargetR = ((targetValue & targetMaskR) >> (2 * numBits))
				shiftedTargetG = ((targetValue & targetMaskG) >> numBits)
				shiftedTargetB = (targetValue & targetMaskB)

				r = baseMask | shiftedTargetR
				g = baseMask | shiftedTargetG
				b = baseMask | shiftedTargetB

				oldPixel = currentPix[x0+x,y0+y]

				# Can't forget both & and | here, since we want to both set and unset the proper bits
				pixel = (oldPixel[0] & r | shiftedTargetR, oldPixel[1] & g | shiftedTargetG,\
						 oldPixel[2] & b | shiftedTargetB)
				currentPix[x0+x, y0+y] = pixel
		# end pixel loops

		# refresh image in label
		tkimage = ImageTk.PhotoImage(self.currentImage)
		self.imageLabel.configure(image=tkimage)
		self.imageLabel.image = tkimage

	# /encodeImage()



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
						((pix[1] & (2**numBits-1)) << numBits) + (pix[2] & (2**numBits-1))
				#if pre != 0:
				#	print pre
				gray = pre * factor
				pixels[x,y] = (gray, gray, gray)

		tkimage = ImageTk.PhotoImage(self.currentImage)
		self.imageLabel.configure(image=tkimage)
		self.imageLabel.image = tkimage
		print "Done decoding."


	def saveImage(self):
		pathToSave = tkFileDialog.asksaveasfilename()

		if pathToSave == "":
			print "Save cancelled"
			return

		self.currentImage.save(pathToSave)


	def spinboxChanged(self):
		print self.numBitsBox.get()


mainWindow = Tkinter.Tk()

app = App(mainWindow)

mainWindow.mainloop()