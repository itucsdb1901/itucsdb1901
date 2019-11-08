class Person:
	def __init__(self, id, name, birthDay, nationality):
		self.id = id
		self.name = name
		self.birthDay = birthDay
		self.nationality = nationality

class Team:
	def __init__(self, id, name, leagueID, coachID, stadiumID):
		self.id = id
		self.name = name
		self.leagueID = leagueID
		self.coachID = coachID
		self.stadiumID = stadiumID

class Squad:
	def __init__(self, teamID, personID, position):
		self.teamID = teamID
		self.personID = personID
		self.position = position

class Stadium:
	def __init__(self, id, name, capacity, city):
		self.id = id
		self.name = name
		self.capacity = capacity
		self.city = city

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
	def __init__(self, id, homeID, awayID, homeScore, awayScore, stadiumID, leagueID, date, refreeID):
		self.id = id
		self.homeID = homeID
		self.awayID = awayID
		self.homeScore = homeScore
		self.awayScore = awayScore
		self.stadiumID = stadiumID
		self.refreeID = refreeID
		self.date = date

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
