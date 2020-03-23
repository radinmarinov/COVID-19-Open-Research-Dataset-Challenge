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
PAGE = 0
ARTICLE = 0
@app.route('/')
def render():
	global SEARCH
	global DATA
	global ENTRY
	global SUMMARY
	global ARTICLE
	global PAPERS
	global PAGE
	global ARTICLE
	SEARCH = False
	DATA = []
	ENTRY = ""
	SUMMARY = False
	SUMMARY_TEXT = ""
	PAPERS = []
	return render_template("index.html", search = SEARCH, data = DATA, search_entry = ENTRY, summary = SUMMARY, summary_text = SUMMARY_TEXT, page = PAGE)

@app.route('/search', methods=['POST'])
def search():
	global SEARCH
	global DATA
	global ENTRY
	global SUMMARY
	global ARTICLE
	global PAPERS
	global PAGE
	global ARTICLE
	SUMMARY = False
	SEARCH = True
	ENTRY = request.form['keywords']
	keywords = ENTRY.split(" ")
	PAPERS = rf.find_paper(keywords)
	DATA = []
	for x in range(0,100):
		DATA.append([PAPERS["init_title"].iloc[x], "Abstract: " + PAPERS["init_abstract"].iloc[x][0:500] + "..."])

	return render_template("index.html", search = SEARCH, data = DATA, search_entry = ENTRY, summary = SUMMARY, summary_text = SUMMARY_TEXT, page = PAGE)


@app.route('/summary', methods=['POST'])
def summary():
	global SEARCH
	global DATA
	global ENTRY
	global SUMMARY
	global ARTICLE
	global PAPERS
	global PAGE
	global ARTICLE
	SEARCH = True
	SUMMARY = True
	ARTICLE = request.form['link']
	SUMMARY_TEXT = (DATA[int(ARTICLE)][0], rf.summarize_paper(PAPERS['init_body_text'].iloc[int(ARTICLE)], 7))

	return render_template("index.html", search = SEARCH, data = DATA, search_entry = ENTRY, summary = SUMMARY, summary_text = SUMMARY_TEXT, page = PAGE)

@app.route('/next', methods=['POST'])
def next():
	global SEARCH
	global DATA
	global ENTRY
	global SUMMARY
	global ARTICLE
	global PAPERS
	global PAGE
	global ARTICLE
	SEARCH = True
	SUMMARY = False
	PAGE += 5
	return render_template("index.html", search = SEARCH, data = DATA, search_entry = ENTRY, summary = SUMMARY, summary_text = SUMMARY_TEXT, page = PAGE)

@app.route('/prev', methods=['POST'])
def prev():
	global SEARCH
	global DATA
	global ENTRY
	global SUMMARY
	global ARTICLE
	global PAPERS
	global PAGE
	global ARTICLE
	SEARCH = True
	SUMMARY = False
	PAGE -= 5
	return render_template("index.html", search = SEARCH, data = DATA, search_entry = ENTRY, summary = SUMMARY, summary_text = SUMMARY_TEXT, page = PAGE)

	