# Instructions

1. Create images that are:
  * PNG format
  * 3.5 x 5.5 in
  * Margins >= 0.25 in
2. Place images in `./pages` directory
3. Create manifest files in comma-separated (.csv) format
  * Columns: name, file ([see example](manifest/test.csv))
  * Ensure number of pages (excluding inner and outer covers) is a multiple of 8
  * First two pages are the front outer and inner cover
  * Last two pages are the back inner and outer cover
  * So if the book has 24 pages, there should be 28 images (24 pages + 2 front + 2 back)
  * Place manifest files in `./manifest` directory
4. Run `python make_book.py -mf <manifestfilename>`
  * You can also compile multiple manifest files at once:

    ```
    python make_book.py -mf <manifestfilename1,manifestfilename2,...>
    ```

  * You can also configure a page gutter (defaults to `0.125` inches):

    ```
    python make_book.py -mf <manifestfilename> -pg <inches>
    ```

5. Print PDF files
  * Under printer settings, select *Actual Size*
  * If printer settings have margins, make them all 0
  * For Duplex Printing:
    * Print `binder_covers.pdf` on cardstock for covers
    * Print `binder.pdf` on regular paper for pages
  * For Regular Printing
    * Print `cover_000.pdf` on cardstock, flip along horizontal axis, print `cover_001.pdf`
    * Print `binder_even.pdf` on regular paper, flip along horizontal axis, print `binder_odd.pdf`
6. Cut sheets along vertical guides, then horizontal guides
7. Stack sheets recto face-up, in order
8. Staple
