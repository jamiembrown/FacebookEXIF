#!/usr/bin/python

# Simple python script to update your exported Facebook photos with correct EXIF data.
# Find it on GIT here: https://github.com/jamiembrown/FacebookEXIF

import os
import json
from datetime import datetime
import subprocess

# TODO: Update this to point to your unzipped Facebook export - must be a JSON export:
PATH_TO_FACEBOOK_EXPORT = '/Users/jamesbrown/Downloads/facebook-thejamiebrown'

# This is where exiftool is - install it from https://exiftool.org/.
# If you're on a Mac, this probably doesn't need to change:
PATH_TO_EXIFTOOL = '/usr/local/bin/exiftool'

# You should now be able to run "python facebook_exif_fix.py" to update your photos.

# Basic checks on the input

if PATH_TO_FACEBOOK_EXPORT.endswith('/'):
    PATH_TO_FACEBOOK_EXPORT = PATH_TO_FACEBOOK_EXPORT[:-1]

if not os.path.exists(PATH_TO_FACEBOOK_EXPORT):
    print("Facebook export does not exist at %s" % (PATH_TO_FACEBOOK_EXPORT))
    print("")
    print("Please edit the script to point PATH_TO_FACEBOOK_EXPORT to the location of your unzipped Facebook export.")
    print("")
    exit()

if not os.path.exists(PATH_TO_EXIFTOOL):
    print("exiftool was not found at %s" % (PATH_TO_EXIFTOOL))
    print("")
    print("Please install exiftool from https://exiftool.org/ before running this.")
    print("If you have installed exiftool then update PATH_TO_EXIFTOOL in the script to point to the correct location.")
    print("(Tip: try \"which exiftool\" to find out where it is.)")
    print("")
    exit()

if not os.path.exists(PATH_TO_FACEBOOK_EXPORT + '/photos_and_videos'):
    print("No photos and videos found in export")
    exit()

if not os.path.exists(PATH_TO_FACEBOOK_EXPORT + '/posts'):
    print("No posts found in export")
    exit()

if not os.path.exists(PATH_TO_FACEBOOK_EXPORT + '/posts/album'):
    print("No albums found in export")
    exit()

# Get files in core dirs

album_files = os.listdir(PATH_TO_FACEBOOK_EXPORT + '/posts/album')

if len(album_files) == 0:
    print("No album JSON files found")
    exit()

post_files = os.listdir(PATH_TO_FACEBOOK_EXPORT + '/posts')

if len(post_files) == 0:
    print("No post JSON files found")
    exit()

# We're going to put all photo data into a dictionary

photos = {}

# Loop through all posts in the Facebook data to extract photos and properties

for post_file in post_files:

    # Is this a JSON file?

    full_path = PATH_TO_FACEBOOK_EXPORT + '/posts/' + post_file
    if not post_file.endswith('.json') or not os.path.isfile(full_path):
        continue

    # Open it and convert it to a JSON object

    with open(full_path) as file_content:
        data = json.load(file_content)

        # Loop through each post

        for post in data:
            if 'attachments' not in post:
                continue

            # Extract photos in the current post

            matched_media = []
            for attachment in post['attachments']:
                for attachment_data in attachment['data']:
                    if 'media' in attachment_data:
                        if attachment_data['media']['uri'] not in photos:
                            photos[attachment_data['media']['uri']] = attachment_data['media']
                        matched_media.append(attachment_data['media']['uri'])

            # Extract geographic info from the current post and attach to photos

            for attachment in post['attachments']:
                for attachment_data in attachment['data']:
                    if 'place' in attachment_data:
                        for matched_media_item in matched_media:
                            photos[matched_media_item]['place'] = attachment_data['place']

# Loop through all entries in the Facebook albums to extract photos and properties

