import os
import nltk
import string
import networkx
import httplib, urllib, base64
from math import log10
from newspaper import Article
from preprocessing.textcleaner import clean_text_by_sentences
from flask import Flask
app = Flask(__name__)

def sentSimilar(sen1, sen2):
	sen1Words = sen1.split()
	sen2Words = sen2.split()
	numCommonWords = len(set(sen1Words) & set(sen2Words))
	sen1Log = log10(len(sen1Words))
	sen2Log = log10(len(sen2Words))
	if sen1Log + sen2Log == 0:
		return 0
	return numCommonWords / (sen1Log + sen2Log)

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

def setGraphEdgeWeightsTFIDF(senGraph, senToken):
	for sen1 in senGraph.nodes():
   		for sen2 in senGraph.nodes():
			if sen1 != sen2 and not senGraph.has_edge(sen1, sen2):
				similarityWeight = idfModCos(senToken, sen1, sen2)
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
	return "\n".join([sen.text for sen in pulledSentence])

def getArticleTitleText(url):
	article = Article(url)
	article.download()
	article.html
	article.parse()
	return [article.title, article.text.encode('utf-8')]


#url = 'https://hbr.org/2017/02/how-founders-can-recognize-and-combat-depression'
#print getArticleText(url)
#sumTest = getArticleTitleText(url)
#print sumTest[0]
#with open('data.txt', 'r') as myfile:
#	origText = myfile.read().replace('\n', '')
#sumTest[1] = origText
#print extractSentences(sumTest[1], 4)

@app.route('/post/<path:post_url>')
def show_post(post_url):
    # show the post with the given id, the id is an integer
    url = post_url
    sumText = getArticleTitleText(url)
    return extractSentences(sumText[1], 3)

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)



