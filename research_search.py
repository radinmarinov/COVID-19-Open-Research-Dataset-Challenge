from flask import Flask, render_template, redirect, url_for, jsonify, request
from research_finder import ResearchFinder

app = Flask(__name__)


rf = ResearchFinder()

@app.route('/')
def render():
	return render_template("index.html", search = False, data = [], search_entry = "")

@app.route('/', methods=['POST'])
def search():
	search = request.form['keywords']
	keywords = search.split(" ")
	papers = rf.find_paper(keywords)
	formatted_data = []
	for x in range(0,5):
		formatted_data.append([papers["init_title"].iloc[x], papers["init_abstract"].iloc[x]])

	print(formatted_data)


	return render_template("index.html", search = True, data = formatted_data, search_entry = search)