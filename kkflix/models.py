from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
import os


graph = Graph('http://localhost:7474/db/data/', username="neo4j", password="admin")

class User:
    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.find_one('User', 'username', self.username)
        return user

    def register(self, password):
        if not self.find():
            user = Node('User', username=self.username, password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, user['password'])
        else:
            return False

    def like_movie(self,movie_id):
        user=self.find()
        movie=graph.find_one('Movie','id',int(movie_id))
        graph.merge(Relationship(user,'LIKED',movie))

    def watched_movie(self,movie_id):
        user=self.find()
        movie=graph.find_one('Movie','id',int(movie_id))
        graph.merge(Relationship(user,'WATCHED',movie))

    def watch_history(self):
        user=self.find()
        watched_list=[]
        for movie in graph.match(start_node=user,rel_type="WATCHED"):
            watched_list.append(movie.end_node())
        return watched_list
    def liked_history(self):
        user=self.find()
        watched_list=[]
        for movie in graph.match(start_node=user,rel_type="LIKED"):
            watched_list.append(movie.end_node())
        return watched_list

def search_movie(search_key):
    movie_list=[]
    movie=graph.find_one('Movie','title',search_key)
    if movie !=None:
        movie_list.append(movie)
    genre=graph.find_one('Genre','name',search_key)
    # print(genre)
    if genre !=None:
        for movies in graph.match(rel_type="HAS_GENRE",end_node=genre):
            movie_list.append(movies.start_node())
    actor=graph.find_one('Person','name',search_key)
    if actor!=None:
        for movies in graph.match(start_node=actor,rel_type="ACTED_IN"):
            movie_list.append(movies.end_node())
    keyword=graph.find_one('Keyword','name',search_key)
    if keyword !=None:
        for movies in graph.match(rel_type="HAS_KEYWORD",end_node=keyword):
            movie_list.append(movies.start_node())
    return set(movie_list)

def get_movie_info(movie_id):
    movie_id=int(movie_id)
    movie=graph.find_one('Movie','id',movie_id)
    return movie
def get_relate_movie(movie_id):
    movie_list=[]
    movie_id=int(movie_id)
    movie=graph.find_one('Movie','id',movie_id)
    for keyword in graph.match(start_node=movie,rel_type="HAS_KEYWORD"):
        for newmovie in graph.match(rel_type="HAS_KEYWORD",end_node=keyword.end_node()):
            if newmovie.start_node()!=movie:
                movie_list.append(newmovie.start_node())
            if len(set(movie_list))>4:
                break
        if len(set(movie_list))>4:
            break
    return set(movie_list)

def get_personal_videos(genre_list):
    movie_dic={}
    for genre in genre_list:
        genre_node=graph.find_one('Genre','name',genre)
        genre_movie=[]
        i=0
        for movie in graph.match(rel_type="HAS_GENRE",end_node=genre_node):
            i=i+1
            if i>5:
                break
            genre_movie.append(movie.start_node())
        movie_dic[genre]=genre_movie
    return movie_dic
