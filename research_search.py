from flask import Flask, render_template, redirect, url_for, jsonify, request
from research_finder import ResearchFinder

app = Flask(__name__)

rf = ResearchFinder()
rf.load_data()
SEARCH = False
DATA = []
ENTRY = ""
SUMMARY = False
SUMMARY_TEXT = ""
PAPERS = []
@app.route('/')
def render():
	global SEARCH
	global DATA
	global ENTRY
	global SUMMARY
	global ARTICLE
	global PAPERS
	return render_template("index.html", search = SEARCH, data = DATA, search_entry = ENTRY, summary = SUMMARY, summary_text = SUMMARY_TEXT)

@app.route('/search', methods=['POST'])
def search():
	global SEARCH
	global DATA
	global ENTRY
	global SUMMARY
	global ARTICLE
	global PAPERS
	SUMMARY = False
	SEARCH = True
	ENTRY = request.form['keywords']
	keywords = ENTRY.split(" ")
	PAPERS = rf.find_paper(keywords)
	DATA = []
	for x in range(0,5):
		DATA.append([PAPERS["init_title"].iloc[x], "Abstract: " + PAPERS["init_abstract"].iloc[x][0:500] + "..."])

	#print(formatted_data)
	return render_template("index.html", search = SEARCH, data = DATA, search_entry = ENTRY, summary = SUMMARY, summary_text = SUMMARY_TEXT)


@app.route('/summary', methods=['POST'])
def summary():
	global SEARCH
	global DATA
	global ENTRY
	global SUMMARY
	global ARTICLE
	global PAPERS
	SEARCH = True
	SUMMARY = True
	ARTICLE = request.form['link']
	SUMMARY_TEXT = rf.summarize_paper(PAPERS['init_body_text'].iloc[int(ARTICLE)], 7)
	return render_template("index.html", search = SEARCH, data = DATA, search_entry = ENTRY, summary = SUMMARY, summary_text = SUMMARY_TEXT)
	# keywords = search.split(" ")
	# papers = rf.find_paper(keywords)
	# formatted_data = []
	# for x in range(0,5):
	# 	formatted_data.append([papers["init_title"].iloc[x], "Abstract: " + papers["init_abstract"].iloc[x][0:500] + "..."])

	# #print(formatted_data)


	# return render_template("index.html", search = True, data = formatted_data, search_entry = search)