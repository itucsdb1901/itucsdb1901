from flask import render_template, request, current_app, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, current_user, login_user
import sys
import psycopg2 as dbapi2
import classes
from classes import User
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


#####Authentication Related Functions####
def checkSignIn():
    if (request.method=="POST"):
        url=current_app.config["db_url"]
        username = request.form.get("username",False)
        password = request.form.get("password",False)
        checkUser="SELECT a.username, a.password, a.name, a.age, a.email FROM ACCOUNT a WHERE(a.username='%s')"%(username)
        result=getOneRowQuery(url,checkUser)
        if(result is not None):
            if check_password_hash(result[1], password):
                user = User(username, result[1], result[2], result[3], result[4])
                remember = request.form.get("remember",False)
                if remember is not None:
                    current_app.config['USE_SESSION_FOR_NEXT'] = True
                    login_user(user, remember=True)
                else:
                    current_app.config['USE_SESSION_FOR_NEXT'] = False
                    login_user(user, remember=False)            
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
        name = request.form.get("name",False)
        email = request.form.get("email",False)
        age = int(request.form.get("age",False))
        checkExist = "SELECT username FROM ACCOUNT WHERE (username = '%s')" %(username)
        checkExist = getOneRowQuery(url, checkExist)
        if(checkExist is not None):
            return render_template("signup.html", error=1, user = current_user)
        password = generate_password_hash(password, method="sha256")
        saveUser = "INSERT INTO ACCOUNT (username, password, name, email, age) VALUES ('%s', '%s', '%s', '%s', %d)"%(username, password, name, email, age)
        executeSQLquery(url, [saveUser])
        user = User(username, password, name, email, age)
        login_user(user, remember=True)
        return redirect('/')
    return render_template("signup.html", error=0, user = current_user)

@login_required
def delete_account():
    url = current_app.config["db_url"]
    query = "DELETE FROM ACCOUNT WHERE username = '%s'"%current_user.username
    executeSQLquery(url, [query])
    redirect(url_for('logOut'))

@login_required
def update_account():
    if(request.method == "POST"):
        url=current_app.config["db_url"]
        oldpassword = request.form.get("oldpassword",False)
        if check_password_hash(current_user.password, oldpassword):
            password = request.form.get("password",False)
            name = request.form.get("name",False)
            email = request.form.get("email",False)
            age = int(request.form.get("age",False))
            if password is not False:
                password = generate_password_hash(password, method="sha256")
            else:
                password = user.password
            query = "UPDATE ACCOUNT SET password='%s', name='%s', email='%s', age=%d WHERE USERNAME='%s'" %(password, name, email, age, current_user.username)
            user = User(current_user.username, password, name, email, age)
            logout_user()
            login_user(user, remember=True)
            return redirect('/')
        else:
            render_template("signup.html", error=1, user = current_user, update=True)
    return render_template("signup.html", error=0, user = current_user, update=True)

@login_required
def logOut():
    logout_user()
    return redirect(url_for('home_page'))


#########Home Page Function############
def home_page():
    url=current_app.config["db_url"]
    team_count = "SELECT COUNT(*) FROM TEAM"
    team_count = (listTable(url, team_count)[0][0])
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
                "current_user":current_user,
                "teams_count":team_count

                }
    return render_template("home.html", arguments=arguments, user=current_user)


#####Person Related Functions###########
@login_required
def add_person():
    if(request.method=='POST'):
        name=request.form["name"]
        birthyear=int(request.form["birthyear"])
        nationality=request.form["nationality"]
        weight=int(request.form["weight"])
        height=int(request.form["height"])
        personphoto=request.form["personphoto"]
        query="INSERT INTO PERSON (NAME,BIRTHYEAR,NATIONALITY,PERSONPHOTO,height,weight) VALUES ('%s',%d,'%s','%s', %d,%d)"%(name,birthyear,nationality,personphoto,height,weight)
        statement=[query]
        url=current_app.config["db_url"]
        executeSQLquery(url,statement)
    return render_template("add_person.html", user=current_user)

