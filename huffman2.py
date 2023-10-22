import cv2
from pprint import pprint
from bitstring import BitArray
# importing Counter module
from collections import Counter
import numpy as np


class Node:
    '''
    Create a Node class for creating a tree
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
    using a flattened image, create a list of nodes with different intensities
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
    using a sorted node list, create an initial tree structure from the bottom up
    with all info but the bitstring representation of each leaf node
    '''
    while len(sorted_list) >  1:
        node1 = sorted_list[0]
        node2 = sorted_list[1]
        sorted_list = sorted_list[2:]
        newnode = Node(intensity="comb", freq=node1.freq + node2.freq, isLeaf=False, children=[node1, node2])
        sorted_list = [newnode] + sorted_list
        sorted_list = sorted(sorted_list, key=lambda x: x.freq)
    return sorted_list[0]

def populatetree(node, bits):
    '''
    once  you have the tree made, traverse from top down assigning bitstring
    representations to each leaf node
    '''
    if node.isLeaf:
        node.assignbit(bits)
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
    tracker = root
    while len(encodedstring) > 0:
        skipper += 1
        if skipper % 3000 == 0:
            progress = round(1 - round(len(encodedstring) / oglen, 2), 2) * 100
            print(progress, "%")
        step = encodedstring[0]
        encodedstring = encodedstring[1:]
        if step == "0":
            tracker = tracker.children[0]
        elif step == "1":
            tracker = tracker.children[1]
            
        if tracker.isLeaf:
            decoded.append(tracker.intensity)
            tracker = root
            continue
    return decoded

# Load the input image 
image = cv2.imread('spiral.png')


# Use the cvtColor() function to grayscale the image 
# currently a numpy array
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

# save the width and height for later
w,h, flattened_vals = flattenWH(gray_image)
print(w,h)

# flatten the image into one long array
flattened_vals = gray_image.flatten()

# create sourted 
sorted_list = create_frequencies(flattened_vals=flattened_vals)

tree = create_tree(sorted_list=sorted_list)
populatetree(tree, "")

dicty = {}
createmappig(tree)

pprint(dicty)
encodedstring = createencodedstring(flattened_vals, dicty)


file = open("save.bin", 'wb')
obj = BitArray(bin=encodedstring)
obj.tofile(file)
file.close()

# interted = invertmapping(dicty)

# items = Counter(interted).keys()

decoded = np.array(decoder(encodedstring, tree))
print(decoded)
decodedshaped = decoded.reshape(w, h)

print(np.equal(gray_image, decodedshaped))

print(len(encodedstring) < len(flattened_vals) * 8)


