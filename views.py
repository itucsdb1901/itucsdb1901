from flask import render_template, request, current_app
import sys
import psycopg2 as dbapi2
import classes
import datetime


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
    query = 'DELETE FROM PERSON WHERE (id=%d)'%personid
    executeSQLquery(url, [query])
    return players_page()


def home_page():
    return render_template("home.html")

def matches_page():
    return render_template("matches.html")

def player_page(personid):
    url = current_app.config["db_url"]
    query = "SELECT * FROM PERSON WHERE (id=%d)"%personid
    result=getOneRowQuery(url,query)
    person=classes.Person(id=int(result[0]),name=result[1],birthDay=int(result[2]),nationality=result[3])
    return render_template("player.html",player=person, year = int(datetime.datetime.now().year))

def players_page():
    url = current_app.config['db_url']
    listSQL = "SELECT * FROM PERSON"
    players = listTable(url, listSQL)
    return render_template("players.html", players=players)
    
def teams_page():
    url = current_app.config['db_url']
    listSQL = "SELECT * FROM TEAM"
    teams = listTable(url, listSQL)
    return render_template("teams.html", teams=teams)

def team_page(teamid):
    url = current_app.config["db_url"]
    query = "SELECT t.id,t.name,l.name, p.name, s.name,l.country FROM TEAM t,LEAGUE l,PERSON p, STADIUM s WHERE (l.id=t.leagueid AND p.id=t.coach AND s.id=t.stadiumid AND t.id=%d)"%teamid
    result=getOneRowQuery(url,query)
    team=classes.Team(id=int(result[0]),name=result[1],leagueID=result[2],stadiumID=result[4],coachID=result[3])
    return render_template("team.html",team=team,country=result[5])

def delete_team(teamid):
    url = current_app.config['db_url']
    query = 'DELETE FROM TEAM WHERE (id=%d)'%teamid
    executeSQLquery(url, [query])
    return teams_page()

def add_player_to_squad(teamid):
    url = current_app.config['db_url']
    teamSQL = "SELECT id, name FROM team WHERE id=%d" %teamid
    getPlayerListSQL = '''
    SELECT person.id, person.name as namee from person LEFT JOIN team ON person.id=team.coach 
        WHERE team.coach is null
    intersect 
    SELECT person.id, person.name as namee from person LEFT JOIN squad ON person.id=squad.personid 
        WHERE squad.personid is null '''
    playerList=listTable(url, getPlayerListSQL)
    team = getOneRowQuery(url, teamSQL)
    if(request.method == 'POST'):
        position = request.form['position']
        playerid = int(request.form['playerbox'])
        query = "INSERT INTO squad (personid,teamid,position) VALUES (%d, %d ,'%s')" %(playerid, teamid, position)
        executeSQLquery(url, [query])
    return render_template("add_player_to_squad.html",playerList=playerList,team=team)

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
