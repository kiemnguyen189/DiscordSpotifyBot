#!/usr/bin/python

# This code sample creates a private playlist in the authorizing user's
# YouTube channel.
# Usage:
#   python youtubeSearchTEST.py --title=<TITLE> --description=<DESCRIPTION>

import argparse
import os
import sys

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
    
CLIENT_SECRETS_FILE = 'client_secret_343978715528-1hsginveor4ornac0trgv6a5qkr3tf9g.apps.googleusercontent.com.json'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
SCOPES = ['https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
    
# Authorize the request and store authorization credentials.
def get_authenticated_service():
  	flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  	credentials = flow.run_console()
  	return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def search_videos(args, youtube):

	# calling the search.list method to 
	# retrieve youtube search results 
	search_keyword = youtube.search().list(q=args.title, part="id, snippet", maxResults=5).execute()

	# extracting the results from search response 
	results = search_keyword.get("items", []) 

	# empty list to store video, 
	# channel, playlist metadata 
	videos = [] 

	#TODO: Fix the SEARCH function to return JSON format of video results
	# extracting required info from each result object 
	for result in results: 
		# video result object 
		if result['id']['kind'] == "youtube# video": 
			videos.append("% s (% s) (% s) (% s)" % (result["snippet"]["title"])) 

	print("Videos:\n", "\n".join(videos), "\n") 

    
def new_playlist(args, youtube):
  
  	body = dict(
    	snippet=dict(
      		title=args.title,
      		description=args.description
    	),
    	status=dict(
      		privacyStatus='private'
    	) 
  	) 
    
  	playlists_insert_response = youtube.playlists().insert(
    	part='snippet,status',
    	body=body
  	).execute()

  	print 'New playlist ID: %s' % playlists_insert_response['id']
  
if __name__ == '__main__':

	FUNCTION_MAP = {'searchVideos': search_videos,
					'newPlaylist': new_playlist}
           
	parser = argparse.ArgumentParser()
	parser.add_argument('function', choices=FUNCTION_MAP.keys())
  	parser.add_argument('-t', '--title',
      	default='Test Playlist',
      	help='The title of the new playlist.')
  	parser.add_argument('-d', '--description',
      	default='A private playlist created with the YouTube Data API.',
		help='The description of the new playlist.')

	args = parser.parse_args()
  	print(args)

	youtube = get_authenticated_service()

	try:
		func = FUNCTION_MAP[args.function]
		func(args, youtube)
		#globals()[sys.argv[1]](sys.argv[2], youtube)
	except HttpError, e:
		print 'An HTTP error %d occurred:\n%s' % (e.resp.status, e.content)