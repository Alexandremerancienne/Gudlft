import json
from datetime import datetime

from flask import Flask, render_template, request, redirect, flash, url_for


def load_clubs():
    with open("clubs.json") as clubs_file:
        clubs_list = json.load(clubs_file)["clubs"]
        return clubs_list


def load_competitions():
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
    with open("purchases.json") as purchases_file:
        competition_places_purchased_by_club =\
            json.load(purchases_file)[club_email][competition_name]
        return competition_places_purchased_by_club


def dump_data(file, data):
    with open(file, 'w') as file:
        json.dump(data, file, indent=4, separators=(',', ': '))


app = Flask(__name__)
app.secret_key = "something_special"

competitions = load_competitions()
clubs = load_clubs()


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/show_summary', methods=['POST'])
def show_summary():
    competitions_list = load_competitions()
    club = [club for club in clubs if club['email'] == request.form['email']]
    if len(club) == 0:
        invalid_email = "Unknown user: please enter a valid email"
        return render_template('index.html', invalid_email=invalid_email), 403
    else:
        club = club[0]
        return render_template('welcome.html',
                               club=club,
                               competitions=competitions_list)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    competitions_list = load_competitions()
    url_club = [elt for elt in clubs if elt["name"] == club][0]
    url_competition = [elt for elt in competitions_list
                       if elt["name"] == competition][0]
    if url_club and url_competition:
        return render_template("booking.html",
                               club=url_club,
                               competition=url_competition)
    else:
        flash("Something went wrong-please try again")
        return render_template("welcome.html",
                               club=club,
                               competitions=competitions)


@app.route("/purchase_places", methods=["POST"])
def purchase_places():

    competitions_list = load_competitions()
    competition = [competition for competition in competitions_list
                   if competition["name"] == request.form["competition"]][0]
    competition_index = competitions_list.index(competition)

    clubs_list = load_clubs()
    club = [club for club in clubs_list if club["name"] == request.form["club"]][0]
    club_index = clubs_list.index(club)

    places_already_bought = \
        load_competition_places_purchased_by_club(club, competition)
    purchased_places = int(request.form["places"])

    reservation = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reservation_date = (datetime.strptime(reservation,
                                          '%Y-%m-%d %H:%M:%S'))
    competition_date = datetime.strptime(competition['date'],
                                         '%Y-%m-%d %H:%M:%S')

    negative_places = 'Invalid request: please enter a positive number of places'\
        if purchased_places < 0 else ''

    insufficient_places = 'Invalid request: please enter a number of places' \
                          ' under competition capacity'\
        if purchased_places > int(competition['places']) else ''

    insufficient_points = 'Invalid request: please enter a number of places ' \
                          'under club points'\
        if purchased_places > int(club['points']) else ''

    limit_overall = 'Invalid request: maximum purchase limit of 12 places' \
        if purchased_places > 12 else ''

    competition_limit = 'Invalid request: maximum purchase limit of' \
                        ' 12 places per competition'\
        if places_already_bought + purchased_places > 12 else ''

    competition_over = 'Invalid request: this competition is over!' \
        if competition_date < reservation_date else ''

    if competition_date < reservation_date:
        return render_template("welcome.html",
                               club=club,
                               competitions=competitions_list,
                               competition_over=competition_over), 403
    else:
        if purchased_places <= int(competition['places'])\
                and purchased_places <= int(club['points'])\
                and 0 <= purchased_places <= 12\
                and places_already_bought + purchased_places <= 12:
            club['points'] = str(int(club['points']) - purchased_places)
            competition['places'] = \
                str(int(competition['places']) - purchased_places)
            flash("Great-booking complete!")

            clubs_list[club_index] = club
            competitions_list[competition_index] = competition

            with open("purchases.json", "r") as purchases_file:
                purchases_data = json.load(purchases_file)
            purchases_data[club['email']][competition['name']] \
                += purchased_places

            dump_data('clubs.json', {'clubs': clubs_list})
            dump_data('competitions.json', {'competitions': competitions_list})
            dump_data("purchases.json", purchases_data)

            return render_template("welcome.html",
                                   club=club,
                                   competitions=competitions_list)

        else:
            return render_template("welcome.html",
                                   club=club,
                                   competitions=competitions_list,
                                   negative_places=negative_places,
                                   insufficient_places=insufficient_places,
                                   insufficient_points=insufficient_points,
                                   limit_overall=limit_overall,
                                   competition_limit=competition_limit), 403


@app.route("/points_board")
def display_points():
    clubs_list = load_clubs()
    return render_template("board.html", clubs=clubs_list)


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