@login_required
def update_person(personid):
    url = current_app.config['db_url']
    person = "select * from person p where p.id = %d " %personid
    person = getOneRowQuery(url, person)
    person = classes.Person(person[0], person[1], person[2], person[3], person[4], person[5], person[6])
    update = True
    if(request.method=='POST'):
        name=request.form["name"]
        birthyear=int(request.form["birthyear"])
        nationality=request.form["nationality"]
        weight=int(request.form["weight"])
        height=int(request.form["height"])
        personphoto=request.form["personphoto"]
        query="UPDATE PERSON SET NAME='%s', BIRTHYEAR=%d, NATIONALITY='%s', PERSONPHOTO='%s', height=%d, weight=%d WHERE id = %d"%(name,birthyear,nationality,personphoto,height,weight, personid)
        statement=[query]
        url=current_app.config["db_url"]
        executeSQLquery(url,statement)
        return redirect(url_for('home_page'))
    return render_template("add_person.html", user=current_user, person=person, update=update)


#####Player Related Functions####
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
    amount=negotitation[5]
    duration=negotitation[3]
    startdate=negotitation[4]
    scoredgoal=number_goal[0]
    yellowcardx = yellowcardy[0]
    redcardx = redcardy[0]
    (teamID, teamName, position) = (result[7], result[8], result[9])
    (playerID, name, birthDay, nationality, photo, height, weight) = (result[0], result[1], result[2], result[3], result[4], result[5], result[6])
    person=classes.Person(playerID, name, birthDay, nationality, photo, height, weight)
    return render_template("player.html",player=person, year = int(datetime.datetime.now().year), teamID = teamID, teamName = teamName, position = position,scoredgoal=scoredgoal,amount=amount,duration=duration,startdate=startdate,redcardx=redcardx,yellowcardx=yellowcardx, user=current_user )

@login_required
def delete_player(personid):
    url = current_app.config['db_url']
    query = 'DELETE FROM PERSON WHERE (id=%d)'%personid
    executeSQLquery(url, [query])
    return players_page()

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


#####Coach Related Functions####
def coachs_page():
    url = current_app.config['db_url']
    listSQL = "select * from person join team on person.id=team.coach order by person.name"
    coachs = listTable(url, listSQL)
    return render_template("coachs.html", coachs=coachs, user=current_user)    

def search_coach():
    url = current_app.config['db_url']
    search = request.form['search']
    listSQL = "select * from person join team on person.id=team.coach  WHERE (lower(person.name) LIKE '%" + search.lower() + "%')"
    coachs = listTable(url, listSQL)
    return render_template("coachs.html", coachs=coachs, user=current_user)

def coach_page(personid):
    url = current_app.config["db_url"]
    query = "select p.id, p.name, p.birthyear, p.nationality, p.personphoto, p.height, p.weight, t.id, t.name from person p join team t on p.id=t.coach WHERE (p.id=%d)"%personid
    result=getOneRowQuery(url,query)
    (id, name, birthDay, nationality, personphoto, height, weight) = (result[0], result[1], result[2], result[3], result[4], result[5], result[6])
    (teamID, teamName) = (result[7], result[8])
    person=classes.Person(id, name, birthDay, nationality, personphoto, height, weight)
    return render_template("coach.html",coach=person, year = int(datetime.datetime.now().year), teamID = teamID, teamName = teamName, user=current_user)


