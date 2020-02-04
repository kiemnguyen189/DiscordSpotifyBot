import os
import sys
import json
import csv
import spotipy
import webbrowser
import spotipy.util as util
#from json.decoder import jsonDecodeError

SPOTIPY_CLIENT_ID='73bfdc603198435cbe551387b700b323'
SPOTIPY_CLIENT_SECRET='0f843775243d4be2991bf540ed8dfc44'
SPOTIPY_REDIRECT_URI='https://www.google.co.uk'

# get username from terminal
username = sys.argv[1]
#myFile = sys.stdin()

# My UserID = https://open.spotify.com/user/kiemnguyen189?si=OSdZuuWEQpqjem5rOKDeCg
# My UserID = kiemnguyen189

# PLAYLISTS
apiTest = "https://open.spotify.com/playlist/4f0xpQWvQgYiR2pqFC3K1s?si=rF6FVA1UTxyTeahfj7rGBQ"
best = "https://open.spotify.com/playlist/1alXxqzm5q3cQKpMHQOLsF?si=LObRa4RpRTqddLwQC7fKlg"
songMumboJumbo = "https://open.spotify.com/playlist/2ZF3YfrGT27ubjCse2VMZK?si=jE8gCh1dSy-GqAK0IZxrGw"

# Erase cache and prompt for user permission
try:
    token = util.prompt_for_user_token(username, 
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)
except:
    #os.remove(".cache-%s" % username)
    token = util.prompt_for_user_token(username, 
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)

#----------------------------------------------------------------------------------------------------------------

# Create spotipyObject
spotipyObj = spotipy.Spotify(auth=token)

user = spotipyObj.current_user()
displayName = user['display_name']
followers = user['followers']['total']

playlist1 = spotipyObj.playlist(apiTest, market=None)
total = playlist1['tracks']['total']
print(total)

tracks = playlist1['tracks']['items']   # List of all tracks

playlistDict = {}

# Print ALL names of Tracks in Playlist
for i in range (0, total):
    name = tracks[i]['track']['name']   # Find i'th track in list
    #print(name)
    artists = tracks[i]['track']['artists']
    # Print ALL artists on the Track
    for j in range (0, len(artists)):
        artist = artists[j]['name']
        #print(" - " + artist)
        playlistDict[str(name)] = str(artist)

##
#print(json.dumps(user, sort_keys=True, indent=4))
print(json.dumps(playlist1, sort_keys=True, indent=4))

# Write to CSV File
with open('tracks.csv', mode='wb') as myFile:
    fieldNames = ['name', 'artists']
    tracksWriter = csv.DictWriter(myFile, fieldnames=fieldNames)
    tracksWriter.writeheader()
    for names, artists in playlistDict.items():
        tracksWriter.writerow({'name': names, 'artists': artists})
