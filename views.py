from flask import render_template, request, current_app, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, current_user, login_user
import sys
import psycopg2 as dbapi2
import classes
from classes import User
import datetime

def checkSignIn():
    if (request.method=="POST"):
        url=current_app.config["db_url"]
        username = request.form.get("username",False)
        password = request.form.get("password",False)
        checkUser="SELECT * FROM ACCOUNT WHERE(username='%s' AND password='%s' )"%(username,password)
        result=listTable(url,checkUser)
        if(len(result)==0):
            return render_template("login.html")
        else:
            current_app.config["signed"] = True
            return home_page()
    return render_template("login.html")


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



def checkSignIn():
    if (request.method=="POST"):
        url=current_app.config["db_url"]
        username = request.form.get("username",False)
        password = request.form.get("password",False)
        checkUser="SELECT * FROM ACCOUNT WHERE(username='%s')"%(username)
        result=getOneRowQuery(url,checkUser)
        if(result is not None):
            if check_password_hash(result[2], password):
                user = User(username, result[2])
                login_user(user)            
                return redirect('/')
            else:
                return render_template("login.html", error = 1)
        else:
            return render_template("signup.html", error = 2)
    return render_template("login.html")

def signUp():
    if(request.method == "POST"):
        url=current_app.config["db_url"]
        username = request.form.get("username",False)
        password = request.form.get("password",False)
        checkExist = "SELECT username FROM ACCOUNT WHERE (username = '%s')" %(username)
        checkExist = getOneRowQuery(url, checkExist)
        if(checkExist is not None):
            return render_template("signup.html", error=1, user = current_user)
        password = generate_password_hash(password, method="sha256")
        saveUser = "INSERT INTO ACCOUNT (username, password) VALUES ('%s', '%s')"%(username, password)
        executeSQLquery(url, [saveUser])
        user = User(username=username, password=password)
        login_user(user)
        return redirect('/')
    return render_template("signup.html", error=0, user = current_user)

@login_required
def logOut():
    logout_user()
    return home_page()


@login_required
def delete_player(personid):
    url = current_app.config['db_url']
    query = 'DELETE FROM PERSON WHERE (id=%d)'%personid
    executeSQLquery(url, [query])
    return players_page()

def home_page():
    url=current_app.config["db_url"]
    person_count = "SELECT COUNT(*) FROM PERSON"
    person_count = (listTable(url, person_count)[0][0])
    leagues_count  ="SELECT COUNT(*) FROM LEAGUE"
    leagues_count = (listTable(url,  leagues_count)[0][0])
    matches_count  ="SELECT COUNT(*) FROM MATCH"
    matches_count =(listTable(url,  matches_count)[0][0])
    stadiums_count="SELECT COUNT(*) FROM STADIUM"
    stadiums_count =(listTable(url, stadiums_count)[0][0])
    goals_count = "SELECT COUNT(*) FROM GOAL"
    goals_count =(listTable(url, goals_count)[0][0])
    arguments = {
                "person_count": person_count, 
                "leagues_count": leagues_count,
                "matches_count":matches_count,
                "stadiums_count":stadiums_count,
                "goals_count":goals_count,
                "current_user":current_user

                }
    return render_template("home.html", arguments=arguments, user=current_user)

def matches_page():
    url = current_app.config['db_url']
    query = '''SELECT t1.name, t2.name, m.homescore, m.awayscore, std.name, lg.name, m.matchdate, m.homeid, m.awayid ,m.id 
                FROM match m, team t1, team t2, stadium std, league lg
                    WHERE (m.homeid = t1.id AND m.awayid = t2.id 
                        AND m.stadiumid = std.id AND m.leagueid = lg.id) ORDER BY lg.name ASC'''
    matches = listTable(url, query)
    return render_template("matches.html", matches = matches, user=current_user)

def match_detail(matchid):
    if(current_app.config["signed"]==False):
        return checkSignIn()
    url = current_app.config["db_url"]
    query="SELECT t1.name as home,t2.name as away,m.homescore,m.awayscore FROM MATCH m join team t1 on (t1.id=m.homeid) join team t2 on (t2.id=m.awayid) WHERE (m.id=%d)"%matchid
    teams = listTable(url,query)
    query="SELECT p.name,c.red,c.minute FROM MATCH m LEFT JOIN CARD c ON (c.matchid=m.id) JOIN PERSON p ON (p.id=c.playerid)  WHERE(m.id=%d) ORDER BY c.minute ASC"%matchid
    cards = listTable(url, query)
    query="SELECT p.name as playername,g.minute,t.name as teamname FROM MATCH m LEFT JOIN goal g ON (g.matchid=m.id) JOIN person p on (p.id=g.playerid) JOIN SQUAD s ON (s.personid=p.id) JOIN TEAM t ON (t.id=s.teamid) WHERE (m.id=%d) ORDER BY g.minute ASC"%matchid
    goals = listTable(url,query)
    query="SELECT p1.name as outname,p2.name as inname,s.minute FROM MATCH m LEFT JOIN SUBSTITUTION s ON (s.matchid=m.id) JOIN person p1 on (p1.id=s.outplayerid) JOIN person p2 on (p2.id=s.inplayerid)  where m.id=%d order by s.minute ASC"%matchid
    substitutions = listTable(url,query)
    return render_template("match_detail.html",cards=cards,goals=goals,substitutions=substitutions,teams=teams)

