#!/usr/bin/env python3

import PIL.Image
from hilbertcurve.hilbertcurve import HilbertCurve
import json
import os
import sys
from scipy.io.wavfile import write
import numpy as np
import moviepy
import moviepy.editor
import moviepy.video.fx.resize

SIZE = 256  # The size used in pixels
SAMPLERATE = 44100 # The sample rate used in the output audio
LENGTH = 0.5 # The length of each individual image's audio counterpart in seconds


def makePath() -> list:

    hilbert_curve = HilbertCurve(SIZE, 2, -1)

    distances = list(range(SIZE * SIZE))
    points = hilbert_curve.points_from_distances(distances)
    return points


def resize(image: PIL.Image.Image, size: int) -> PIL.Image.Image:
    return image.resize((size, size))

def resizeVideo(video: moviepy.editor.VideoFileClip, size: int) -> moviepy.editor.VideoFileClip:
    return video.fx(moviepy.video.fx.resize.resize,newsize=(size,size))

def getImagesFromVideo(video: moviepy.editor.VideoFileClip) -> list:
    frames = []
    for frame in video.iter_frames(fps=1/LENGTH):
        image = PIL.Image.fromarray(np.uint8(frame)).convert('RGB')
        frames.append(image)
    return frames

def getPixels(image: PIL.Image.Image, path: list) -> list:
    pixels = []
    for x, y in path:
        pixels.append(image.getpixel((x, y)))
    return pixels


def convertPixelsToFrequencies(pixels: list) -> list:
    freqs = []
    for pixel in pixels:
        realPixel = pixel[:3]
        brightness = sum(realPixel) / 3
        decibals = brightness * (60 / 255)
        color = 0
        for num in realPixel:
            color += num
        hertz = color * ((16000 - 25) / (765)) + 25
        freqs.append((hertz, decibals))
    return freqs


def makeFreqFromFreqs(freqs: list) -> tuple:
    resHz = 0
    resDb = 0
    for hertz, decibals in freqs:
        resHz += hertz
        resDb += decibals
    resHz *= ((16000 - 25) / (16000 * 255 * 255))
    resHz += 25
    resDb *= (60 / (60 * 255 * 255))
    print("Hertz: "+str(resHz))
    print("Decibels: "+str(resDb))
    return (resHz, resDb)

def makeSine(freq: tuple, samplerate: int, length: int) -> np.array:
    t = np.linspace(0., float(length), samplerate)
    data = freq[1] * np.sin(2. * np.pi * freq[0] * t)
    return data.astype(np.int16)

def writeFreq(freq: tuple, samplerate: int) -> None:
    write("freq.wav", samplerate, makeSine(freq,samplerate))

def writeFreqs(freqs: list, samplerate: int) -> None:
    sines = []
    for freq in freqs:
        sines += list(makeSine(freq, samplerate, LENGTH))
    write("freq.wav", samplerate, np.array(sines).astype(np.int16))

def video2sound(file: str, path: list) -> list:
    video = moviepy.editor.VideoFileClip(file)
    print("Resizing video")
    video = resizeVideo(video, SIZE)
    print(f"Getting images from video after converting video to {1/LENGTH} FPS")
    images = getImagesFromVideo(video)
    print("Looping through images and creating the frequencies for each")
    freqss = []
    for image in images:
        pixels = getPixels(image, path)
        freqs = convertPixelsToFrequencies(pixels)
        freq = makeFreqFromFreqs(freqs)
        freqss.append(freq)
    print("Combining frequencies together and writing to freq.wav")
    writeFreqs(freqss, SAMPLERATE)
    return freqss

def image2sound(file: str, path: list) -> tuple:
    image = PIL.Image.open(file)
    print("Resizing image")
    image = resize(image, SIZE)
    print("Converting image to frequency")
    pixels = getPixels(image, path)
    freqs = convertPixelsToFrequencies(pixels)
    freq = makeFreqFromFreqs(freqs)
    print("Writing frequency to freq.wav")
    writeFreq(freq, SAMPLERATE)
    return freq

def remakePath():
    if not os.path.exists("image2sound") or os.path.isfile("image2sound"):
        try:
            os.system("rm -rf image2sound")
        except:
            pass
        os.system("mkdir image2sound")
    print(
        f"Calculating Hilbert's Curve for p={SIZE}, n=2 with all threads. Note: this may take a while, especially for lower end devices, but you should only see this once per size."
    )
    path = makePath()
    json.dump(path, open(f"image2sound/path{SIZE}.json", "w"))
    return path

if not os.path.exists(f"image2sound/path{SIZE}.json"):
    path = remakePath()
else:
    path = json.load(open(f"image2sound/path{SIZE}.json", "r"))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Expected filename but got nothing")
    if sys.argv[1].endswith(".mp4"):
        video2sound(sys.argv[1], path)
    else:
        image2sound(sys.argv[1], path)
