import requests
import json
import pickle
import random

## pun code

def findSubject():
    #read from the noun list
    nouns = pickle.load( open( "nouns", "rb" ))
    choiceIndex = random.randrange(0, len(nouns))
    word = nouns[choiceIndex]
    return word.replace('\n','')

def findActionOrLocation():
    #read from the action word list
    words = pickle.load( open( "actions", "rb" ))
    choiceIndex = random.randrange(0, len(words))
    word = words[choiceIndex]
    return word.replace('\n','')

def findWordsSimilarTo(word):
    res = requests.get("https://api.datamuse.com/words?ml="+word).json()
    words = []
    for wor in res:
        if ' ' not in wor['word']:
            words.append(wor['word'])

    #Test Helpers
    if word == "space":
        words.append('sputnik')
    if word == "barbarian":
        words.append('visigoth')
    if word == "that you can't see":
        #words = []
        words.append("invisible")
    #print(words)
    return words

def findSynonymsTo(word):
    res = requests.get("https://api.datamuse.com/words?rel_syn="+word).json()
    words = []
    for wor in res:
        if ' ' not in wor['word']:
            words.append(wor['word'])
    return words

def buildPun():
    subject = findSubject()
    actionOrLocation = findActionOrLocation()

    createPunAnswer(subject, actionOrLocation)

def createPunAnswer(subject, actionOrLocation):
    subjectActionOptionPairs = {}
    similar_to_subject = findWordsSimilarTo(subject)
    #similar_to_subject = findSynonymsTo(subject)
    similar_to_actionOrLocation = findWordsSimilarTo(actionOrLocation)
    #print(similar_to_subject)
    #print(similar_to_actionOrLocation)
    for similarSubjectWord in similar_to_subject:
        subjectActionOptionPairs[similarSubjectWord] = {}
        for similarActOrLocWord in similar_to_actionOrLocation:
            subjectActionOptionPairs[similarSubjectWord][similarActOrLocWord] = []
            substrings = findSubstringBetweenSubjectandActionOrLocation(similarSubjectWord, similarActOrLocWord)
            #print(substrings)
            for substring in substrings:
                subjectActionOptionPairs[similarSubjectWord][similarActOrLocWord].append(combineWords(similarSubjectWord, similarActOrLocWord, substring))

    return subjectActionOptionPairs

def findSubstringBetweenSubjectandActionOrLocation(subject, actionOrLocation):
    substrings = []
    #search for the shorter string in the longer string
    if len(subject) < len(actionOrLocation):
        shorter = subject
        longer = actionOrLocation
    else:
        shorter = actionOrLocation
        longer = subject

    for i in range(0, len(longer)):
        substring = findSubstring(longer[i:], shorter)
        if substring:
            substrings.append(substring)
    return substrings

#find a substring longer than 3 characters that is common between both strings
def findSubstring(string1, string2):
    index = string2.find(string1[0])
    #print("found " + string1 + " in " + string2 + " at " + str(index))
    end = index
    for i in range(index, min(len(string1), len(string2))):
        if string1[i] == string2[i]:
            #print(string1[i] + " == " + string2[i])
            end+=1
        else:
            break
    #print(end - index)
    if end - index >= 3:
        return string1[index:end]
    return False


def combineWords(subject, actionOrLocation, substring):
    #print("trying to join: " + subject + " , and " + actionOrLocation + " at substring: " + substring)
    #The word with the syllable accuring earlier in the string is our inserter 
    #  which will be inserted into the other word
    subIndex = subject.find(substring)
    actIndex = actionOrLocation.find(substring)
    
    # the root is the longer word
    if len(subject) > len(actionOrLocation):
        root = subject
        inserter = actionOrLocation
        index = subIndex
        #print("greater")
    else:
        root = actionOrLocation
        inserter = subject
        index = actIndex
        #print("less than")

    #Prepending
    if root.find(substring) == 0:
        #print("prepend")
        combined = root[index+len(inserter):]
        combined = inserter + combined

    #inserting
    else:
        #print("insert")
        combined = root[:index]
        combined = combined + inserter
    #print(root)
    #print(inserter)
    
    return combined

