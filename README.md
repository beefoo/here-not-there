# Instructions

1. Create images that:
  * PNG format
  * 3.5 x 5.5in
  * Margins >= 0.25in
2. Create manifest files in CSV format
  * Columns: name, file
  * Ensure number of pages (excluding inner and outer covers) is a multiple of 8
  * First two pages are the front outer and inner cover
  * Last two pages are the back inner and outer cover
3. Run `python make_book.py -mf <manifestfilename1,manifestfilename2,...>`
4. Print PDF files
  * Under printer settings, select *Actual Size*
  * If printer settings have margins, make them all 0
  * For Duplex Printing:
    * Print `binder_covers.pdf` on cardstock for covers
    * Print `binder.pdf` on regular paper for pages
  * For Regular Printing
    * Print `cover_000.pdf` on cardstock, flip along horizontal axis, print `cover_001.pdf`
    * Print `binder_even.pdf` on regular paper, flip along horizontal axis, print `binder_odd.pdf`
5. Cut sheets along vertical guides, then horizontal guides
6. Stack sheets recto face-up, in order
7. Staple
