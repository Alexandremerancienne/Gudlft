from server import app, load_clubs
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