def player_page(personid):
    url = current_app.config["db_url"]
    query = "SELECT p.*, t.id, t.name, s.position FROM PERSON p LEFT JOIN SQUAD s ON (s.personid = p.id) LEFT JOIN TEAM t ON (s.teamid = t.id) WHERE (p.id=%d)"%personid
    goal = " select count(*) from goal left join person on(goal.playerid = person.id) where(person.id=%d)"%personid
    query2="select * from negotitation where personid=%d"%personid
    redcard = "select count(*) from card left join person on(card.playerid = person.id) where(person.id=%d) and (card.red=true)"%personid
    yellowcard = "select count(*) from card left join person on(card.playerid = person.id) where(person.id=%d) and (card.red=false)"%personid
    result=getOneRowQuery(url,query)
    number_goal=getOneRowQuery(url,goal)
    negotitation = getOneRowQuery(url,query2)
    yellowcardy = getOneRowQuery(url,yellowcard)
    redcardy = getOneRowQuery(url,redcard)
    amount=negotitation[4]
    duration=negotitation[3]
    startdate=negotitation[5]
    seasons=startdate+1
    scoredgoal=number_goal[0]
    yellowcardx = yellowcardy[0]
    redcardx = redcardy[0]
    (teamID, teamName, position) = (result[5], result[6], result[7])
    person=classes.Person(id=int(result[0]),name=result[1],birthDay=int(result[2]),nationality=result[3],personphoto=result[4])
    return render_template("player.html",player=person, year = int(datetime.datetime.now().year), teamID = teamID, teamName = teamName, position = position,scoredgoal=scoredgoal,amount=amount,duration=duration,startdate=startdate,seasons=seasons,redcardx=redcardx,yellowcardx=yellowcardx, user=current_user )

@login_required
def add_goal(personid):
    url = current_app.config["db_url"]
    infoQuery = "SELECT p.*, t.id, t.name FROM PERSON p LEFT JOIN SQUAD s ON (s.personid = p.id) LEFT JOIN TEAM t ON (s.teamid = t.id) WHERE (p.id=%d)"%personid
    result=getOneRowQuery(url,infoQuery)
    person=classes.Person(id=int(result[0]),name=result[1],birthDay=int(result[2]),nationality=result[3],personphoto=result[4])
    teamID = result[5]
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
    return render_template("add_goal.html", matches=matches, person=person, assistPlayers = assistPlayers, user=current_user)

@login_required
def add_card_to_player(playerid):
    url=current_app.config['db_url']
    getMatchesSQL='''SELECT a.name,match.homescore,match.awayscore,b.name,match.id FROM MATCH,TEAM a,TEAM b,PERSON,SQUAD 
    WHERE(a.id=match.homeid and b.id=match.awayid and person.id=%d and person.id=squad.personid and 
    (squad.teamid=match.homeid or squad.teamid=match.awayid)) '''%playerid
    matches=listTable(url,getMatchesSQL)
    if(request.method == 'POST'):
        matchid=int(request.form['match'])
        minute=int(request.form['minute'])
        red=str(request.form['cardColor'])
        query = "INSERT INTO CARD (playerid,red,matchid,minute) VALUES (%d, %s ,%d,%d)" %(playerid, red, matchid,minute)
        executeSQLquery(url, [query])
    return render_template("add_card_to_player.html",matches=matches,playerid=playerid, user=current_user)

def search_player():
    url = current_app.config['db_url']
    search = request.form['search']
    listSQL = "SELECT DISTINCT p.* FROM PERSON p JOIN SQUAD s ON ((p.id = s.personid) and (lower(p.name) LIKE '%" + search.lower() + "%')) order by p.name"
    players = listTable(url, listSQL)
    return render_template("players.html", players=players, user=current_user)

def players_page():
    url = current_app.config['db_url']
    listSQL = "SELECT DISTINCT p.* FROM PERSON p JOIN SQUAD s ON (p.id = s.personid) order by name"
    players = listTable(url, listSQL)
    return render_template("players.html", players=players, user=current_user)

