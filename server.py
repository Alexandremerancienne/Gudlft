import json
import pathlib
from flask import Flask, render_template, request, redirect, flash, url_for


def load_clubs():
    if pathlib.Path("updated_clubs.json").exists():
        with open("updated_clubs.json") as clubs_file:
            clubs_list = json.load(clubs_file)["clubs"]
    else:
        with open("clubs.json") as clubs_file:
            clubs_list = json.load(clubs_file)["clubs"]
    return clubs_list


def load_competitions():
    if pathlib.Path("updated_competitions.json").exists():
        with open("updated_competitions.json") as competitions_file:
            competitions_list = json.load(competitions_file)["competitions"]
    else:
        with open("competitions.json") as competitions_file:
            competitions_list = json.load(competitions_file)["competitions"]
    return competitions_list


def load_purchases():
    with open("purchases.json") as purchases_file:
        purchases_list = json.load(purchases_file)
        return purchases_list


def load_competition_places_purchased_by_club(club, competition):
    club_email = club['email']
    competition_name = competition['name']
    if pathlib.Path("updated_purchases.json").exists():
        with open("updated_purchases.json") as purchases_file:
            competition_places_purchased_by_club =\
                json.load(purchases_file)[club_email][competition_name]
    else:
        with open("purchases.json") as purchases_file:
            competition_places_purchased_by_club =\
                json.load(purchases_file)[club_email][competition_name]
    return competition_places_purchased_by_club


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
        return render_template('welcome.html', club=club, competitions=competitions)


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
    competitions_list = load_competitions()
    competition_index = competitions_list.index(competition)

    club = [club for club in clubs if club["name"] == request.form["club"]][0]
    clubs_list = load_clubs()
    club_index = clubs_list.index(club)

    places_already_bought = load_competition_places_purchased_by_club(club, competition)
    purchased_places = int(request.form["places"])

    insufficient_places = 'Invalid request: please enter a number of places under competition capacity'\
        if purchased_places > int(competition['places']) else ''

    insufficient_points = 'Invalid request: please enter a number of places under club points'\
        if purchased_places > int(club['points']) else ''

    purchase_limit_overall = 'Invalid request: maximum purchase limit of 12 places' \
        if purchased_places > 12 else ''

    purchase_limit_per_competition = 'Invalid request: maximum purchase limit of 12 places per competition'\
        if places_already_bought + purchased_places > 12 else ''

    if purchased_places <= int(competition['places']) and purchased_places <= int(club['points'])\
            and purchased_places <= 12 and places_already_bought + purchased_places <= 12:
        club['points'] = str(int(club['points']) - purchased_places)
        competition['places'] = str(int(competition['places']) - purchased_places)
        flash("Great-booking complete!")

        clubs_list[club_index] = club
        competitions_list[competition_index] = competition

        with open('updated_clubs.json', 'w') as clubs_file:
            json.dump({'clubs': clubs_list}, clubs_file)

        with open('updated_competitions.json', 'w') as competitions_file:
            json.dump({'competitions': competitions_list}, competitions_file)

        if pathlib.Path("updated_purchases.json").exists():
            with open("updated_purchases.json", "r") as purchases_file:
                purchases_data = json.load(purchases_file)
        else:
            with open("purchases.json", "r") as purchases_file:
                purchases_data = json.load(purchases_file)

        purchases_data[club['email']][competition['name']] += purchased_places

        with open("updated_purchases.json", "w") as purchases_file:
            json.dump(purchases_data, purchases_file)

        return render_template("welcome.html", club=club, competitions=competitions)

    else:
        return render_template("welcome.html", club=club, competitions=competitions,
                               insufficient_places=insufficient_places,
                               insufficient_points=insufficient_points,
                               purchase_limit_overall=purchase_limit_overall,
                               purchase_limit_per_competition=purchase_limit_per_competition), 403

# TODO: Add route for points display


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
