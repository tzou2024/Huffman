import cv2
from pprint import pprint
from bitstring import BitArray
# importing Counter module
from collections import Counter
import numpy as np
import sys


class Node:
    '''
    Node class for creating a tree
    '''
    def __init__(self, intensity, freq, isLeaf, children=[]):
        self.intensity = intensity
        self.freq = freq
        self.isLeaf = isLeaf
        self.children = children
        self.bitrep = ""
    
    def __str__(self):  
        return "<Node: '% s', " "freq: % s, bit: %s , leaf: %s>" % (self.intensity, str(round(self.freq, 2)), self.bitrep, self.isLeaf)  

    def assignbit(self, bitstring):
        self.bitrep = bitstring

def flattenWH(image):
    '''
    Flatten the image and return its width and height
    '''
    w, h = image.shape
    flattened_vals = gray_image.flatten()
    return w, h, flattened_vals


def create_frequencies(flattened_vals):
    '''
    Using a flattened image, create a list of nodes with different intensities
    sorted by freq as a percentage in ascending order
    '''
    frequencies = {}
    nodelist = []
    for i in flattened_vals:
        frequencies[i] = frequencies.get(i, 0) + 1

    for key, val in frequencies.items():
        nodelist.append(Node(intensity=key, freq=val/len(flattened_vals), isLeaf=True))
        
    sorted_list = sorted(nodelist, key=lambda x: x.freq)
    
    return sorted_list

def create_tree(sorted_list):
    '''
    Using a sorted node list, create an initial tree structure from the bottom up
    with all info but the bitstring representation of each leaf node
    '''
    while len(sorted_list) >  1:
        # Extract the two lowest frequency nodes
        node1 = sorted_list[0]
        node2 = sorted_list[1]
        # Cut them out of the frequency list
        sorted_list = sorted_list[2:]
        # Create a parent node that relates the two lowest frequency nodes
        newnode = Node(intensity="comb", freq=node1.freq + node2.freq, isLeaf=False, children=[node1, node2])
        # Add that parent back into the frequency list
        sorted_list = [newnode] + sorted_list
        # Re-sort the frequency list
        sorted_list = sorted(sorted_list, key=lambda x: x.freq)
    return sorted_list[0]

def populatetree(node, bits):
    '''
    Once you have the tree made, traverse from top down assigning bitstring
    representations to each leaf node
    '''
    if node.isLeaf:
        # If you've reached a leaf, assign the bitstring to the node
        node.assignbit(bits)
    
    # If you aren't at a leaf node, add a 0 or 1 for left and right child and continue traversing
    if len(node.children) > 0:
        populatetree(node.children[0], bits+'0')
    if len(node.children) > 1:
        populatetree(node.children[1], bits+'1')

def createmappig(node):
    '''
    we don't want to have to traverse the tree for each lookup, so save the mappings from intensities
    to bitstrings in a dictionary
    '''
    if node.isLeaf:
        dicty[node.intensity] = node.bitrep
    if len(node.children) > 0:
        createmappig(node.children[0])
    if len(node.children) > 1:
        createmappig(node.children[1])

def createencodedstring(img, dicty):
    '''
    Take the flattened image and convert each number to its bitstring representation
    and combine those all into one large encoded string
    '''
    encodedstring= ""
    for i in img:
        encodedstring += dicty[i]
    return encodedstring

def decoder(encodedstring, root):
    '''
    Use the tree to decode the encoded string back into intensity values
    '''
    oglen = len(encodedstring)
    decoded = []
    skipper = 0

    # Use another variable to keep track of root node
    tracker = root
    while len(encodedstring) > 0:
        # Keeping track of progress using skipper variable
        # because decoding takes a long time
        # skipper += 1
        # if skipper % 3000 == 0:
        #     progress = round(1 - round(len(encodedstring) / oglen, 2), 2) * 100
        #     print(progress, "%")
            
        # Pull the next bit out of the encoded string
        step = encodedstring[0]
        encodedstring = encodedstring[1:]

        # Traverse down the tree according to the bit that was just pulled
        if step == "0":
            tracker = tracker.children[0]
        elif step == "1":
            tracker = tracker.children[1]

        # If after you've traversed the step you arrive at a leaf node, you know that you've
        # Decoded a full intensity value, so save that and start back over at the root node
        if tracker.isLeaf:
            decoded.append(tracker.intensity)
            tracker = root
            continue
    return decoded

# total arguments
n = len(sys.argv)

imgpath = "spiral.png"
# Load the input image 
if n > 1:
    imgpath = sys.argv[1]

image = cv2.imread('spiral.png')
print("Loading in image: ", imgpath)

# Use the cvtColor() function to grayscale the image 
# currently a numpy array

print("Converting to grayscale")
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

# save the width and height for later
w,h, flattened_vals = flattenWH(gray_image)

# flatten the image into one long array
print("Flatten image into 1d array")
flattened_vals = gray_image.flatten()

# create sorted list of frequencies
print("Creating frequency list")
sorted_list = create_frequencies(flattened_vals=flattened_vals)

# use frequencies to create tree from bottom up
print("Creating tree from bottom up")
tree = create_tree(sorted_list=sorted_list)

print("Populating tree edges with 0's and 1's for bitstring representations for intensity values: ")
populatetree(tree, "")

# save the bitstring representations to a dictionary to save time encoding

print("++++++++++++++++++++++++++++++++++++++")
print("Saving bitstring representations: ")
dicty = {}
createmappig(tree)

pprint(dicty)
# use the mapping to convert all intensity values into one encoded bitstring
encodedstring = createencodedstring(flattened_vals, dicty)

'''
Saving the binary file. The image files already have better compression than we
Can implement so the binary file is bigger than the picture file, so we are assuming
Theoretical space storage
'''
file = open("compressed_ " + imgpath[:-4] + ".bin", 'wb')
obj = BitArray(bin=encodedstring)
obj.tofile(file)
file.close()

print("++++++++++++++++++++++++++++++++++++++")
print("Original Theoretical File Size: ", len(flattened_vals), "bytes * 8 bits = ", len(flattened_vals) * 8, "bits")
print("Theoretical Encoded Bitstring Size: ", len(encodedstring), "bits")
print("(+ neglible tree storage for a large volume of images)" )
print("Compression ratio: ", len(encodedstring) / len(flattened_vals) * 8, "%")

print("++++++++++++++++++++++++++++++++++++++")
print("Checking Decoding against original image using tree: ")
print("(may take a while)")
# Given the decoded string, prove that we can decode the image using the same tree
decoded = np.array(decoder(encodedstring, tree))
decodedshaped = decoded.reshape(w, h)

if np.array_equal(gray_image, decodedshaped):
    print("Decoded Successfully!")

