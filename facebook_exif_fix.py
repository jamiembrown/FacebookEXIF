import os
import json
from datetime import datetime
import subprocess

PATH_TO_FACEBOOK_EXPORT = '/Users/jamesbrown/Downloads/facebook-jamesbrown'
PATH_TO_EXIFTOOL = '/usr/local/bin/exiftool'

# Basic checks on the input

if PATH_TO_FACEBOOK_EXPORT.endswith('/'):
    PATH_TO_FACEBOOK_EXPORT = PATH_TO_FACEBOOK_EXPORT[:-1]

if not os.path.exists(PATH_TO_FACEBOOK_EXPORT):
    print "Facebook export does not exist at %s" % (PATH_TO_FACEBOOK_EXPORT)
    exit()

if not os.path.exists(PATH_TO_EXIFTOOL):
    print "exiftool was not found at %s" % (PATH_TO_EXIFTOOL)
    exit()

if not os.path.exists(PATH_TO_FACEBOOK_EXPORT + '/photos_and_videos'):
    print "No photos and videos found in export"
    exit()

if not os.path.exists(PATH_TO_FACEBOOK_EXPORT + '/posts'):
    print "No posts found in export"
    exit()

if not os.path.exists(PATH_TO_FACEBOOK_EXPORT + '/posts/album'):
    print "No albums found in export"
    exit()

# Get files in core dirs

album_files = os.listdir(PATH_TO_FACEBOOK_EXPORT + '/posts/album')

if len(album_files) == 0:
    print "No album JSON files found"
    exit()

post_files = os.listdir(PATH_TO_FACEBOOK_EXPORT + '/posts')

if len(post_files) == 0:
    print "No post JSON files found"
    exit()

# Extract photo data

photos = {}

# Loop through all post JSON data

for post_file in post_files:
    full_path = PATH_TO_FACEBOOK_EXPORT + '/posts/' + post_file
    if not post_file.endswith('.json') or not os.path.isfile(full_path):
        continue
    with open(full_path) as file_content:
        data = json.load(file_content)
        for post in data:
            if 'attachments' not in post:
                continue
            matched_media = []
            for attachment in post['attachments']:
                for attachment_data in attachment['data']:
                    if 'media' in attachment_data:
                        if attachment_data['media']['uri'] not in photos:
                            photos[attachment_data['media']['uri']] = attachment_data['media']
                        matched_media.append(attachment_data['media']['uri'])
            for attachment in post['attachments']:
                for attachment_data in attachment['data']:
                    if 'place' in attachment_data:
                        for matched_media_item in matched_media:
                            photos[matched_media_item]['place'] = attachment_data['place']

# Loop through all album JSON data

for album_file in album_files:
    full_path = PATH_TO_FACEBOOK_EXPORT + '/posts/album/' + album_file
    if not album_file.endswith('.json') or not os.path.isfile(full_path):
        continue
    with open(full_path) as file_content:
        data = json.load(file_content)
        album_name = data['name']
        for album_photo in data['photos']:
            if album_photo['uri'] not in photos:
                photos[album_photo['uri']] = album_photo
            if 'albums' not in photos[album_photo['uri']]:
                photos[album_photo['uri']]['albums'] = []
            if album_name not in photos[album_photo['uri']]['albums']:
                photos[album_photo['uri']]['albums'].append(album_name)

for photo_uri in photos:
    photo = photos[photo_uri]
    created_timestamp = photo['creation_timestamp']

    if 'media_metadata' in photo and 'photo_metadata' in photo['media_metadata'] and 'exif_data' in photo['media_metadata']['photo_metadata'] and 'taken_timestamp' in photo['media_metadata']['photo_metadata']['exif_data'][0]:
        created_timestamp = photo['media_metadata']['photo_metadata']['exif_data'][0]['taken_timestamp']

    created_date = datetime.utcfromtimestamp(created_timestamp).strftime('%Y-%m-%d %H:%M:%S').replace('-', ':')

    params = []
    params.append('-AllDates="' + created_date + '"')
    params.append('-DateTimeOriginal="' + created_date + '"')

    if 'place' in photo and 'coordinate' in photo['place'] and 'latitude' in photo['place']['coordinate']:
        params.append('-gpslatitude="' + str(photo['place']['coordinate']['latitude']) + '"')
        params.append('-gpslatituderef="' + str(photo['place']['coordinate']['latitude']) + '"')
        params.append('-gpslongitude="' + str(photo['place']['coordinate']['longitude']) + '"')
        params.append('-gpslongituderef="' + str(photo['place']['coordinate']['longitude']) + '"')

    if 'description' in photo:
        params.append('-ImageDescription="' + photo['description'].replace('"', '') + '"')
        params.append('-iptc:Caption-Abstract="' + photo['description'].replace('"', '') + '"')
    elif 'title' in photo:
        params.append('-ImageDescription="' + photo['title'].replace('"', '') + '"')
    elif 'albums' in photo and len(photo['albums']) > 0:
        params.append('-ImageDescription="' + photo['albums'][0].replace('"', '') + '"')

    if 'title' in photo:
        params.append('-iptc:ObjectName="' + photo['title'].replace('"', '') + '"')


    keywords = []

    if 'albums' in photo:
        for album in photo['albums']:
            keywords.append(album)

    if len(keywords) > 0:
        params.append('-iptc:Keywords="' + (','.join(keywords)).replace('"', '') + '"')

    command = ' '.join(params)

    full_command = PATH_TO_EXIFTOOL + ' ' + command + ' -overwrite_original ' + PATH_TO_FACEBOOK_EXPORT + '/' + photo_uri
    process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE)
    process.wait()

    if process.returncode != 0:
        print "ERROR returned by exiftool"
        exit()
