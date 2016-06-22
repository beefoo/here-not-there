# -*- coding: utf-8 -*-

# Description: generates set of images that can be printed as a book
# Example usage:
#   python make_book.py manifest/red.csv,manifest/yellow.csv,manifest/blue.csv pages/ print/

import csv
import math
import os
from PIL import Image, ImageDraw
from PyPDF2 import PdfFileMerger
import sys

# input
if len(sys.argv) < 3:
    print "Usage: %s <commas-separated paths to manifest files> <input directory> <output directory>" % sys.argv[0]
    sys.exit(1)
INPUT_MANIFEST_FILES = sys.argv[1]
INPUT_DIR = sys.argv[2]
OUTPUT_DIR = sys.argv[3]

# config
sheetW = 8.5
sheetH = 11.0
fileFormat = "PDF"
fileExt = ".pdf" # png

# ensure output dir exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# read manifest files
manifest_files = []
INPUT_MANIFEST_FILES = INPUT_MANIFEST_FILES.split(",")
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

        # Create a blank image
        imageBase = Image.new("RGB", (imageW, imageH), "white")

        base_i = i * 2 - i % 2
        file_indices = [max_i - base_i, base_i, max_i - (base_i+2), base_i+2]
        if i % 2 == 1:
            file_indices = [base_i, max_i - base_i, base_i+2, max_i - (base_i+2)]


        offset_x = 0
        if i % 2 > 0:
            offset_x = imageW - pageW * 2
        x = offset_x
        y = 0
        for fi in file_indices:
            page = pages[fi]
            image = Image.open(page["file"])

            # Make warnings if size mismatch
            (thisW, thisH) = image.size
            if thisW != pageW or thisH != pageH:
                print "Warning: size mismatch for %s (%s x %s)" % (page["file"], thisW, thisH)

            imageBase.paste(image, (x, y))

            # place in a grid of 4
            x += pageW
            if x >= pageW * 2:
                x = offset_x
                y += pageH

        # Put guide lines on every other image
        if i % 2 == 0:
            draw = ImageDraw.Draw(imageBase)
            margin = pxPerInch * 0.25
            x = pageW * 2 + 1
            w = pxPerInch * 0.5
            draw.line([(x, margin), (x, w)], fill=128)
            draw.line([(x, imageH-margin), (x, imageH-w)], fill=128)
            draw.line([(margin, pageH), (w, pageH)], fill=128)
            draw.line([(imageW-margin, pageH), (imageW-w, pageH)], fill=128)
            del draw

        # Save the image
        page_type = "page"
        if i <= 1:
            page_type = "cover"
        outputFile =  directory + "/" + page_type + "_" + format(i, '03') + fileExt
        imageBase.save(outputFile, fileFormat, dpi=dpi)
        print "Saved image: %s" % outputFile

        # Build binders
        if i > 1:
            binder.append(outputFile)
            if i % 2 == 0:
                binder_even.append(outputFile)
            else:
                binder_odd.append(outputFile)
        else:
            binder_covers.append(outputFile)

    # Make pdf binders
    mergePages(binder, directory + "/" + "binder" + fileExt)
    mergePages(binder_even, directory + "/" + "binder_even" + fileExt)
    mergePages(binder_odd, directory + "/" + "binder_odd" + fileExt)
    mergePages(binder_covers, directory + "/" + "binder_covers" + fileExt)