def coachs_page():
    url = current_app.config['db_url']
    listSQL = "select * from person join team on person.id=team.coach order by person.name"
    coachs = listTable(url, listSQL)
    return render_template("coachs.html", coachs=coachs, user=current_user)    

def search_coach():
    url = current_app.config['db_url']
    search = request.form['search']
    listSQL = "select * from person join team on person.id=team.coach  WHERE (lower(person.name) LIKE '%" + search + "%')"
    coachs = listTable(url, listSQL)
    return render_template("coachs.html", coachs=coachs, user=current_user)

def coach_page(personid):
    url = current_app.config["db_url"]
    query = "select DISTINCT * from person join team on person.id=team.coach WHERE (person.id=%d)"%personid
    result=getOneRowQuery(url,query)
    (teamID, teamName, position) = (result[5], result[6], result[7])
    person=classes.Person(id=int(result[0]),name=result[1],birthDay=int(result[2]),nationality=result[3],personphoto=result[4])
    return render_template("coach.html",coach=person, year = int(datetime.datetime.now().year), teamID = teamID, teamName = teamName, user=current_user)

def teams_page():
    url = current_app.config['db_url']
    listSQL = "SELECT t.id, t.name, t.teamlogo,l.name as leaguename FROM TEAM t LEFT JOIN LEAGUE l ON (t.leagueid = l.id)"
    teams = listTable(url, listSQL)
    return render_template("teams.html", teams=teams, user=current_user)

def search_team():
    url = current_app.config['db_url']
    search = request.form['search']
    listSQL = "SELECT * FROM TEAM WHERE (name LIKE '%" + search + "%')"
    teams = listTable(url, listSQL)
    return render_template("teams.html", teams=teams, user=current_user)

def team_page(teamid):
    url = current_app.config["db_url"]
    query = "SELECT t.id,t.name,l.name, p.name, s.name,l.country,teamlogo FROM TEAM t,LEAGUE l,PERSON p, STADIUM s WHERE (l.id=t.leagueid AND p.id=t.coach AND s.id=t.stadiumid AND t.id=%d)"%teamid
    result=getOneRowQuery(url,query)
    getSquadSQL="SELECT DISTINCT p.name,s.position,p.id FROM person p,squad s,team t where(p.id=s.personid and s.teamid=%d)"%teamid
    squad=listTable(url,getSquadSQL)
    team=classes.Team(id=int(result[0]),name=result[1],leagueID=result[2],stadiumID=result[4],coachID=result[3],teamLogo=result[6])
    return render_template("team.html",team=team,country=result[5],squad=squad, user=current_user)

@login_required
def delete_team(teamid):
    url = current_app.config['db_url']
    query = 'DELETE FROM TEAM WHERE (id=%d)'%teamid
    executeSQLquery(url, [query])
    return teams_page()

@login_required
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
        duration = int(request.form['duration'])
        startdate= int(request.form['startdate'])
        amount= int(request.form['amount'])
        query = "INSERT INTO squad (personid,teamid,position) VALUES (%d, %d ,'%s')" %(playerid, teamid, position)
        query2 ="INSERT INTO negotitation (personid,teamid,duration,amount,startdate) VALUES (%d,%d,%d,%d,%d)" %(playerid,teamid,duration,amount,startdate)
        executeSQLquery(url, [query])
        executeSQLquery(url, [query2])
    return render_template("add_player_to_squad.html",playerList=playerList,team=team, user=current_user)

@login_required
def delete_player_from_squad(playerid):
    url = current_app.config['db_url']
    getTeamIDSQL="SELECT teamid from squad where personid=%d"%playerid
    teamid=listTable(url,getTeamIDSQL)
    query = 'DELETE FROM SQUAD WHERE (personid=%d)'%playerid
    query2="delete from negotitation where (personid=%d)"%playerid
    executeSQLquery(url, [query])
    executeSQLquery(url,[query2])
    return team_page(teamid[0])

@login_required
def add_person():
    if(request.method=='POST'):
        name=request.form["name"]
        birthyear=int(request.form["birthyear"])
        nationality=request.form["nationality"]
        personphoto=request.form["personphoto"]
        query="INSERT INTO PERSON (NAME,BIRTHYEAR,NATIONALITY,PERSONPHOTO) VALUES ('%s',%d,'%s','%s')"%(name,birthyear,nationality,personphoto)
        statement=[query]
        url=current_app.config["db_url"]
        executeSQLquery(url,statement)
    return render_template("add_person.html", user=current_user)