#####Team Related Functions####
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
    query = "SELECT t.id, t.name, t.leagueid, t.stadiumid, t.coach, t.teamlogo, t.fancount, t.city, t.establishyear, l.name, l.country, p.name, s.name FROM TEAM t,LEAGUE l,PERSON p, STADIUM s WHERE (l.id=t.leagueid AND p.id=t.coach AND s.id=t.stadiumid AND t.id=%d)"%teamid
    result=getOneRowQuery(url,query)
    (id, name, leagueID, stadiumID, coach, teamLogo, fancount, city, establishyear) = (result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])
    (leagueName, country, coachName, stadiumName) = (result[9], result[10], result[11], result[12])
    team=classes.Team(id, name, leagueID, stadiumID, coach, teamLogo, fancount, city, establishyear)
    getSquadSQL="SELECT DISTINCT p.name,s.position,p.id FROM person p,squad s,team t where(p.id=s.personid and s.teamid=%d)"%teamid
    squad=listTable(url,getSquadSQL)
    return render_template("team.html",team=team,squad=squad, leagueName = leagueName, coachName = coachName, stadiumName = stadiumName, user=current_user)

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
        name = request.form.get('name', False)
        coachid = int(request.form['coach'])
        leagueid = int(request.form['league'])
        stadiumid = int(request.form['stadium'])
        fancount = int(request.form['fancount'])
        teamcity = request.form['teamcity']
        establish_year = int(request.form['establish_year'])
        teamLogo = request.form.get('teamLogo',False)
        query1 = "INSERT INTO team (name, leagueid, stadiumid, coach, teamlogo, fancount, city, establishyear) VALUES ('%s', %d, %d, %d,'%s', %d, '%s', %d)" %(name, leagueid, stadiumid, coachid, teamLogo, fancount, teamcity, establish_year)
        executeSQLquery(url, [query1])
        getTeamID = "SELECT MAX(id) FROM TEAM"
        teamID = int(listTable(url, getTeamID)[0][0])
        query2 = "insert into standing (teamid, leagueid, win, lose, draw, scoredgoals, againstgoals) values (%d, %d, 0, 0, 0, 0, 0)"%(teamID, leagueid)
        executeSQLquery(url, [query2])
    return render_template("add_team.html", stadiums = stadiums, leagues = leagues, people = people, user=current_user)

def update_team(teamid):
    url = current_app.config['db_url']
    update = True
    getTeamSQL = "SELECT t.id, t.name, t.leagueid, t.stadiumid, t.coach, t.teamlogo, t.fancount, t.city, t.establishyear FROM team t where t.id = %d" %teamid
    team = listTable(url, getTeamSQL)[0]
    team = classes.Team(team[0], team[1], team[2], team[3], team[4], team[5], team[6], team[7], team[8])
    getPeopleSQL = "SELECT * FROM person"
    getStadiumsSQL = "SELECT * FROM stadium"
    getLeaguesSQL = "SELECT * FROM league"
    people = listTable(url, getPeopleSQL)
    leagues = listTable(url, getLeaguesSQL)
    stadiums = listTable(url, getStadiumsSQL)
    if(request.method == 'POST'):
        name = request.form.get('name', False)
        coachid = int(request.form['coach'])
        leagueid = int(request.form['league'])
        stadiumid = int(request.form['stadium'])
        fancount = int(request.form['fancount'])
        teamcity = request.form['teamcity']
        establish_year = int(request.form['establish_year'])
        teamLogo = request.form.get('teamLogo',False)
        query1 = "UPDATE team SET name='%s', leagueid=%d, stadiumid=%d, coach=%d, teamlogo='%s', fancount=%d, city='%s', establishyear=%d WHERE id = %d" %(name, leagueid, stadiumid, coachid, teamLogo, fancount, teamcity, establish_year, teamid)
        query2 = "UPDATE standing SET leagueid = %d WHERE teamid = %d"%(leagueid, teamid)
        executeSQLquery(url, [query1, query2])
        return redirect(url_for("teams_page"))
    return render_template("add_team.html", team = team, stadiums = stadiums, leagues = leagues, people = people, user=current_user, update=update)


#####League Related Functions####
def leagues_page():
    url = current_app.config["db_url"]
    listSQL = "SELECT * FROM LEAGUE "
    leagues = listTable(url, listSQL)
    return render_template("leagues.html",leagues=leagues, user=current_user)

