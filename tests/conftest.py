from server import app, load_clubs, load_competitions
from random import choice

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
            'places': competition['places']}


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