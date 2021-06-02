# FacebookEXIF
This simple Python script runs easily on Mac and puts the EXIF data back into photos exported from Facebook - including description, location and most importantly, date taken. To get started, you'll first need to [download your Facebook data in JSON format](https://www.facebook.com/help/1701730696756992) and unzip it.

This is inspired by the excellent project over at [AddShore](https://addshore.com/2020/04/add-exif-data-back-to-facebook-images-0-10/), which is written in Java and requires a JRE. That didn't seem to work on my Mac, so I wrote a basic clone in Python.

## Prerequisites

There's only one technical requirement - you must have installed [ExifTool](https://exiftool.org/) first. If you're on Mac, just download the MacOS Package and run the installer.

You also must have downloaded your Facebook data in JSON format - the default is HTML format and is not supported by this script.

## Usage

Edit the `facebook_fix_exif.py` script and update the following line to point to your downloaded and unzipped Facebook JSON repo:

```python
PATH_TO_FACEBOOK_EXPORT = '/Users/jamiebrown/Downloads/facebook-jamiebrown'
```

You can then run the script in the command line:

```bash
python facebook_fix_exif.py
```

The script will run through your photos and add the EXIF tags where possible. Note that it edits the files in-place - so if this is the only copy of your photos then make sure you have a backup first.

The script probably will work on Windows if you have Python installed, but may need some tweaks to paths etc.