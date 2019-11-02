from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def home_page():
    return render_template("home.html")

@app.route("/matches")
def matches_page():
    return render_template("matches.html")
    
@app.route("/players")
def players_page():
    return render_template("players.html")
    
@app.route("/teams")
def teams_page():
    return render_template("teams.html")



if __name__ == "__main__":
    app.run()
