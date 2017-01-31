from .models import User,get_personal_videos,get_movie_info,get_relate_movie,search_movie
from flask import Flask, request, session, redirect, url_for, render_template, flash
app = Flask(__name__)

@app.route('/personal', methods=['GET','POST'])
def personal():
    if request.method == 'POST':
        search_key = request.form['search_title']
        session['search_key']=search_key
        return redirect(url_for('result'))
    username = session.get('username')
    liked_id=request.cookies.get('liked_id','')
    if liked_id !='':
        User(username).like_movie(liked_id)
    genre_list=['Action','Fantasy','Comedy','Family','Crime','History','Animation','Romance','Suspense']
    movie_dic=get_personal_videos(genre_list)
    return render_template('personal.html',username=username,movie_dic=movie_dic)

@app.route('/result')
def result():
    username = session.get('username')
    search_key=session.get('search_key')
    search_result=search_movie(search_key)
    if len(search_result)>1000:
        result=search_result[:10]
    else:
        result=search_result
    return render_template('result.html',username=username,result=result)

@app.route('/donate')
def donate():
    username=session.get('username')
    return render_template('donate.html',username=username)

@app.route('/history')
def watch_history():
    username=session.get('username')
    watched_list=User(username).watch_history()
    return render_template('history.html',username=username,watched_list=watched_list)

@app.route('/liked')
def liked_history():
    username=session.get('username')
    watched_list=User(username).liked_history()
    return render_template('liked.html',username=username,watched_list=watched_list)



@app.route('/watching',methods=['GET','POST'])
def videos():
    if request.method == 'POST':
        search_key = request.form['search_title']
        session['search_key']=search_key
        return redirect(url_for('result'))
    username=session.get('username')
    liked_id=request.cookies.get('liked_id','')
    movie_id=request.cookies.get('movie_id','')
    movie=get_movie_info(movie_id)
    relate_movie=get_relate_movie(movie_id)
    if liked_id !='':
        User(username).like_movie(liked_id)
    User(username).watched_movie(movie_id)
    return render_template('videos.html',username=username,movie=movie,relate_movie=relate_movie)
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        if len(username) < 1:
            flash('username must be at least one character.')
        elif password!=password_confirm:
            flash('password not match')
        elif len(password) < 5:
            flash('password must be at least 5 characters.')
        elif not User(username).register(password):
            flash('username already taken.')
        else:
            session['username'] = username
            return redirect(url_for('personal'))

    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User(username).verify_password(password):
            flash('Invalid Password or username.')
        else:
            session['username'] = username
            return redirect(url_for('personal'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out')
    return redirect(url_for('login'))
