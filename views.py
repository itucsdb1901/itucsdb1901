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
    url = current_app.config['db_url']
    query = '''SELECT t1.name, t2.name, m.homescore, m.awayscore, std.name, lg.name, m.matchdate, m.homeid, m.awayid 
                FROM match m, team t1, team t2, stadium std, league lg
                    WHERE (m.homeid = t1.id AND m.awayid = t2.id 
                        AND m.stadiumid = std.id AND m.leagueid = lg.id)'''
    matches = listTable(url, query)
    return render_template("matches.html", matches = matches)

def player_page(personid):
    url = current_app.config["db_url"]
    query = "SELECT p.*, t.id, t.name, s.position FROM PERSON p LEFT JOIN SQUAD s ON (s.personid = p.id) LEFT JOIN TEAM t ON (s.teamid = t.id) WHERE (p.id=%d)"%personid
    result=getOneRowQuery(url,query)
    (teamID, teamName, position) = (result[4], result[5], result[6])
    person=classes.Person(id=int(result[0]),name=result[1],birthDay=int(result[2]),nationality=result[3])
    return render_template("player.html",player=person, year = int(datetime.datetime.now().year), teamID = teamID, teamName = teamName, position = position )

def add_goal(personid):
    url = current_app.config["db_url"]
    infoQuery = "SELECT p.*, t.id, t.name FROM PERSON p LEFT JOIN SQUAD s ON (s.personid = p.id) LEFT JOIN TEAM t ON (s.teamid = t.id) WHERE (p.id=%d)"%personid
    result=getOneRowQuery(url,infoQuery)
    person=classes.Person(id=int(result[0]),name=result[1],birthDay=int(result[2]),nationality=result[3])
    (teamID, temName) = (result[4], result[5])
    matchesQuery = '''
    select m.id, t1.name, t2.name, m.homescore, m.awayscore from match m 
	join team t1 on (t1.id = m.homeid)
	join team t2 on (t2.id = m.awayid)
	left join (select m.id as matchid, count(g.id) as savedgoals from goal g 
		left join squad s on (g.playerid = s.personid) 
		left join team t on (t.id = s.teamid and t.id = %d) 
		left join match m on ( (m.id = g.matchid) and ( (m.homeid = t.id) or (m.awayid = t.id) ) )
		group by m.id ) as saved
		on (m.id = saved.matchid) 
		where ( (savedgoals < m.homescore and m.homeid = %d) 
			or (savedgoals < m.awayscore and m.awayid = %d) 
			or (savedgoals is null and ( (m.homeid = %d and m.homescore > 0) or (m.awayid = %d and m.awayscore > 0) ) ) ) 
            '''%(teamID, teamID, teamID, teamID, teamID)
    matches = listTable(url, matchesQuery)
    assistPlayerQuery = '''
    SELECT p.* FROM PERSON p JOIN SQUAD s ON (s.personid = p.id AND s.teamid = %d AND p.id <> %d)
    ''' %(teamID,personid)
    assistPlayers = listTable(url, assistPlayerQuery)
    if request.method == "POST":
        minute = int(request.form.get('minute', False))
        assistPlayerID = int(request.form.get('assistPlayerid', False))
        matchID = int(request.form.get('matchid', False))
        addGoalQuery = "INSERT INTO GOAL (matchid, playerid, minute) VALUES (%d, %d, %d)" %(matchID, personid, minute)
        executeSQLquery(url, [addGoalQuery])
        findGoalIDSQL = "SELECT max(id) FROM GOAL"
        goalID = int(getOneRowQuery(url, findGoalIDSQL)[0])
        addAssistQuery = "INSERT INTO ASSIST (playerid, goalid) VALUES (%d, %d)"%(assistPlayerID, goalID)
        executeSQLquery(url, [addAssistQuery])
    return render_template("add_goal.html", matches=matches, person=person, assistPlayers = assistPlayers)

