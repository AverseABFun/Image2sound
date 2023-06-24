#!/usr/bin/env python3

from main import video2sound, image2sound, path

if __name__ == "__main__":
    vidSound = video2sound("test/roar.mp4", path)
    imgSound = image2sound("test/lion.jpeg", path)
    print("First 11 elements of vidSound: "+vidSound[:11]) # if vidSound is correct, it should be ~1000 elements long. That would clog up the terminal so it's a good idea to shorten it.
    print("vidSound length: "+len(vidSound))
    print("imgSound: "+imgSound) # imgSound is just a tuple of length 2, so it's fine.