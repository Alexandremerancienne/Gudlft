from random import choice
from server import load_clubs, dump_data, load_competitions, load_purchases
from tests.conftest import load_future_competition

from locust import HttpUser, task, between

clubs = load_clubs()
competitions = load_competitions()
purchases = load_purchases()


class WebsiteUser(HttpUser):
    wait_time = between(1, 10)
    host = 'http://127.0.0.1:5000/'

    club = choice(clubs)
    competition = load_future_competition()

    def on_start(self):
        self.client.post("/show_summary", {
            "email": self.club['email'],
        })

    @task
    def index(self):
        self.client.get("/")

    @task
    def points_board(self):
        self.client.get("/points_board")

    @task
    def book(self):
        self.client.get("/book/" + self.competition['name'] + "/" + self.club['name'])

    @task
    def purchase(self):
        self.client.post("/purchase_places", {"club": self.club['name'],
                                              "competition": self.competition['name'],
                                              "places": '0'})

    def on_stop(self):
        self.client.get("/logout")
        dump_data("clubs.json", {"clubs": clubs})
        dump_data("competitions.json", {"competitions": competitions})
        dump_data("purchases.json", purchases)
