import os
import nltk
import string
import networkx
import httplib, urllib, base64
from math import log10, sqrt
from newspaper.article import Article
from preprocessing.textcleaner import clean_text_by_sentences

#TO USE
def sentSimilar(sen1, sen2):
	sen1Words = sen1.split()
	sen2Words = sen2.split()
	numCommonWords = len(set(sen1Words) & set(sen2Words))
	sen1Log = log10(len(sen1Words))
	sen2Log = log10(len(sen2Words))
	if sen1Log + sen2Log == 0.0:
		return 0.0
	return numCommonWords / (sen1Log + sen2Log)

#TESTING SIMILARITY METRICS
def sentSimilarJac(sen1, sen2):
	sen1Words = sen1.split()
	sen2Words = sen2.split()
	numCommonWords = len(set(sen1Words) & set(sen2Words))
	numUnion = len(set(sen1Words).union(set(sen2Words)))
	return numCommonWords / numUnion

#TESTING SIMILARITY METRICS
def sentSimilarBM25(sen1, sen2):
	score = 0.0
	sen1Words = sen1.split()
	sen2Words = sen2.split()
	k = 1.2
	b = .75
	avgdl = BM25AvgDocLen()
	for word in sen2Words:
		idfWord = BM25idfWord(word)
		occCount = BM25WordInSen(word, sen1Words)
		second = occCount * (k + 1) / (occCount + k * (1 - b + b * len(sen1Words) / avgdl))
		score += (idfWord * second)
	return score
def BM25idfWord(word):
	docLen = len(senToken)
	wordOccurence = BM25WordOcc(word)
	if wordOccurence <= (len(senToken) / 2.0):
		return log10((docLen - wordOccurence + .5) / (wordOccurence + .5))
	elif wordOccurence > (len(senToken) / 2.0):
		return .25 * BM25AvgIDF()
def BM25WordInSen(searchWord, senWordToken):
	totalCount = 0.0
	for word in senWordToken:
		if searchWord == word:
			totalCount += 1
	return totalCount
def BM25WordOcc(word):
	occCount = 0.0
	for sentence in senToken:
		if word in sentence:
			occCount += 1
	return occCount
def BM25AvgIDF():
	totalText = ''
	totalIDF = 0.0
	for sentence in senToken:
		totalText += sentence + ' '
	totalTextWords = set(totalText.split())
	for word in totalTextWords:

		wordOccurence = 0.0
		for sentence in senToken:
			if word in sentence:
				wordOccurence += 1
		totalIDF += log10(len(senToken) / wordOccurence)
	totalIDF = totalIDF / len(totalTextWords)
	return totalIDF

def BM25AvgDocLen():
	avgLen = 0.0
	for sentence in senToken:
		avgLen += len(sentence.split())
	avgLen /= len(senToken)
	return avgLen

##################################################################

def buildGraph(senToken):
	graph = networkx.Graph()
	for sentence in senToken:
		if not graph.has_node(sentence):
			graph.add_node(sentence)
	return graph

def setGraphEdgeWeights(senGraph):
	for sen1 in senGraph.nodes():
   		for sen2 in senGraph.nodes():
			if sen1 != sen2 and not senGraph.has_edge(sen1, sen2):
				similarityWeight = sentSimilar(sen1, sen2)
				if similarityWeight != 0:
					senGraph.add_edge(sen1, sen2, weight = similarityWeight)

def addScores(sentences, scores):
    for sentence in sentences:
        # Adds the score to the object if it has one.
        if sentence.token in scores:
            sentence.score = scores[sentence.token]
        else:
            sentence.score = 0

def extractSentences(text, length):
	global senToken
	origText = text
	sentence = clean_text_by_sentences(origText, language="english")
	senToken = [sen.token for sen in sentence]
	#senToken = nltk.sent_tokenize(origText)
	senGraph = buildGraph(senToken)
	setGraphEdgeWeights(senGraph)
	senGraph.remove_nodes_from(networkx.isolates(senGraph))
	pageRank = networkx.pagerank(senGraph, weight='weight')
	addScores(sentence, pageRank)
	sentence.sort(key=lambda s: s.score, reverse=True)
	pulledSentence = sentence[:int(length)]
    # most important sentences in ascending order of importance
	pulledSentence.sort(key=lambda s: s.index)
	finalText = ""
	for sen in pulledSentence:
		finalText += sen.text
		finalText += '\n'
	return finalText

def getArticleTitleText(url):
	article = Article(url)
	article.download()
	article.html
	article.parse()
	return [article.title, article.text.encode('utf-8')]

#with open('data.txt', 'r') as myfile:
#	origText = myfile.read().replace('\n', ' ')
#print extractSentences(origText, 3)
