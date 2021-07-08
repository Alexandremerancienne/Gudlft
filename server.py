import json
from flask import Flask, render_template, request, redirect, flash, url_for


def load_clubs():
    with open("clubs.json") as clubs_file:
        clubs_list = json.load(clubs_file)["clubs"]
        return clubs_list


def load_competitions():
    with open("competitions.json") as competitions_file:
        competitions_list = json.load(competitions_file)["competitions"]
        return competitions_list


app = Flask(__name__)
app.secret_key = "something_special"

competitions = load_competitions()
clubs = load_clubs()


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/showSummary',methods=['POST'])
def show_summary():
    club = [club for club in clubs if club['email'] == request.form['email']]
    if len(club) == 0:
        invalid_email = "Unknown user: please enter a valid email"
        return render_template('index.html', invalid_email=invalid_email), 403
    else:
        club = club[0]
        return render_template('welcome.html',club=club,competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    foundClub = [c for c in clubs if c["name"] == club][0]
    foundCompetition = [c for c in competitions if c["name"] == competition][0]
    if foundClub and foundCompetition:
        return render_template(
            "booking.html", club=foundClub, competition=foundCompetition
        )
    else:
        flash("Something went wrong-please try again")
        return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/purchasePlaces", methods=["POST"])
def purchase_places():
    competition = [competition for competition in competitions
                   if competition["name"] == request.form["competition"]][0]
    club = [club for club in clubs if club["name"] == request.form["club"]][0]
    purchased_places = int(request.form["places"])

    insufficient_places = 'Invalid request: please enter a number of places under competition capacity'\
        if purchased_places > int(competition['places']) else ''

    insufficient_points = 'Invalid request: please enter a number of places under club points'\
        if purchased_places > int(club['points']) else ''

    purchase_limit = 'Invalid request: maximum purchase limit of 12 places for a competition'\
        if purchased_places > 12 else ''

    if purchased_places <= int(competition['places']) and purchased_places <= int(club['points'])\
            and purchased_places <= 12:
        club['points'] = str(int(club['points']) - purchased_places)
        competition['places'] = str(int(competition['places']) - purchased_places)
        flash("Great-booking complete!")
        return render_template("welcome.html", club=club, competitions=competitions)

    else:
        return render_template("welcome.html", club=club, competitions=competitions,
                               insufficient_places=insufficient_places,
                               insufficient_points=insufficient_points,
                               purchase_limit=purchase_limit), 403

# TODO: Add route for points display


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