def add_card_to_player(playerid):
    url=current_app.config['db_url']
    getMatchesSQL='''SELECT a.name,match.homescore,match.awayscore,b.name,match.id FROM MATCH,TEAM a,TEAM b,PERSON,SQUAD 
    WHERE(a.id=match.homeid and b.id=match.awayid and person.id=%d and person.id=squad.personid and 
    (squad.teamid=match.homeid or squad.teamid=match.awayid)) '''%playerid
    matches=listTable(url,getMatchesSQL)
    if(request.method == 'POST'):
        matchid=int(request.form['match'])
        minute=int(request.form['minute'])
        red=bool(request.form['cardColor'])
        query = "INSERT INTO CARD (playerid,red,matchid,minute) VALUES (%d, %r ,%d,%d)" %(playerid, red, matchid,minute)
        executeSQLquery(url, [query])
    return render_template("add_card_to_player.html",matches=matches,playerid=playerid)

def search_player():
    url = current_app.config['db_url']
    search = request.form['search']
    listSQL = "SELECT * FROM PERSON WHERE (name LIKE '%" + search + "%')"
    players = listTable(url, listSQL)
    return render_template("players.html", players=players)

def players_page():
    url = current_app.config['db_url']
    listSQL = "SELECT DISTINCT p.* FROM PERSON p JOIN SQUAD s ON (p.id = s.personid)"
    players = listTable(url, listSQL)
    return render_template("players.html", players=players)
    
def teams_page():
    url = current_app.config['db_url']
    listSQL = "SELECT t.id, t.name, l.name as leaguename FROM TEAM t LEFT JOIN LEAGUE l ON (t.leagueid = l.id)"
    teams = listTable(url, listSQL)
    return render_template("teams.html", teams=teams)
def search_team():
    url = current_app.config['db_url']
    search = request.form['search']
    listSQL = "SELECT * FROM TEAM WHERE (name LIKE '%" + search + "%')"
    teams = listTable(url, listSQL)
    return render_template("teams.html", teams=teams)   

def team_page(teamid):
    url = current_app.config["db_url"]
    query = "SELECT t.id,t.name,l.name, p.name, s.name,l.country FROM TEAM t,LEAGUE l,PERSON p, STADIUM s WHERE (l.id=t.leagueid AND p.id=t.coach AND s.id=t.stadiumid AND t.id=%d)"%teamid
    result=getOneRowQuery(url,query)
    getSquadSQL="SELECT DISTINCT p.name,s.position,p.id FROM person p,squad s,team t where(p.id=s.personid and s.teamid=%d)"%teamid
    squad=listTable(url,getSquadSQL)
    team=classes.Team(id=int(result[0]),name=result[1],leagueID=result[2],stadiumID=result[4],coachID=result[3])
    return render_template("team.html",team=team,country=result[5],squad=squad)

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

def delete_player_from_squad(playerid):
    url = current_app.config['db_url']
    getTeamIDSQL="SELECT teamid from squad where personid=%d"%playerid
    teamid=listTable(url,getTeamIDSQL)
    query = 'DELETE FROM SQUAD WHERE (personid=%d)'%playerid
    executeSQLquery(url, [query])
    return team_page(teamid[0])


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

def leagues_page():
    url = current_app.config["db_url"]
    listSQL = "SELECT * FROM LEAGUE "
    leagues = listTable(url, listSQL)
    return render_template("leagues.html",leagues=leagues)

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

def add_match():
    url = current_app.config['db_url']
    getTeamSQL = "SELECT * FROM team"
    getStadiumsSQL = "SELECT * FROM stadium"
    getLeaguesSQL = "SELECT * FROM league"
    teams = listTable(url, getTeamSQL)
    leagues = listTable(url, getLeaguesSQL)
    stadiums = listTable(url, getStadiumsSQL)
    if(request.method == 'POST'):
        homeid = int(request.form['hometeamid'])
        awayid = int(request.form['awayteamid'])
        homescore = int(request.form['homescore'])
        awayscore = int(request.form['awayscore'])
        leagueid = int(request.form['leagueid'])
        stadiumid = int(request.form['stadiumid'])
        matchdate = request.form['matchdate']
        matchdate = datetime.datetime.strptime(matchdate, '%Y-%m-%d').date()
        query = "INSERT INTO match (homeid, awayid, homescore, awayscore, leagueid, stadiumid, matchdate) VALUES (%d, %d, %d, %d, %d, %d, CAST('%s' AS  DATE))" %(homeid, awayid, homescore, awayscore, leagueid, stadiumid, matchdate)
        executeSQLquery(url, [query])
    return render_template("add_match.html", stadiums = stadiums, leagues = leagues, teams = teams)

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
