import nltk
import re
from nltk.corpus import wordnet
from Discord_chatbot.Process_Function_H import *


listofwords=['hello','Streamer', 'info', 'clear' ,'kick', 'ban','game' ,'commands','friends','friendship','set','player','check','preference','generate','compare','current','overall','detail']
listofsynonym={}
keywords={}
keywordsdictonary={}



for word in listofwords:
  synonyms=[]
  for synonym in wordnet.synsets(word):
    for x in synonym.lemmas():
      name = re.sub('[^a-zA-Z0-9 \n\.]', ' ', x.name())
      synonyms.append(name)
  listofsynonym[word]=set(synonyms)

keywords['friends','when','since']=[]
for synonym in list(listofsynonym['friends']):
  keywords['friends','when','since'].append('.*\\b'+synonym+'\\b.*')
keywords['friendship','friends','playing','games']=[]
for synonym in list(listofsynonym['friends']):
  keywords['friendship','friends','playing','games'].append('.*\\b'+synonym+'\\b.*')
keywords['set','steam','id']=[]
for synonym in list(listofsynonym['set']):
  keywords['set','steam','id'].append('.*\\b'+synonym+'\\b.*')
keywords['player','count','game','currently','how','many']=[]
for synonym in list(listofsynonym['player']):
  keywords['player','count','game','currently','how','many'].append('.*\\b'+synonym+'\\b.*')
keywords['check','playing','game','streamer']=[]
for synonym in list(listofsynonym['check']):
  keywords['check','playing','game','streamer'].append('.*\\b'+synonym+'\\b.*')
keywords['preference','set','preference']=[]
for synonym in list(listofsynonym['preference']):
  keywords['preference','set','preference'].append('.*\\b'+synonym+'\\b.*')
keywords['generate','graph','viewer','player','single']=[]
for synonym in list(listofsynonym['generate']):
  keywords['generate','graph','viewer','player','single'].append('.*\\b'+synonym+'\\b.*')
keywords['compare','graphs','generate']=[]
for synonym in list(listofsynonym['compare']):
  keywords['compare','graphs','generate'].append('.*\\b'+synonym+'\\b.*')
keywords['current','top','streamer']=[]
for synonym in list(listofsynonym['current']):
  keywords['current','top','streamer'].append('.*\\b'+synonym+'\\b.*')
keywords['overall','top','streamer']=[]
for synonym in list(listofsynonym['overall']):
  keywords['overall','top','streamer'].append('.*\\b'+synonym+'\\b.*')
keywords['detail','current','stream']=[]
for synonym in list(listofsynonym['detail']):
  keywords['detail','current','stream'].append('.*\\b'+synonym+'\\b.*')


def response_proccessing(input, id):
  responses = {
    'hello': hello,
    'Streamer': userFavouriteStreamersStreaming,
    'info': info,
    'commands': commands,
    'game': game,
    'friends': friendsSince,
    'friendship': friendsPlaying,
    'set': setSteamID,
    'player': currentPlayerCountFavouriteGames(id),
    'check': checkUserPlayingGame,
    'preference': setPreference,
    'generate': generateSingleGraph,
    'compare': generateCompareGraph,
    'current': gameCurrentTopStreamers,
    'overall': overallTopStreamerClips,
    'detail': currentStreamDetails,
    'Undefined': undefined
  }
  for intent, keys in keywords.items():
    keywordsdictonary[intent]=re.compile('|'.join(keys))
  while True:
    userinput = input.lower()
    matchedintent = None
    for intent,pattern in keywordsdictonary.items():
      if re.search(pattern, userinput):
        matchedintent=intent
    key='Undefined'
    if matchedintent in responses:
      key = matchedintent
    responses[key]()