def scoringFunction(subject, actOrLocation, answer):
    answerLength = len(answer)

    #Score the answer by how much different the word is from the subject or actOrLocation, between 25% and 50% different is optimal
    differenceScore = scoreDifference(subject, actOrLocation, answer)

    #score the answer by change in length, the larger the increase the worse the score
    lengthCompare = max(len(subject), len(actOrLocation))
    lengthScore = (lengthCompare/answerLength)
    #if the answer is shorter then the words, we probably have an issue
    if lengthCompare < answerLength:
        lengthScore = 0
    #if the answer is too short to be a witty response, zero its score
    if len(answer) < 5:
        lengthScore = 0

    #score the answer by its ability to maintain proper grammatical and pronunciation standards
    grammarScore = 1

    score = (differenceScore + lengthScore + grammarScore)/3
    return score

def scoreDifference(subject, actOrLocation, answer):
    answerLength = len(answer)
    iterationLength = min(len(subject), answerLength)
    subjectDiffCount = 1
    actOrLocCount = 1
    for i in range(0, iterationLength):
        #print("does " + subject[i] + " == " + answer[i])
        if subject[i] != answer[i]:
            subjectDiffCount += 1

    iterationLength = min(len(actOrLocation), answerLength)
    for i in range(0, iterationLength):
        #print("does " + actOrLocation[i] + " == " + answer[i])
        if actOrLocation[i] != answer[i]:
            actOrLocCount += 1
    
    differenceScore = 0
    if (subjectDiffCount/answerLength >= 0.25 and subjectDiffCount/answerLength <= 0.5):
        differenceScore = 1
    if (actOrLocCount/answerLength >= 0.25 and actOrLocCount/answerLength <= 0.5):
        differenceScore = 1 
    
    return differenceScore

def searchForBestAnswer(answers):
    scoredAnswers = []
    for key in answers:
        for answerOptions in answers[key]:
            for answer in answers[key][answerOptions]:
                scoredAnswers.append((answer, scoringFunction(key, answerOptions, answer), key, answerOptions))
    bestScore = 0
    bestAnswer = ""
    answers = []
    #print(scoredAnswers)
    for answer in scoredAnswers:
        if answer[1] > bestScore:
            bestScore = answer[1]
            bestAnswer = answer[0]
        if answer[1] == bestScore:
            answers.append(answer[0])
    #print(answers)
    return bestAnswer

def constructSentence(subject, actOrLocation, bestAnswer):
    sentence = "What do you call a "
    sentence = sentence + subject + " "
    if False: #isLocation(actOrLocation):
        sentence = sentence + "in "
    else:
        sentence = sentence + "that can "
    
    sentence = sentence + actOrLocation + "?"
    sentence = sentence + " " + bestAnswer + "."
    return sentence

subject = 'potato'
actOrLocation = 'space'
#answers = createPunAnswer(subject, actOrLocation)
#bestAnswer = searchForBestAnswer(answers)

#sentence = constructSentence(subject, actOrLocation, bestAnswer)
#print(sentence)

#subject = 'barbarian'
#actOrLocation = "that you can't see"
#answers = createPunAnswer(subject, actOrLocation)
#print(answers)
#bestAnswer = searchForBestAnswer(answers)

#sentence = constructSentence(subject, actOrLocation, bestAnswer)
#print(sentence)
lines = ""
index = 0
while index < 100:
    subject = findSubject()
    actOrLocation = findActionOrLocation()
    #print("what do you call a " + subject + " that can " + actOrLocation + "?")
    answers = createPunAnswer(subject, actOrLocation)
    #print(answers)
    bestAnswer = searchForBestAnswer(answers)

    sentence = constructSentence(subject, actOrLocation, bestAnswer)
    if (bestAnswer != ""):
        index +=1
        lines = lines + sentence + '\n'

fp = open('output.txt', 'a')
fp.write(lines)
fp.close()

#TestyBois
#print(findSubstringBetweenSubjectandActionOrLocation('visigoth', 'invisible'))
#print(findSubstringBetweenSubjectandActionOrLocation('spud', 'sputnik'))
#print(combineWords('visigoth', 'invisible', 'visi'))
#print(combineWords('spud', 'sputnik', 'spu'))
#splitWordIntoSyllables('sputnik')

#print(scoringFunction('spud', 'sputnik', 'spudnik'))
