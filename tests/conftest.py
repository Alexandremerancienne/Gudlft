import json
from datetime import datetime

from server import app, load_clubs, load_competitions, load_purchases
from server import load_competition_places_purchased_by_club, dump_data
from random import choice, randrange

import pytest

clubs = load_clubs()
competitions = load_competitions()
purchases = load_purchases()


@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

        dump_data('clubs.json', {'clubs': clubs})
        dump_data('competitions.json', {'competitions': competitions})
        dump_data('purchases.json', purchases)


@pytest.fixture
def club():
    club = choice(clubs)
    return {'email': club['email'],
            'name': club['name'],
            'points': club['points']}


@pytest.fixture
def competition():
    competition = choice(competitions)
    return {'name': competition['name'],
            'places': competition['places'],
            'date': competition['date']}


@pytest.fixture
def future_competition():

    def reservation_date():
        time = datetime.now()
        string = time.strftime('%Y-%m-%d %H:%M:%S')
        date = (datetime.strptime(string, '%Y-%m-%d %H:%M:%S'))
        return date

    def competition_date(competition):
        return datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')

    reservation = reservation_date()
    future_competitions = [competition for competition in competitions
                           if competition_date(competition) > reservation]

    if len(future_competitions) != 0:
        future_competition = choice(future_competitions)
        return {'name': future_competition['name'],
                'places': future_competition['places'],
                'date': future_competition['date']}
    else:
        return {'name': 'Future Competition',
                'date': '2030-03-27 10:00:00',
                'places': '20'}


@pytest.fixture
def places():
    return randrange(1, 13)


@pytest.fixture
def affordable_places(club, future_competition):
    club_points = int(club['points'])
    competition_places = int(future_competition['places'])
    places_already_bought = load_competition_places_purchased_by_club(club, future_competition)
    if places_already_bought < 12:
        max_affordable_places = min(12, club_points, competition_places)
        return randrange(0, max_affordable_places + 1) \
            if max_affordable_places + 1 > 0 else 0
    else:
        return 0


@pytest.fixture
def pair_club_competition(club, future_competition):
    with open("purchases.json", "r") as purchases_file:
        purchases_data = json.load(purchases_file)
        return {'club': club, 'competition': future_competition,
                'places_purchased': purchases_data[club['email']][future_competition['name']]}


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
