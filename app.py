from flask import flash, Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
from wiki_chronological_search import *
import json

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        Phrase=request.form.getlist('Phrase')
        Number_of_Events=request.form.getlist('Number_of_Events')
        print(Phrase)
        search_results=wiki_search(Phrase[0],Number_of_Events[0])
        print(search_results)
        if search_results != None:
            transformed_search_results = zip(search_results[0].tolist(), search_results[1].tolist())
            return render_template("result.html",result = transformed_search_results)
        else:
            flash('No results found!')
            return redirect('/')
            
if __name__ == '__main__':
   app.secret_key = 'super secret key'
   app.config['SESSION_TYPE'] = 'filesystem'
   sess = Session()
   sess.init_app(app)
   app.run(debug = True)