for album_file in album_files:

    # Is this a JSON file?

    full_path = PATH_TO_FACEBOOK_EXPORT + '/posts/album/' + album_file
    if not album_file.endswith('.json') or not os.path.isfile(full_path):
        continue

    # Open it and convert to a JSON object

    with open(full_path) as file_content:
        data = json.load(file_content)

        # Extract photos from the current album

        album_name = data['name']
        for album_photo in data['photos']:
            if album_photo['uri'] not in photos:
                photos[album_photo['uri']] = album_photo

            # Tag photo with the album name

            if 'albums' not in photos[album_photo['uri']]:
                photos[album_photo['uri']]['albums'] = []
            if album_name not in photos[album_photo['uri']]['albums']:
                photos[album_photo['uri']]['albums'].append(album_name)

# Did we get anything? If not, it's probably not a JSON export

if len(photos) == 0:
    print("No photos found in Facebook export.")
    print("")
    print("Are you sure this is a JSON export? Make sure you selected JSON format when creating your Facebook download - the default is HTML and is not supported by this script.")
    print("")
    exit()

# We've got a list of photos now, let's loop through them and add EXIF

for photo_uri in photos:
    photo = photos[photo_uri]
    created_timestamp = photo['creation_timestamp']

    # If there's a taken_timestamp EXIF tag, use that instead of the Facebook created tag

    if 'media_metadata' in photo and 'photo_metadata' in photo['media_metadata'] and 'exif_data' in photo['media_metadata']['photo_metadata'] and 'taken_timestamp' in photo['media_metadata']['photo_metadata']['exif_data'][0]:
        created_timestamp = photo['media_metadata']['photo_metadata']['exif_data'][0]['taken_timestamp']

    # Convert the date to UTC

    created_date = datetime.utcfromtimestamp(created_timestamp).strftime('%Y-%m-%d %H:%M:%S').replace('-', ':')

    # Start compiling a list of params to send to exiftool

    params = []
    params.append('-AllDates="' + created_date + '"')
    params.append('-DateTimeOriginal="' + created_date + '"')

    # If there's GPS data, add that

    if 'place' in photo and 'coordinate' in photo['place'] and 'latitude' in photo['place']['coordinate']:
        params.append('-gpslatitude="' + str(photo['place']['coordinate']['latitude']) + '"')
        params.append('-gpslatituderef="' + str(photo['place']['coordinate']['latitude']) + '"')
        params.append('-gpslongitude="' + str(photo['place']['coordinate']['longitude']) + '"')
        params.append('-gpslongituderef="' + str(photo['place']['coordinate']['longitude']) + '"')

    # See if we can get some sort of description from the photo

    if 'description' in photo:
        params.append('-ImageDescription="' + photo['description'].replace('"', '') + '"')
        params.append('-iptc:Caption-Abstract="' + photo['description'].replace('"', '') + '"')
    elif 'title' in photo:
        params.append('-ImageDescription="' + photo['title'].replace('"', '') + '"')
    elif 'albums' in photo and len(photo['albums']) > 0:
        params.append('-ImageDescription="' + photo['albums'][0].replace('"', '') + '"')

    if 'title' in photo:
        params.append('-iptc:ObjectName="' + photo['title'].replace('"', '') + '"')

    # Add album names as keywords

    keywords = []

    if 'albums' in photo:
        for album in photo['albums']:
            keywords.append(album)

    if len(keywords) > 0:
        params.append('-iptc:Keywords="' + (','.join(keywords)).replace('"', '') + '"')

    # Generate the full exiftool command

    command = PATH_TO_EXIFTOOL + ' ' + ' '.join(params) + ' -overwrite_original ' + PATH_TO_FACEBOOK_EXPORT + '/' + photo_uri

    # Launch exiftool and wait

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()

    # If the process returned a non-zero response (i.e. an error) break

    if process.returncode != 0:
        print("ERROR returned by exiftool for %s" % (photo_uri))
        exit()

    print("Added EXIF for %s" % (photo_uri))

# We're all done!

print("")
print("Completed %d photos" % (len(photos)))
print("Your EXIF tagged photos are in %s" % (PATH_TO_FACEBOOK_EXPORT + '/photos_and_videos/'))
print("Have a nice day!")