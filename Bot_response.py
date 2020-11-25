import nltk
nltk.download()
import re
from nltk.corpus import wordnet


listofwords=['hello','Streamer', 'info', 'clear' ,'kick', 'ban','game' ,'commands','friends']
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

keywords['greet']=[]
for synonym in list(listofsynonym['hello']):
  keywords['greet'].append('.*\\b'+synonym+'\\b.*')
keywords['Streamer']=[]
for synonym in list(listofsynonym['Streamer']):
  keywords['Streamer'].append('.*\\b'+synonym+'\\b.*')
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
keywords['friends']=[]
for synonym in list(listofsynonym['friends']):
  keywords['friends'].append('.*\\b'+synonym+'\\b.*')


responses={ 
'greet':bruh,
'Streamer':function,
'info':function,
'clear' :function,
'kick':function,
'ban':function,
'commands':function,
'game' :function,
'friends':function,
'Undefined':function
}

for intent, keys in keywords.items():
  keywordsdictonary[intent]=re.compile('|'.join(keys))
while True:
  userinput = input().lower()
  matchedintent = None 
  for intent,pattern in keywordsdictonary.items():
    if re.search(pattern, userinput):
      matchedintent=intent  
  key='Undefined' 
  if matchedintent in responses:
    key = matchedintent
  responses[key]()






