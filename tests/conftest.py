import json

from server import app, load_clubs, load_competitions, load_competition_places_purchased_by_club
from random import choice, randrange

import pytest


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def club():
    clubs = load_clubs()
    club = choice(clubs)
    return {'email': club['email'],
            'name': club['name'],
            'points': club['points']}


@pytest.fixture
def competition():
    competitions = load_competitions()
    competition = choice(competitions)
    return {'name': competition['name'],
            'places': competition['places'],
            'date': competition['date']}


@pytest.fixture
def places():
    return randrange(1, 13)


@pytest.fixture
def affordable_places(club, competition):
    club_points = int(club['points'])
    competition_places = int(competition['places'])
    places_already_bought = load_competition_places_purchased_by_club(club, competition)
    if places_already_bought < 12:
        max_affordable_places = min(12, club_points, competition_places)
        return randrange(0, max_affordable_places + 1) \
            if max_affordable_places + 1 > 0 else 0
    else:
        return 0


@pytest.fixture
def pair_club_competition(club, competition):
    with open("updated_purchases.json", "r") as purchases_file:
        purchases_data = json.load(purchases_file)
        return {'club': club, 'competition': competition,
                'places_purchased': purchases_data[club['email']][competition['name']]}


class AuthActions(object):
    def __init__(self, client):
        self.client = client

    def login(self, club):
        return self.client.post('/showSummary',
                                data=dict(email=club['email']))

    def logout(self):
        return self._client.get('/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