def league(leagueid):
    url=current_app.config["db_url"]
    scoredgoals= "none"
    againstgoals="none"
    gamesplayed="none"
    scored=False
    against=False
    played=False
    if(request.method=='POST'):
        scoredgoals=request.form.get("scoredgoals",False) 
        againstgoals=request.form.get("againstgoals", False)
        gamesplayed=request.form.get("gamesplayed", False)
    if(scoredgoals == "filterscored"):
        scored=True
        if(againstgoals == "filteragainst"):
            against=True
        if(againstgoals == "filteragainst" and gamesplayed == "filterplayed"):
            against=True
            played=True
    elif(againstgoals == "filteragainst"):
        against=True
        if(gamesplayed == "filterplayed"):
            played=True
    elif(gamesplayed == "filterplayed"):
        played=True
    query = "select t.id, t.name, s.win, s.draw, s.lose, s.scoredgoals, s.againstgoals, (s.win+s.draw+s.lose) as gamesPlayed, (s.scoredgoals-s.againstgoals) as avarage, (s.win*3 + s.draw) as point from standing s join team t on (t.id = s.teamid) where (s.leagueid=%d) order by point desc, avarage desc ;"%leagueid
    getleaguename= "select name from league where (id=%d)"%leagueid
    leaguename= listTable(url,getleaguename)[0][0]
    standing=listTable(url,query)
    return render_template("league.html",leaguename=leaguename,standing=standing, user=current_user, scored=scored, against=against, played=played)

@login_required
def add_league():
    if(request.method=='POST'):
        name=request.form["name"]
        teamcount=int(request.form["teamcount"])
        country=request.form["country"]
        establishyear=int(request.form["establishyear"])
        division=int(request.form["division"])
        query="INSERT INTO LEAGUE (NAME,TEAMCOUNT,COUNTRY, ESTABLISHYEAR, DIVISION) VALUES ('%s',%d,'%s', %d, %d)"%(name,teamcount,country, establishyear, division)
        statement=[query]
        url=current_app.config["db_url"]
        executeSQLquery(url,statement)
    return render_template("add_league.html", user=current_user)


#####Stadium Related Functions####
@login_required
def add_stadium():
    url = current_app.config['db_url']
    if(request.method == 'POST'):
        name = request.form['name']
        capacity = int(request.form['capacity'])
        city = request.form['city']
        establishyear = int(request.form['establishyear'])
        budget = int(request.form['budget'])
        query = "INSERT INTO stadium (name, capacity, city, establishyear, budget) VALUES ('%s', %d, '%s', %d, %d)" %(name, capacity, city, establishyear, budget) 
        executeSQLquery(url, [query])
    return render_template("add_stadium.html", user=current_user)

def stadiums_page():
    url = current_app.config["db_url"]
    listSQL = "select s.name, team.name, s.capacity, s.city, s.establishyear, s.budget, s.id from stadium s join team on s.id = team.stadiumid "
    stadiums = listTable(url, listSQL)
    return render_template("stadiums.html",stadiums=stadiums, user=current_user)

def search_stadium():
    url = current_app.config['db_url']
    search = request.form['search']
    listSQL = "select s.name, team.name, s.capacity, s.city, s.establishyear, s.budget, s.id from stadium s join team on s.id = team.stadiumid "
    listSQL = listSQL + "WHERE (lower(s.name) LIKE '%" + search.lower() + "%')"
    stadiums = listTable(url, listSQL)
    return render_template("stadiums.html", stadiums=stadiums, user=current_user) 

def order_stadium(ordertype):
    url = current_app.config['db_url']
    listSQL = "select s.name, team.name, s.capacity, s.city, s.establishyear, s.budget, s.id from stadium s join team on s.id = team.stadiumid "
    if ordertype == 0:
        order = "order by s.name"
    elif ordertype == 1:
        order = "order by team.name"
    elif ordertype == 2:
        order = "order by s.capacity desc"
    elif ordertype == 3:
        order = "order by s.city"
    elif ordertype == 4:
        order = "order by s.establishyear desc"
    else:
        order = "order by s.budget desc"
    listSQL = listSQL + order
    stadiums = listTable(url, listSQL)
    return render_template("stadiums.html", stadiums=stadiums, user=current_user) 

