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

def add_league():
    if(request.method=='POST'):
        name=request.form["name"]
        teamcount=int(request.form["teamcount"])
        country=request.form["country"]
        query="INSERT INTO LEAGUE (NAME,TEAMCOUNT,COUNTRY) VALUES ('%s',%d,'%s')"%(name,teamcount,country)
        statement=[query]
        url=current_app.config["db_url"]
        executeSQLquery(url,statement)
    return render_template("add_league.html")

def add_team():
    url = current_app.config['db_url']
    getPeopleSQL = "SELECT * FROM person"
    getStadiumsSQL = "SELECT * FROM stadium"
    getLeaguesSQL = "SELECT * FROM league"
    people = listTable(url, getPeopleSQL)
    leagues = listTable(url, getLeaguesSQL)
    stadiums = listTable(url, getStadiumsSQL)
    if(request.method == 'POST'):
        name = request.form['name']
        coachid = int(request.form['coach'])
        leagueid = int(request.form['league'])
        stadiumid = int(request.form['stadium'])
        query = "INSERT INTO team (name, leagueid, stadiumid, coach) VALUES ('%s', %d, %d, %d)" %(name, leagueid, stadiumid, coachid)
        executeSQLquery(url, [query])
    return render_template("add_team.html", stadiums = stadiums, leagues = leagues, people = people)

def add_stadium():
    url = current_app.config['db_url']
    if(request.method == 'POST'):
        name = request.form['name']
        capacity = int(request.form['capacity'])
        city = request.form['city']
        query = "INSERT INTO stadium (name, capacity, city) VALUES ('%s', %d, '%s')" %(name, capacity, city) 
        executeSQLquery(url, [query])
    return render_template("add_stadium.html")

def add_data_page():
    return render_template("add_data.html")