def leagues_page():
    url = current_app.config["db_url"]
    listSQL = "SELECT * FROM LEAGUE "
    leagues = listTable(url, listSQL)
    return render_template("leagues.html",leagues=leagues, user=current_user)

def league(leagueid):
    url=current_app.config["db_url"]
    query = "select t.id, t.name, s.win, s.draw, s.lose, s.scoredgoals, s.againstgoals, (s.win+s.draw+s.lose) as gamesPlayed, (s.scoredgoals-s.againstgoals) as avarage, (s.win*3 + s.draw) as point from standing s join team t on (t.id = s.teamid) where (s.leagueid=%d) order by point desc, avarage desc ;"%leagueid
    getleaguename= "select name from league where (id=%d)"%leagueid
    leaguename= listTable(url,getleaguename)[0][0]
    standing=listTable(url,query)
    return render_template("league.html",leaguename=leaguename,standing=standing, user=current_user)

@login_required
def add_league():
    if(request.method=='POST'):
        name=request.form["name"]
        teamcount=int(request.form["teamcount"])
        country=request.form["country"]
        query="INSERT INTO LEAGUE (NAME,TEAMCOUNT,COUNTRY) VALUES ('%s',%d,'%s')"%(name,teamcount,country)
        statement=[query]
        url=current_app.config["db_url"]
        executeSQLquery(url,statement)
    return render_template("add_league.html", user=current_user)

@login_required
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
        teamLogo = request.form.get('teamLogo',False)
        query1 = "INSERT INTO team (name, leagueid, stadiumid, coach, teamlogo) VALUES ('%s', %d, %d, %d,'%s')" %(name, leagueid, stadiumid, coachid, teamLogo)
        executeSQLquery(url, [query1])
        getTeamID = "SELECT MAX(id) FROM TEAM"
        teamID = int(listTable(url, getTeamID)[0][0])
        query2 = "insert into standing (teamid, leagueid, win, lose, draw, scoredgoals, againstgoals) values (%d, %d, 0, 0, 0, 0, 0)"%(teamID, leagueid)
        executeSQLquery(url, [query2])
    return render_template("add_team.html", stadiums = stadiums, leagues = leagues, people = people, user=current_user)

@login_required
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
        if(homescore > awayscore):
            whoWin = 1
        elif (awayscore > homescore):
            whoWin = 2
        else:
            whoWin = 0
        query = "INSERT INTO match (homeid, awayid, homescore, awayscore, leagueid, stadiumid, matchdate) VALUES (%d, %d, %d, %d, %d, %d, CAST('%s' AS  DATE))" %(homeid, awayid, homescore, awayscore, leagueid, stadiumid, matchdate)
        query2 = "UPDATE standing SET win = (win + %d), draw = (draw + %d), lose = (lose + %d), scoredgoals = (scoredgoals + %d), againstgoals = (againstgoals + % d) WHERE (teamid = %d)" %(1 if whoWin == 1 else 0, 1 if whoWin == 0 else 0, 1 if whoWin == 2 else 0, homescore, awayscore, homeid)
        query3 = "UPDATE standing SET win = (win + %d), draw = (draw + %d), lose = (lose + %d), scoredgoals = (scoredgoals + %d), againstgoals = (againstgoals + % d) WHERE (teamid = %d)" %(1 if whoWin == 2 else 0, 1 if whoWin == 0 else 0, 1 if whoWin == 1 else 0, awayscore, homescore, awayid)
        queryList = [query, query2, query3]
        executeSQLquery(url, queryList)
    return render_template("add_match.html", stadiums = stadiums, leagues = leagues, teams = teams, user=current_user)

@login_required
def add_stadium():
    url = current_app.config['db_url']
    if(request.method == 'POST'):
        name = request.form['name']
        capacity = int(request.form['capacity'])
        city = request.form['city']
        query = "INSERT INTO stadium (name, capacity, city) VALUES ('%s', %d, '%s')" %(name, capacity, city) 
        executeSQLquery(url, [query])
    return render_template("add_stadium.html", user=current_user)

def stadiums_page():
    url = current_app.config["db_url"]
    listSQL = "select * from stadium join team on stadium.id = team.stadiumid "
    stadiums = listTable(url, listSQL)
    return render_template("stadiums.html",stadiums=stadiums, user=current_user)

def search_stadium():
    url = current_app.config['db_url']
    search = request.form['search']
    listSQL = "select * from stadium join team on stadium.id = team.stadiumid WHERE (name LIKE '%" + search + "%')"
    stadiums = listTable(url, listSQL)
    return render_template("stadiums.html", stadiums=stadiums, user=current_user) 

@login_required
def add_data_page():
    return render_template("add_data.html", user=current_user)