@login_required
def update_stadium(stadiumid):
    url = current_app.config['db_url']
    stadium = "select * from stadium s where s.id = %d " %stadiumid
    stadium = getOneRowQuery(url, stadium)
    stadium = classes.Stadium(stadium[0], stadium[1], stadium[2], stadium[3], stadium[4], stadium[5])
    update = True
    if(request.method == 'POST'):
        name = request.form['name']
        capacity = int(request.form['capacity'])
        city = request.form['city']
        establishyear = int(request.form['establishyear'])
        budget = int(request.form['budget'])
        query = "UPDATE stadium SET name = '%s', capacity = %d, city = '%s', establishyear = %d, budget = %d WHERE id = %d" %(name, capacity, city, establishyear, budget, stadiumid) 
        executeSQLquery(url, [query])
        return redirect(url_for('stadiums_page'))    
    return render_template("add_stadium.html", stadium=stadium, user=current_user, update=update) 


#####Match Related Functions####
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
        extratime1 = int(request.form['extratime1'])
        extratime2 = int(request.form['extratime2'])
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
        query = "INSERT INTO match (homeid, awayid, homescore, awayscore, extratime1, extratime2, leagueid, stadiumid, matchdate) VALUES (%d, %d, %d, %d, %d, %d, %d, %d, CAST('%s' AS  DATE))" %(homeid, awayid, homescore, awayscore, extratime1, extratime2, leagueid, stadiumid, matchdate)
        query2 = "UPDATE standing SET win = (win + %d), draw = (draw + %d), lose = (lose + %d), scoredgoals = (scoredgoals + %d), againstgoals = (againstgoals + % d) WHERE (teamid = %d)" %(1 if whoWin == 1 else 0, 1 if whoWin == 0 else 0, 1 if whoWin == 2 else 0, homescore, awayscore, homeid)
        query3 = "UPDATE standing SET win = (win + %d), draw = (draw + %d), lose = (lose + %d), scoredgoals = (scoredgoals + %d), againstgoals = (againstgoals + % d) WHERE (teamid = %d)" %(1 if whoWin == 2 else 0, 1 if whoWin == 0 else 0, 1 if whoWin == 1 else 0, awayscore, homescore, awayid)
        queryList = [query, query2, query3]
        executeSQLquery(url, queryList)
    return render_template("add_match.html", stadiums = stadiums, leagues = leagues, teams = teams, user=current_user)

@login_required
def delete_match(matchid):
    url = current_app.config['db_url']
    query = "delete from card c where (c.matchid=%d)"%matchid
    executeSQLquery(url,[query])
    query = "delete from substitution s where s.matchid=%d"%matchid
    executeSQLquery(url,[query])
    query = "delete from assist a where (a.goalid in (select id from goal g where matchid=%d)) "%matchid
    executeSQLquery(url,[query])
    query = "delete from goal g where (g.matchid=%d)"%matchid
    executeSQLquery(url,[query])
    query = "delete from match m where (m.id=%d)"%matchid
    executeSQLquery(url,[query])
    return matches_page()

def matches_page():
    url = current_app.config['db_url']
    query = '''SELECT t1.name, t2.name, m.homescore, m.awayscore, std.name, lg.name, m.matchdate, m.homeid, m.awayid ,m.id 
                FROM match m, team t1, team t2, stadium std, league lg
                    WHERE (m.homeid = t1.id AND m.awayid = t2.id 
                        AND m.stadiumid = std.id AND m.leagueid = lg.id) ORDER BY lg.name ASC'''
    matches = listTable(url, query)
    return render_template("matches.html", matches = matches, user=current_user)

