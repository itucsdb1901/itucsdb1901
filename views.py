from flask import render_template, request, current_app
import sys
import psycopg2 as dbapi2
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import classes


def executeSQLquery(url, statements):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in (statements):
            cursor.execute(statement)
        cursor.close()

def listTable(url, statement):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        cursor.execute(statement)
        result = cursor.fetchall()
        cursor.close()
    return result

def getOneRowQuery(url,statement):
    with dbapi2.connect(url) as connection:
        cursor=connection.cursor()
        cursor.execute(statement)
        result= cursor.fetchone()
        cursor.close()
    return result

def delete_player(personid):
    url = current_app.config['db_url']
    query = 'DELETE FROM test1 WHERE (id=%d)'%personid
    executeSQLquery(url, [query])
    return players_page()


def home_page():
    return render_template("home.html")

def matches_page():
    return render_template("matches.html")

def player_page(personid):
    url = current_app.config["db_url"]
    query = "SELECT * FROM test1 WHERE (id=%d)"%personid
    result=getOneRowQuery(url,query)
    person=classes.Person(id=int(result[0]),name=result[1],birthDay=1990,nationality="b")
    return render_template("player.html",player=person)

def players_page():
    url = current_app.config['db_url']
    listSQL = "SELECT * FROM test1"
    players = listTable(url, listSQL)
    return render_template("players.html", players=players)
    
def teams_page():
    return render_template("teams.html")

def leagues_page():
	return render_template("leagues.html")

def add_person():
    if(request.method=='POST'):
        name=request.form["name"]
        birthyear=int(request.form["birthyear"])
        nationality=request.form["nationality"]
        query="INSERT INTO PERSON (NAME,BIRTHYEAR,NATIONALITY) VALUES ('%s',%d,'%s')"%(name,birthyear,nationality)
        statement=[query]
        url=current_app.config["db_url"]
        executeSQLquery(url,statement)
    return render_template("add_person.html")

def add_team():
    return render_template("add_team.html")

def add_stadium():
    return render_template("add_stadium.html")

def add_data_page():
    return render_template("add_data.html")
