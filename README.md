# FacebookEXIF
Puts the EXIF data back into photos exported from Facebook - including description, location and most importantly, date taken. To get started, you'll first need to [download your Facebook data in JSON format](https://www.facebook.com/help/1701730696756992).

This is inspired by the excellent project over at [AddShore](https://addshore.com/2020/04/add-exif-data-back-to-facebook-images-0-10/), but that didn't seem to work on my Mac, so I wrote a clone in Python.

There's only one requirement to run it - you must have installed [ExifTool](https://exiftool.org/) first - if you're on Mac, just download the MacOS Package and run it. Then edit the `facebook_fix_exif.py` script to point to your downloaded and unzipped Facebook JSON repo:

```python

PATH_TO_FACEBOOK_EXPORT = '/Users/jamiebrown/Downloads/facebook-jamiebrown'

```

You can then run it:

```
python facebook_fix_exif.py

```

It will run through and add the EXIF tags where possible. Note that it edits the files in-place - so if this is the only copy of your photos then make sure you have a backup first.

The script probably will work on Windows if you have Python installed, but may need some tweaks to paths etc.