def match_detail(matchid):
    url = current_app.config["db_url"]
    query="SELECT t1.name as home,t2.name as away,m.homescore,m.awayscore FROM MATCH m join team t1 on (t1.id=m.homeid) join team t2 on (t2.id=m.awayid) WHERE (m.id=%d)"%matchid
    teams = listTable(url,query)
    query="SELECT p.name,c.red,c.minute,c.id as cardid,c.yellow1,c.yellow2,c.banduration FROM MATCH m LEFT JOIN CARD c ON (c.matchid=m.id) JOIN PERSON p ON (p.id=c.playerid)  WHERE(m.id=%d) ORDER BY c.minute ASC"%matchid
    cards = listTable(url, query)
    query="SELECT p.name as playername,g.minute,t.name as teamname,g.id as goalid FROM MATCH m LEFT JOIN goal g ON (g.matchid=m.id) JOIN person p on (p.id=g.playerid) JOIN SQUAD s ON (s.personid=p.id) JOIN TEAM t ON (t.id=s.teamid) WHERE (m.id=%d) ORDER BY g.minute ASC"%matchid
    goals = listTable(url,query)
    query="SELECT p1.name as outname,p2.name as inname,s.minute,s.aftercorner,s.afteroffside,s.aftergoal,s.afterout,s.id as subid FROM MATCH m LEFT JOIN SUBSTITUTION s ON (s.matchid=m.id) JOIN person p1 on (p1.id=s.outplayerid) JOIN person p2 on (p2.id=s.inplayerid)  where m.id=%d order by s.minute ASC"%matchid
    substitutions = listTable(url,query)
    return render_template("match_detail.html",cards=cards,goals=goals,substitutions=substitutions,teams=teams,user=current_user)

@login_required
def add_match_detail(matchid):
    url = current_app.config["db_url"]
    query1="select p.id,p.name,s.teamid from match m join squad s on (s.teamid=m.homeid or s.teamid=m.awayid) join person p on(p.id=s.personid) where(m.id=%d)"%matchid
    players=listTable(url,query1)
    if(request.method=='POST'):
        outplayerid=int(request.form["outplayerid"])
        inplayerid=int(request.form["inplayerid"])
        minute=int(request.form["minute"])
        aftercorner=str(request.form["afterCorner"])
        afteroffside=str(request.form["afterOffside"])
        aftergoal=str(request.form["afterGoal"])
        afterout=str(request.form["afterOut"])
        query="INSERT INTO substitution (outplayerid,inplayerid,matchid,minute,aftercorner,afteroffside,aftergoal,afterout) VALUES (%d,%d,%d,%d,'%s','%s','%s','%s')"%(outplayerid,inplayerid,matchid,minute,aftercorner,afteroffside,aftergoal,afterout)
        executeSQLquery(url,[query])

    return render_template("add_match_detail.html", user=current_user, players=players,matchid=matchid)

@login_required
def delete_substitution(subid):
    url=current_app.config["db_url"]
    query="delete from substitution where id =%d"%subid
    executeSQLquery(url,[query])
    return matches_page()


