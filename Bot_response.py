import re
from nltk.corpus import wordnet

listofwords=['hello','Streamer']
listofsynonym={}
keywords={}
keywordsdictonary={}
keywords['greet'] = []
responses={ 'greet':'Hello! How can I help you?',
    'Streamer':'your favourite streamers are ...',
    'Undefined':'I dont quite understand. Could you repeat that?'}

for word in listofwords:
  synonyms=[]
  for synonym in wordnet.synsets(word):
    for x in synonym.lemmas():
      name = re.sub('[^a-zA-Z0-9 \n\.]', ' ', x.name())
      synonyms.append(name)

  listofsynonym[word]=set(synonyms)

for synonym in list(listofsynonym['hello']):
  keywords['greet'].append('.*\\b'+synonym+'\\b.*')

keywords['Streamer']=[]
for synonym in list(listofsynonym['Streamer']):
  keywords['Streamer'].append('.*\\b'+synonym+'\\b.*')
for intent, keys in keywords.items():
  keywordsdictonary[intent]=re.compile('|'.join(keys))


def output(input):
  userinput = input.lower()
  matchedintent = None 
  for intent,pattern in keywordsdictonary.items():
    if re.search(pattern, userinput):
      matchedintent=intent  
  key='Undefined' 
  if matchedintent in responses:
    key = matchedintent
  return responses[key]
