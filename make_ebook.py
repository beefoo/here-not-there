# -*- coding: utf-8 -*-

# Description: generates set of images that can be printed as a book
# Example usage:
#   python make_ebook.py -mf red,yellow,blue

import argparse
import csv
import math
import os
from PIL import Image, ImageDraw
from PyPDF2 import PdfFileMerger
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-mf', dest="INPUT_MANIFEST_FILES", default="red,yellow,blue", help="Comma-separated list of manifest file names")
parser.add_argument('-md', dest="MANIFEST_DIR", default="manifest/", help="Directory of manifest files")
parser.add_argument('-id', dest="INPUT_DIR", default="pages/", help="Directory of input files/pages")
parser.add_argument('-od', dest="OUTPUT_DIR", default="ebook/", help="Directory for output files")

# init input
args = parser.parse_args()
MANIFEST_DIR = args.MANIFEST_DIR
INPUT_MANIFEST_FILES = [MANIFEST_DIR + f + '.csv' for f in args.INPUT_MANIFEST_FILES.split(",")]
INPUT_DIR = args.INPUT_DIR
OUTPUT_DIR = args.OUTPUT_DIR

# config
sheetW = 8.5
sheetH = 11.0
fileFormat = "PDF"
fileExt = ".pdf"

# ensure output dir exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# read manifest files
manifest_files = []
for mf in INPUT_MANIFEST_FILES:
    with open(mf) as f:
        r = csv.DictReader(f)
        pages = []
        for row in r:
            row["file"] = INPUT_DIR + row["file"]
            pages.append(row)
        # add manifest file
        manifest_files.append({
            "file": mf,
            "name": os.path.basename(mf).split(".")[0],
            "pages": pages
        })

def imagesToPDF(filePaths, pageW, pageH, fileName, fileFormat, dpi):
    img = False

    # Just one file
    if len(filePaths)==1:
        filePath = filePaths[0]
        img = Image.open(filePath)
        warnSizeMismatch(filePath, img.size, (pageW, pageH))

    # more than one file
    elif len(filePaths) > 1:
        # Create a blank image and paste each image on it
        img = Image.new("RGB", (pageW * len(filePaths), pageH), "white")
        for i, filePath in enumerate(filePaths):
            subImg = Image.open(filePath)
            warnSizeMismatch(filePath, subImg.size, (pageW, pageH))
            img.paste(subImg, (i*pageW, 0))

    # Save image
    if img:
        img.save(fileName, fileFormat, dpi=dpi, resolution=dpi[0])
        print "Saved image: %s" % fileName

    return fileName

def mergePages(pages, filename):
    merger = PdfFileMerger()

    for p in pages:
        f = open(p, "rb")
        merger.append(f)

    with open(filename, "wb") as outfile:
        merger.write(outfile)
        print "Saved binder: %s" % filename

def warnSizeMismatch(name, a, b):
    if a[0]!=b[0] or a[1]!=b[1]:
        print "Size mismatch: %s (%s x %s) != (%s x %s)" % (name, a[0], b[0], a[1], b[1])

# read files from directory
for f in manifest_files:
    pages = f["pages"]
    pageCount = len(pages)
    imageCount = int(math.ceil(1.0 * pageCount / 4))

    print "Loading %s pages in %s" % (pageCount, f["name"])
    if pageCount % 2 != 0:
        print "Warning: number of pages is not even"

    # get information about images
    sampleImage = Image.open(pages[0]["file"])
    dpi = sampleImage.info['dpi']
    (pageW, pageH) = sampleImage.size
    print "Page size: %spx x %spx" % (pageW, pageH)
    print "Image DPI: %s x %s" % dpi

    # calculate image sizes
    spreadW = pageW * 2
    print "Creating covers at (%s x %s)" % (pageW, pageH)
    print "Creating spreads at (%s x %s)" % (spreadW, pageH)

    # ensure directory exists
    directory = OUTPUT_DIR + f["name"]
    if not os.path.exists(directory):
        os.makedirs(directory)

    # initialize binders
    binder = []
    binder_combined_covers = []

    # retrieve covers
    frontCover = pages.pop(0)
    backCover = pages.pop()

    # build covers
    frontFile = imagesToPDF([frontCover["file"]], pageW, pageH, directory + "/cover_front" + fileExt, fileFormat, dpi)
    backFile = imagesToPDF([backCover["file"]], pageW, pageH, directory + "/cover_back" + fileExt, fileFormat, dpi)
    binder.append(frontFile)
    combinedCoverFile = imagesToPDF([backCover["file"], frontCover["file"]], pageW, pageH, directory + "/spread_covers" + fileExt, fileFormat, dpi)
    binder_combined_covers.append(combinedCoverFile)

    for i in xrange(0, len(pages), 2):
        outputFile =  directory + "/spread_" + format(int(i/2), '03') + fileExt
        outputFile = imagesToPDF([pages[i]["file"], pages[i+1]["file"]], pageW, pageH, outputFile, fileFormat, dpi)
        binder.append(outputFile)
        binder_combined_covers.append(outputFile)

    binder.append(backFile)

    # Make pdf binders
    if len(binder):
        mergePages(binder, directory + "/" + "binder" + fileExt)
    if len(binder_combined_covers):
        mergePages(binder_combined_covers, directory + "/" + "binder_combined_covers" + fileExt)
