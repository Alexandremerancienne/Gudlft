import json
from datetime import datetime

from server import app, load_clubs, load_competitions, load_purchases
from server import load_competition_places_purchased_by_club, dump_data
from random import choice, randrange

import pytest

clubs = load_clubs()
competitions = load_competitions()
purchases = load_purchases()


def reservation_date():
    time = datetime.now()
    string = time.strftime("%Y-%m-%d %H:%M:%S")
    date = datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    return date


def competition_date(competition):
    return datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")


@pytest.fixture(scope="module")
def client():
    app.config["TESTING"] = True
    yield app.test_client()
    dump_data("clubs.json", {"clubs": clubs})
    dump_data("competitions.json", {"competitions": competitions})
    dump_data("purchases.json", purchases)


@pytest.fixture()
def club():
    reload_clubs = load_clubs()
    club = choice(reload_clubs)
    return {"email": club["email"],
            "name": club["name"],
            "points": club["points"]}


@pytest.fixture
def competition():
    competition = choice(competitions)
    return {
        "name": competition["name"],
        "places": competition["places"],
        "date": competition["date"],
    }


@pytest.fixture
def future_competition():
    reload_competitions = load_competitions()
    reservation = reservation_date()
    future_competitions = [
        competition
        for competition in reload_competitions
        if competition_date(competition) >= reservation
    ]
    future_competition = choice(future_competitions)
    return {
        "name": future_competition["name"],
        "places": future_competition["places"],
        "date": future_competition["date"],
    }


@pytest.fixture
def past_competition():
    reservation = reservation_date()
    past_competitions = [
        competition
        for competition in competitions
        if competition_date(competition) < reservation
    ]
    return choice(past_competitions)


@pytest.fixture
def places():
    return randrange(1, 13)


@pytest.fixture
def affordable_places(club, future_competition):
    club_points = int(club["points"])
    competition_places = int(future_competition["places"])
    places_already_bought = load_competition_places_purchased_by_club(
        club, future_competition
    )
    print(places_already_bought)
    max_affordable_places = min(
        12 - places_already_bought, club_points, competition_places
    )
    return (
        randrange(0, max_affordable_places + 1)
        if max_affordable_places + 1 > 0
        else 0
    )


@pytest.fixture
def pair_club_competition(club, future_competition):
    with open("purchases.json", "r") as purchases_file:
        purchases_data = json.load(purchases_file)
        return {
            "club": club,
            "competition": future_competition,
            "places_purchased": purchases_data[club["email"]][
                future_competition["name"]
            ],
        }


class AuthActions(object):
    def __init__(self, client):
        self.client = client

    def login(self, club):
        return self.client.post("/showSummary", data=dict(email=club["email"]))

    def logout(self):
        return self.client.get("/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
