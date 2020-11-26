import nltk
nltk.download('wordnet')
import re
from nltk.corpus import wordnet


listofwords=['hello','Streamer', 'info', 'clear' ,'kick', 'ban','game' ,'commands','friends','friendship','sets','player','check','preference','generate','compare','current','overall','detail']
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

keywords['hello']=[]
for synonym in list(listofsynonym['hello']):
  keywords['hello'].append('.*\\b'+synonym+'\\b.*')
keywords['Streamer','favourite','streaming']=[] 
for synonym in list(listofsynonym['Streamer']):
  keywords['Streamer','favourite','streaming'].append('.*\\b'+synonym+'\\b.*')
keywords['info']=[]
for synonym in list(listofsynonym['info']):
  keywords['info'].append('.*\\b'+synonym+'\\b.*')
keywords['clear']=[]
for synonym in list(listofsynonym['clear']):
  keywords['clear'].append('.*\\b'+synonym+'\\b.*')
keywords['kick']=[]
for synonym in list(listofsynonym['kick']):
  keywords['kick'].append('.*\\b'+synonym+'\\b.*')
keywords['ban']=[]
for synonym in list(listofsynonym['ban']):
  keywords['ban'].append('.*\\b'+synonym+'\\b.*')
keywords['game']=[]
for synonym in list(listofsynonym['game']):
  keywords['game'].append('.*\\b'+synonym+'\\b.*')
keywords['commands']=[]
for synonym in list(listofsynonym['commands']):
  keywords['commands'].append('.*\\b'+synonym+'\\b.*')
keywords['friends','when','since']=[]
for synonym in list(listofsynonym['friends']):
  keywords['friends','when','since'].append('.*\\b'+synonym+'\\b.*')
keywords['friendship','friends','playing','games']=[]
for synonym in list(listofsynonym['friends']):
  keywords['friendship','friends','playing','games'].append('.*\\b'+synonym+'\\b.*')
keywords['set','steam','id']=[]
for synonym in list(listofsynonym['sets']):
  keywords['set','steam','id'].append('.*\\b'+synonym+'\\b.*')
keywords['player','count','game','currently','how','many']=[]
for synonym in list(listofsynonym['player']):
  keywords['player','count','game','currently','how','many'].append('.*\\b'+synonym+'\\b.*')
keywords['check','playing','game','streamer']=[]
for synonym in list(listofsynonym['check']):
  keywords['check','playing','game','streamer'].append('.*\\b'+synonym+'\\b.*')
keywords['preference','set','preference']=[]
for synonym in list(listofsynonym['preference']):
  keywords['preference','sets','preference'].append('.*\\b'+synonym+'\\b.*')
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


responses={ 
'hello':[hello],
'Streamer':userFavouriteStreamersStreaming,
'info':info,
'clear' :clear,
'kick':kick,
'ban':ban,
'commands':commands,
'game' :game,
'friends':friendsSince,
'friendship':friendsPlaying,
'sets':setSteamID,
'player':currentPlayerCountFavouriteGames,
'check':checkUserPlayingGame,
'preference':setPreference,
'generate':generateSingleGraph,
'compare':generateCompareGraph,
'current':gameCurrentTopStreamers,
'overall':overallTopStreamerClips,
'detail':currentStreamDetails,
'Undefined':undefined
}

for intent, keys in keywords.items():
  keywordsdictonary[intent]=re.compile('|'.join(keys))
while True:
  userinput = input().lower()
  rename = re.findall(r"[^()0-9-]+", userinput)
  numbers = re.findall('[0-9]+', userinput)
  matchedintent = None 
  for intent,pattern in keywordsdictonary.items():
    if re.search(pattern, userinput):
      matchedintent=intent  
  key='Undefined' 
  if matchedintent in responses:
    key = matchedintent
  responses[hello]()
  responses[Streamer](rename)#name
  responses[info]()
  responses[clear](numbers)#number
  responses[kick](rename)#name
  responses[ban](rename)#name
  responses[commands](rename)
  responses[game](rename)#name
  responses[friends](rename)#name
  responses[friendship](rename)#name
  responses[sets](rename)#name
  responses[player](rename)#name
  responses[preference](rename)#name
  responses[generate](rename)#name
  responses[compare](rename)#name
  responses[current](rename)#name
  responses[overall](rename)#name
  responses[detail](rename)#name
  responses[Undefined]()
