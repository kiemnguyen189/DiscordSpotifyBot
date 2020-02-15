#!/usr/bin/python

# This code sample creates a private playlist in the authorizing user's
# YouTube channel.
# Usage:
#   python youtubeSearchTEST.py function --title=<TITLE> --description=<DESCRIPTION>

import argparse
import os
import sys
import json
import csv

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

MAX_RESULTS = 5
    
# Authorize the request and store authorization credentials.
def get_authenticated_service():
  	flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  	credentials = flow.run_console()
  	return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

#TODO: search is complete, now COMBINE to read EACH CSV row, get top result (not channel), add to playlist

# Search top MAX_RESULTS on YouTube for videos relevent to -t=KEYWORD using terminal
def searchVideosCMD(args, youtube):

	print(args)

	# calling the search.list method to 
	# retrieve youtube search results 
	search_keyword = youtube.search().list(q=args.title, part="id, snippet", maxResults=MAX_RESULTS).execute()
	#all = youtube.search().list(q=args.title, part=)

	# extracting the results from search response 
	results = search_keyword.get('items', []) 	# RETURNS: List of Dictionaries (List[{channel}, {res1}, {res2}, ...])
	print(json.dumps(results, sort_keys=True, indent=4))

	# empty list to store video
	#videos = [] 
	videosDict = {}

	# resDict = 1 Element of list 'results', i.e. results[0] = channel, results[1] = 1st results, etc...
	for resDict in results:
		if resDict['id']['kind'] == 'youtube#video':
			result = resDict['snippet']['title'].encode('utf-8')
			#videos.append(str(result))
			videosDict[result] = str(resDict['id']['videoId'])
	#print(videos)
	#print(videosDict)	
	return videosDict

# Searches videos using keyword argument
def searchVideo(word):
	# calling the search.list method to 
	# retrieve youtube search results 
	search_keyword = youtube.search().list(q=word, part="id, snippet", maxResults=2).execute()

	# extracting the results from search response 
	results = search_keyword.get('items', []) 	# RETURNS: List of Dictionaries (List[{channel}, {res1}])
	print(json.dumps(results, sort_keys=True, indent=4))

	# empty list to store video
	videosDict = {}

	# resDict = 1 Element of list 'results', i.e. results[0] = channel, results[1] = 1st results, etc...
	
	if results[1]['id']['kind'] == 'youtube#video':
		result = results['snippet']['title'].encode('utf-8')
		videosDict[result] = str(results['id']['videoId'])
	
	return videosDict

# Search top video for each CSV item
def searchCSV(args, youtube):

	playlist = newPlaylist(args, youtube)

	with open(str(args.title)+".csv") as csvFile:
		reader = csv.reader(csvFile, delimiter=',')
		count = 0
		for row in reader:
			if count != 0:
				vidId = searchVideo(row[0] + " " + row[1])
				print(vidId)
				body = createBody(playlist, vidId)
				insertVideos = youtube.playlistItems().insert(
					part='snippet',
					body=body
				).execute()
			count += 1

# Creates a body Dict structure for adding to a playlist
def createBody(playlist, vidId):
	body = dict(
		snippet=dict(
			playlistId=playlist,
			resourceId=dict(
				kind='youtube#video',
				videoId=list(vidId.values())[0]
			)
		)
	)
	return body


# Create a new playlist on YouTube account with title -t=TITLE and description -d=DESCRIPTION
def newPlaylist(args, youtube):

	print(args)
  
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
	return playlists_insert_response['id']


#"""
# Add list of songs to a playlist
def addToPlaylist(args, youtube):

	print(args)

	# Retrieve playlistID 
	playlist = newPlaylist(args, youtube)
	videoDict = searchVideos(args, youtube)
	print(list(videoDict.values())[0])	# Video ID

	# Add a video to playlist
	body = dict(
		snippet=dict(
			playlistId=playlist,
			resourceId=dict(
				kind='youtube#video',
				videoId=list(videoDict.values())[0]
			)
		)
	)

	insertVideos = youtube.playlistItems().insert(
		part='snippet',
		body=body
	).execute()
#"""


def newAndAdd(args, youtube):
	print("")



if __name__ == '__main__':

	# Dictionary of function commands to functions
	FUNCTION_MAP = {'searchVideosCMD': searchVideosCMD,
					'newPlaylist': newPlaylist,
					'addToPlaylist': addToPlaylist,
					'newAndAdd': newAndAdd,
					'searchCSV': searchCSV}
           
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
	except HttpError, e:
		print 'An HTTP error %d occurred:\n%s' % (e.resp.status, e.content)