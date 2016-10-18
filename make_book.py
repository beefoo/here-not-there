# -*- coding: utf-8 -*-

# Description: generates set of images that can be printed as a book
# Example usage:
#   python make_book.py -mf red,yellow,blue

import argparse
import csv
import math
import os
from PIL import Image, ImageDraw
from PyPDF2 import PdfFileMerger
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-bd', dest="BASE_DIR", default="", help="Base directory")
parser.add_argument('-mf', dest="INPUT_MANIFEST_FILES", default="red,yellow,blue", help="Comma-separated list of manifest file names")
parser.add_argument('-md', dest="MANIFEST_DIR", default="manifest/", help="Directory of manifest files")
parser.add_argument('-id', dest="INPUT_DIR", default="pages/", help="Directory of input files/pages")
parser.add_argument('-od', dest="OUTPUT_DIR", default="print/", help="Directory for output files")
parser.add_argument('-g', dest="GUIDES", default=True, type=bool, help="Show or hide guides")
parser.add_argument('-cg', dest="COVER_GUTTER", default=0.25, type=float, help="Cover gutter in inches")
parser.add_argument('-pg', dest="PAGE_GUTTER", default=0.125, type=float, help="Page gutter in inches")
parser.add_argument('-pgi', dest="PAGE_GUTTER_INCREMENT", default=0.0, type=float, help="Page gutter increment in inches")

# init input
args = parser.parse_args()
BASE_DIR = args.BASE_DIR
MANIFEST_DIR = BASE_DIR + args.MANIFEST_DIR
INPUT_MANIFEST_FILES = [MANIFEST_DIR + f + '.csv' for f in args.INPUT_MANIFEST_FILES.split(",")]
INPUT_DIR = BASE_DIR + args.INPUT_DIR
OUTPUT_DIR = BASE_DIR + args.OUTPUT_DIR
GUIDES = args.GUIDES
COVER_GUTTER = args.COVER_GUTTER
PAGE_GUTTER = args.PAGE_GUTTER
PAGE_GUTTER_INCREMENT = args.PAGE_GUTTER_INCREMENT

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
        # Duplicate first and last two pages which are the cover pages
        first = pages[0]
        second = pages[1]
        second_to_last = pages[-2]
        last = pages[-1]
        pages.insert(0, second)
        pages.insert(0, first)
        pages.append(second_to_last)
        pages.append(last)
        # add manifest file
        manifest_files.append({
            "file": mf,
            "name": os.path.basename(mf).split(".")[0],
            "pages": pages
        })

def mergePages(pages, filename):
    merger = PdfFileMerger()

    for p in pages:
        f = open(p, "rb")
        merger.append(f)

    with open(filename, "wb") as outfile:
        merger.write(outfile)
        print "Saved binder: %s" % filename