#####Goal Related Functions####
@login_required
def add_goal(personid):
    url = current_app.config["db_url"]
    infoQuery = "SELECT p.*, t.id, t.name FROM PERSON p LEFT JOIN SQUAD s ON (s.personid = p.id) LEFT JOIN TEAM t ON (s.teamid = t.id) WHERE (p.id=%d)"%personid
    result=getOneRowQuery(url,infoQuery)
    person=classes.Person(int(result[0]),result[1],int(result[2]),result[3],result[4],int(result[5]),int(result[6]),)
    teamID = result[7]
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
        matchID = int(request.form.get('matchid', False))
        minute = int(request.form.get('minute', False))
        goaltype = int(request.form.get('goaltype', False))
        distance = int(request.form.get('distance', False))
        isfreekickgoal = request.form.get('isfreekickgoal', False)
        goalrating = int(request.form.get('goalrating', False))
        addGoalQuery = "INSERT INTO GOAL (matchid, playerid, minute, goaltype, distance, isfreekick, rating) VALUES (%d, %d, %d, %d, %d, '%s', %d)" %(matchID, personid, minute, goaltype, distance, isfreekickgoal, goalrating)
        executeSQLquery(url, [addGoalQuery])
        findGoalIDSQL = "SELECT max(id) FROM GOAL"
        goalID = int(getOneRowQuery(url, findGoalIDSQL)[0])
        assistPlayerID = int(request.form.get('assistPlayerid', False))
        if(assistPlayerID != False):
            passdistance = int(request.form.get('passdistance', False))
            iscross = request.form.get('iscross', False)
            assisttype = int(request.form.get('assisttype', False))
            isfreekickassist = request.form.get('isfreekickassist', False)
            assistrating = int(request.form.get('assistrating', False))
            addAssistQuery = "INSERT INTO ASSIST (playerid, goalid, passdistance, assisttype, isfreekick, iscross, rating) VALUES (%d, %d, %d, %d, '%s', '%s', %d)"%(assistPlayerID, goalID, passdistance, assisttype, isfreekickassist, iscross, assistrating)
            executeSQLquery(url, [addAssistQuery])
    return render_template("add_goal.html", matches=matches, person=person, assistPlayers = assistPlayers, user=current_user)

@login_required
def delete_goal(goalid):
    url=current_app.config['db_url']
    query="delete from assist a where a.goalid=%d "%goalid
    executeSQLquery(url,[query])
    query="delete from goal where id = %d"%goalid
    executeSQLquery(url,[query])
    return matches_page()


#####Card Related Functions####
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
        yellow1st=str(request.form.get('firstyellow','false'))
        banduration=int(request.form.get('banduration',0))
        if(red == 'false'):
            if(yellow1st == 'true'):
                yellow2st='false'
            else:
                yellow2st='true'
                red = 'true'
                banduration=1
        else:
            yellow1st = 'false'
            yellow2st = 'false'
        
        query = "INSERT INTO CARD (playerid,red,matchid,minute,yellow1,yellow2,banduration) VALUES (%d, '%s', %d ,%d ,'%s' ,'%s' ,%d)" %(playerid, red, matchid, minute, yellow1st, yellow2st, banduration)
        executeSQLquery(url, [query])
    return render_template("add_card_to_player.html",matches=matches,playerid=playerid, user=current_user)

@login_required
def delete_card(cardid):
    url=current_app.config['db_url']
    query="DELETE FROM CARD c WHERE c.id=%d"%cardid
    executeSQLquery(url,[query])
    return matches_page()


#####Squad Related Functions####
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
        secondposition = request.form['secondposition']
        foot = request.form['foot']
        playerid = int(request.form['playerbox'])
        kitnumber = int(request.form['kitnumber'])
        injurymonth = int(request.form['injurymonth'])
        amount= int(request.form['amount'])
        duration = int(request.form['duration'])
        startdate= request.form['startdate']
        startdate = datetime.datetime.strptime(startdate, '%Y').date()
        amount= int(request.form['amount'])
        releasecost=int(request.form['releasecost'])
        isrent=str(request.form['isRent'])
        query = "INSERT INTO squad (personid,teamid,position, secondposition, foot, kitnumber, injurymonth) VALUES (%d, %d ,'%s', '%s', '%s', %d, %d)" %(playerid, teamid, position, secondposition, foot, kitnumber, injurymonth)
        query2 ="INSERT INTO negotitation (personid,teamid,duration,startdate,amount,relasecost,isrent) VALUES (%d,%d,%d,CAST('%s' AS  DATE),%d,%d,'%s')" %(playerid,teamid,duration,startdate,amount,releasecost,isrent)
        executeSQLquery(url, [query, query2])
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


#####Add Data Function####
@login_required
def add_data_page():
    return render_template("add_data.html", user=current_user)