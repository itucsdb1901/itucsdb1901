from flask import render_template, request, current_app
import sys
import psycopg2 as dbapi2
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


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


def home_page():
    return render_template("home.html")

def matches_page():
    return render_template("matches.html")
    
def players_page():
    url = current_app.config['db_url']
    listSQL = "SELECT * FROM test1"
    players = listTable(url, listSQL)
    return render_template("players.html", players=players)
    
def teams_page():
    return render_template("teams.html")

def leagues_page():
	return render_template("leagues.html")

def add_player():
    name = request.form['name']
    url = current_app.config['db_url']
    addName = "INSERT INTO TEST1 (FIRST_NAME) VALUES ('" + name + "');"
    statements = [addName]
    executeSQLquery(url, statements)
    return render_template("add_player.html", name=name)


