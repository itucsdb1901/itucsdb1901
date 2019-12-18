class Person:
	def __init__(self, id, name, birthDay, nationality, personphoto, height, weight):
		self.id = id
		self.name = name
		self.birthDay = birthDay
		self.nationality = nationality
		self.personphoto = personphoto
		self.height = height
		self.weight = weight
class Team:
	def __init__(self, id, name, leagueID, stadiumID, coach, teamLogo, fancount, city, establishyear):
		self.id = id
		self.name = name
		self.leagueID = leagueID
		self.coach = coach
		self.stadiumID = stadiumID
		self.teamLogo = teamLogo
		self.city =city
		self.fancount=fancount
		self.establishyear = establishyear

class Squad:
	def __init__(self, teamID, personID, position):
		self.teamID = teamID
		self.personID = personID
		self.position = position

class Stadium:
	def __init__(self, id, name, capacity, city, year, budget):
		self.id = id
		self.name = name
		self.capacity = capacity
		self.city = city
		self.establishyear = year
		self.budget = budget

class League:
	def __init__(self, id, name, teamcount, country):
		self.id = id
		self.name = name
		self.teamcount = teamcount
		self.country = country

class Standing:
	def __init__(self, teamID, win, draw, lose, scoredGoals, againstGoals):
		self.teamID = teamID
		self.win = win
		self.draw = draw
		self.lose = lose
		self.scoredGoals = scoredGoals
		self.againstGoals = againstGoals


class Match:
	def __init__(self, id, homeID, awayID, homeScore, awayScore, stadiumID, leagueID, date, ex1, ex2):
		self.id = id
		self.homeid = homeID
		self.awayid = awayID
		self.homescore = homeScore
		self.awayscore = awayScore
		self.stadiumid = stadiumID
		self.leagueid = leagueID
		self.matchdate = date
		self.extratime1 = ex1
		self.extratime2 = ex2


class Goal:
	def __init__(self, id, playerID, toTeamID, matchID, minute):
		self.id = id
		self.playerID = playerID
		self.toTeamID = toTeamID
		self.matchID = matchID
		self.minute = minute

class Assist:
	def __init__(self, id, playerID, goalID):
		self.id = id
		self.playerID=playerID
		self.goalID=goalID

class Card:
	def __init__(self, id, playerID, yellowOrRed, minute, matchID):
		self.id = id
		self.playerID = playerID
		self.yellowOrRed = yellowOrRed
		self.minute = minute
		self.matchID = matchID

class Substitution:
	def __init__(self, id, outPlayerID, inPlayerID, minute, matchID):
		self.id = id
		self.outPlayerID = outPlayerID
		self.inPlayerID = inPlayerID
		self.minute = minute
		self.matchID = matchID
		
class Negotiation:
	def __init__(self, id, teamID, personID, duration, startDate, amount):
		self.id = id
		self.teamID = teamID
		self.personID = personID
		self.duration = duration
		self.startDate = startDate
		self.amount = amount

class User:
	def __init__(self, username, password, name, email, age):
		self.username = username
		self.password = password
		self.name = name
		self.email = email
		self.age = age
	def is_authenticated(self):
		return True
	def is_active(self):
		return True
	def is_anonymous(self):
		return False
	def get_id(self):
		return self.username