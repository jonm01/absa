import os
import json
import re
import nltk
import ast
import math, itertools, operator
from textblob import TextBlob

def preProcessing(input):
    stopwords = nltk.corpus.stopwords.words("english")
    stopwords.append('OMG')
    stopwords.append(':-)')
    result=(' '.join([word for word in input.split() if word not in stopwords]))
    print('Following are the Stop Words')
    print(stopwords)
    result=str(result)
    result=re.sub(r'\(.*?\)','',result)
    print(result)
    return result

def tokenizeReviews(input):
    tokenizedReviews={}
    tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()
    id=1;
    stopwords = nltk.corpus.stopwords.words("english")
    regexp = re.compile(r'\?')
    for sentence in tokenizer.tokenize(input):
        #logic to remove questions and errors
        if regexp.search(sentence):
            print("removed")
        else:
            sentence=re.sub(r'\(.*?\)','',sentence)
            tokenizedReviews[id]=sentence
            id+=1

    for key,value in tokenizedReviews.items():
        print(key,' ',value)
        tokenizedReviews[key]=value
    return tokenizedReviews


def posTagging(input):
    outputPost={}
    for key,value in input.items():
        outputPost[key]=nltk.pos_tag(nltk.word_tokenize(value))

    for key,value in outputPost.items():
        print(key,' ',value)
        return outputPost


def aspectExtraction(input):
    prevWord=''
    prevTag=''
    currWord=''
    aspectList=[]
    outputDict={}
    #Extracting Aspects
    for key,value in input.items():
        for word,tag in value:
            if(tag=='NN' or tag=='NNP'):
                if(prevTag=='NN' or prevTag=='NNP'):
                    currWord= prevWord + ' ' + word
                else:
                    aspectList.append(prevWord.upper())
                    currWord= word
            prevWord=currWord
            prevTag=tag
    #Eliminating aspect count less than 5
    for aspect in aspectList:
            if(aspectList.count(aspect)>5):
                    if(outputDict.keys()!=aspect):
                            outputDict[aspect]=aspectList.count(aspect)
    outputAspect=sorted(outputDict.items(), key=lambda x: x[1],reverse = True)
    print(outputAspect)
    return outputAspect

#function to add upto 100 and round
def apportion_pcts(pcts, total):
    proportions = [total * (pct / 100) for pct in pcts]
    apportions = [math.floor(p) for p in proportions]
    remainder = total - sum(apportions)
    remainders = [(i, p - math.floor(p)) for (i, p) in enumerate(proportions)]
    remainders.sort(key=operator.itemgetter(1), reverse=True)
    for (i, _) in itertools.cycle(remainders):
        if remainder == 0:
            break
        else:
            apportions[i] += 1
            remainder -= 1
    return apportions

def identifyOpinion(review, aspect, tokenized):
    output={}
    for aspect,no in aspect:
        count=0
        p=0
        ng=0
        n=0
        for key,value in tokenized.items():
            if(aspect in str(value).upper()):
                count=count+1
                a=TextBlob(value)
                output.setdefault(aspect,{"score":[0,0,0], "percent":[0,0,0], "positive":[], "negative":[], "neutral":[]})
                pol=a.sentiment.polarity
                print(pol)

                if (pol>0):
                    p=p+1
                    output[aspect]["score"][0]+=pol
                    output[aspect]["positive"].append(tokenized[key])
                elif(pol<0):
                    ng=ng+1
                    output[aspect]["score"][1]+=pol
                    output[aspect]["negative"].append(tokenized[key])
                else:
                    n=n+1
                    output[aspect]["score"][2]+=1
                    output[aspect]["neutral"].append(tokenized[key])



        if(p>0):
            output[aspect]["score"][0]=round(output[aspect]["score"][0]/p,1)
            output[aspect]["percent"][0]=(p/count)*100
        if(ng>0):
            output[aspect]["score"][1]=round(output[aspect]["score"][1]/ng,1)
            output[aspect]["percent"][1]=(ng/count)*100


        if(n>0):
            output[aspect]["score"][2]=round(output[aspect]["score"][2]/n,1)
            output[aspect]["percent"][2]=(n/count)*100
        output[aspect]["percent"]=apportion_pcts(output[aspect]["percent"],100)

    return output


def startMine(pid):
    fname='data'+pid+'.json'
    with open(fname, 'r') as f:
        data = json.load(f)

    print(data)
    reviews=""
    for r in data["reviews"]:
        reviews=reviews+r["review_text"]

    print("\n\n\n#### Pre Processing ####\n")
    pre = preProcessing(reviews)
    print("\n\n\n#### Splitting into sentence ####\n")
    tokenized = tokenizeReviews(pre)
    print("\n\n\n#### Pos Tagging ####\n")
    postagged = posTagging(tokenized)
    print("\n\n\n#### Aspect Identification ####\n")
    aspects = aspectExtraction(postagged)
    print("\n\n\n#### Opinion mining ####\n")
    opnion=identifyOpinion(postagged,aspects,tokenized)
    f = open("output.json",'w')
    json.dump(opnion,f,indent=4)
    f.close()
    return opnion
