from flask import render_template


def home_page():
    return render_template("home.html")

def matches_page():
    return render_template("matches.html")
    
def players_page():
    return render_template("players.html")
    
def teams_page():
    return render_template("teams.html")