# read files from directory
for f in manifest_files:
    pages = f["pages"]
    pageCount = len(pages)
    imageCount = int(math.ceil(1.0 * pageCount / 4))

    print "Loading %s pages in %s" % (pageCount, f["name"])
    if pageCount % 4 != 0:
        print "Warning: number of pages is not a multiple of 4"
    elif pageCount % 8 != 0:
        print "Warning: number of pages is not a multiple of 8"

    # get information about images
    sampleImage = Image.open(pages[0]["file"])
    dpi = sampleImage.info['dpi']
    (pageW, pageH) = sampleImage.size
    print "Page size: %spx x %spx" % (pageW, pageH)
    print "Image DPI: %s x %s" % dpi

    # calculate image sizes
    imageW = pageW * 2
    imageH = pageH * 2
    imageRatio = (1.0*imageW/imageH)
    sheetRatio = (1.0*sheetW/sheetH)
    if imageRatio < sheetRatio:
        pxPerInch = 1.0 * imageH / sheetH
        imageW = int(round(sheetW * pxPerInch))
    elif imageRatio > sheetRatio:
        pxPerInch = 1.0 * imageW / sheetW
        imageH = int(round(sheetH * pxPerInch))
    print "Creating images at (%s x %s)" % (imageW, imageH)

    # ensure directory exists
    directory = OUTPUT_DIR + f["name"]
    if not os.path.exists(directory):
        os.makedirs(directory)

    # initialize binders
    binder = []
    binder_odd = []
    binder_even = []
    binder_covers = []

    max_i = pageCount - 1
    for i in range(imageCount):

        # Determine what kind of image this is
        isCover = False
        if i <= 1:
            isCover = True
        isPage = not isCover
        isEven = False
        if i % 2 == 0:
            isEven = True
        isOdd = not isEven

        # Create a blank image
        imageBase = Image.new("RGB", (imageW, imageH), "white")

        # Determine which pages go on this image
        base_i = i * 2 - i % 2
        page_indices = [max_i - base_i, base_i, max_i - (base_i+2), base_i+2]
        if isOdd:
            page_indices = [base_i, max_i - base_i, base_i+2, max_i - (base_i+2)]

        # Determine the gutter
        gutterMultiplier = int((imageCount-1-i) / 2)
        gutter = PAGE_GUTTER + PAGE_GUTTER_INCREMENT * gutterMultiplier
        if isCover:
            gutter = COVER_GUTTER
        gutter *= pxPerInch

        # Odd pages should have space on left rather than right
        offset_x = 0
        if isOdd:
            offset_x = int(round(imageW - pageW * 2 - gutter))

        # Outer covers should be centered
        adjustedGutter = gutter
        if isCover and i < 1:
            offset_x =  int(round(gutter * 0.25))
            adjustedGutter =  int(round(gutter * 0.5))

        print "Building image with pages (%s) and gutter (%spx)" % (", ".join([str(p) for p in page_indices]), gutter)

        # Paste the pages into the image
        x = offset_x
        y = 0
        for pi in page_indices:
            page = pages[pi]

            # Paste image
            image = Image.open(page["file"])
            imageBase.paste(image, (x, y))

            # Make warnings if size mismatch
            (thisW, thisH) = image.size
            if thisW != pageW or thisH != pageH:
                print "Warning: size mismatch for %s (%s x %s)" % (page["file"], thisW, thisH)

            # place in a grid of 4
            x += pageW + adjustedGutter
            if x >= pageW * 2 + adjustedGutter:
                x = offset_x
                y += pageH
            x = int(round(x))

        # Put guide lines on every other image
        if isEven and GUIDES:
            draw = ImageDraw.Draw(imageBase)
            margin = pxPerInch * 0.375 # the margin of the image
            x = int(round(pageW * 2 + gutter + 1)) # the x position of right vertical guides
            w = pxPerInch * 0.5 # the length of guide
            draw.line([(x, margin), (x, w)], fill=128) # top, right, vertical
            draw.line([(x, imageH-margin), (x, imageH-w)], fill=128) # bottom, right, vertical
            draw.line([(margin, pageH), (w, pageH)], fill=128) # center, left, horizontal
            draw.line([(x, pageH), (x-w+margin, pageH)], fill=128) # center, right, horizontal
            del draw

        # Save the image
        page_type = "page"
        if isCover:
            page_type = "cover"
        outputFile =  directory + "/" + page_type + "_" + format(i, '03') + fileExt
        imageBase.save(outputFile, fileFormat, dpi=dpi, resolution=dpi[0])
        print "Saved image: %s" % outputFile

        # Build binders
        if isPage:
            binder.append(outputFile)
            if isEven:
                binder_even.append(outputFile)
            else:
                binder_odd.append(outputFile)
        else:
            binder_covers.append(outputFile)

    # Make pdf binders
    if len(binder):
        mergePages(binder, directory + "/" + "binder" + fileExt)
    if len(binder_even):
        mergePages(binder_even, directory + "/" + "binder_even" + fileExt)
    if len(binder_odd):
        mergePages(binder_odd, directory + "/" + "binder_odd" + fileExt)
    if len(binder_covers):
        mergePages(binder_covers, directory + "/" + "binder_covers" + fileExt)
