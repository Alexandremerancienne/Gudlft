from ..conftest import load_future_competition

load_future_competition()


def test_welcome_page_loads(client):
    """
    GIVEN a test client
    WHEN the '/' page is requested (GET)
    THEN check that:
    1) A '200' status code is returned
    2) The response includes the message:
    'Welcome to the GUDLIFT Registration Portal!'
    """

    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the GUDLFT Registration Portal!" in response.data


def test_login_for_registered_user_returns_success(client, club):
    """
    GIVEN a test client with a registered email
    WHEN a POST request is sent to '/showSummary' page with the client's email
    THEN check that:
    1) A '200' status code is returned
    2) The response includes the message:
    'Welcome, <email>'
    """
    response = client.post("/show_summary", data=dict(email=club["email"]))
    assert response.status_code == 200
    assert f"Welcome, {club['email']}" in response.get_data(as_text=True)


def test_login_for_unregistered_user_returns_error(client, club):
    """
    GIVEN a test client with an unregistered email (null object)
    WHEN a POST request is sent to '/showSummary' page with the client's email
    THEN check that:
     1) A '403' status code (Forbidden) is returned
    2) The response includes the message:
    'Unknown user: please enter a valid mail'
    """
    club["email"] = "unknown-user@bot.com"
    response = client.post("/show_summary", data=dict(email=club["email"]))
    assert response.status_code == 403
    assert b"Unknown user: please enter a valid email" in response.data


def test_logout_works(auth):
    """
    GIVEN a test client
    WHEN a POST request is sent to '/logout' page
    THEN check that headers will have 'localhost' as Location header
    """
    response = auth.logout()
    assert response.status_code == 302
    assert "http://localhost/" == response.headers["Location"]


def test_select_a_competition_returns_competition_details(
    auth, client, club, competition
):
    """
    GIVEN an authenticated test client
    WHEN the '/book/<competition>/<club>' page is requested (GET)
    THEN check that:
    1) A '200' status code is returned
    2) The response includes the competition name
    3) The response includes the number of places available
    """
    auth.login(club)
    response = client.get("/book/" + competition["name"] + "/" + club["name"])
    assert response.status_code == 200
    assert f"{competition['name']}" in response.get_data(as_text=True)
    assert f"{int(competition['places'])}" in response.get_data(as_text=True)


def test_purchase_reduces_club_points_and_competition_places(
    auth, client, club, future_competition, affordable_places
):
    """
    GIVEN an authenticated test client
    WHEN a POST request is sent to '/purchasePlaces' page to purchase x places
    THEN check that the number of club points is reduced by x
    """
    auth.login(club)
    response = client.post(
        "/purchase_places",
        data=dict(
            club=club["name"],
            competition=future_competition["name"],
            places=affordable_places,
        ),
    )
    assert (
        f"Points available: {str(int(club['points']) - 3*affordable_places)}"
        in response.get_data(as_text=True)
    )
    assert (
        f"Number of Places: "
        f"{str(int(future_competition['places']) - affordable_places)}"
        in response.get_data(as_text=True)
    )


def test_cannot_purchase_negative_places(
        auth, client, club, future_competition, negative_places
):
    """
    GIVEN an authenticated test client
    WHEN a POST request is sent to '/purchasePlaces'
    with a negative number of places
    THEN check that:
    1) A '403' status code is returned
    2) The response includes the message:
    'Invalid request: please enter a positive number of places'
    """
    auth.login(club)
    response = client.post(
        "/purchase_places",
        data=dict(
            club=club["name"],
            competition=future_competition["name"],
            places=str(negative_places),
        ),
    )
    assert response.status_code == 403
    assert (
            b"Invalid request: please enter a positive number of places"
            in response.data
    )


def test_cannot_purchase_more_than_club_points(
    auth, client, club, future_competition, places
):
    """
    GIVEN an authenticated test client
    WHEN a POST request is sent to '/purchasePlaces'
    with a number of places exceeding the number of club's points
    THEN check that:
    1) A '403' status code is returned
    2) The response includes the message:
    'Invalid request: please enter a number of places under club points'
    """
    auth.login(club)
    response = client.post(
        "/purchase_places",
        data=dict(
            club=club["name"],
            competition=future_competition["name"],
            places=str(int(club["points"]) + places),
        ),
    )
    assert response.status_code == 403
    assert (
        b"Invalid request: please enter a number of places under club points"
        in response.data
    )


def test_cannot_purchase_more_than_competition_capacity(
    auth, client, club, future_competition, places
):
    """
    GIVEN an authenticated test client
    WHEN a POST request is sent to '/purchasePlaces' page
    with a number of places exceeding competition capacity
    THEN check that:
    1) A '403' status code is returned
    2) The response includes the message:
    'Invalid request: please enter a number of places
    under competition capacity'
    """
    auth.login(club)
    response = client.post(
        "/purchase_places",
        data=dict(
            club=club["name"],
            competition=future_competition["name"],
            places=str(int(future_competition["places"]) + places),
        ),
    )
    assert response.status_code == 403
    assert (
        b"Invalid request: please enter a number of places "
        b"under competition capacity"
        in response.data
    )


def test_cannot_purchase_more_than_twelve_places_in_a_row(
    auth, client, club, future_competition, affordable_places
):
    """
    GIVEN an authenticated test client
    WHEN a POST request is sent to '/purchasePlaces' page
    to purchase more than 12 places
    THEN check that:
    1) A '403' status code is returned
    2) The response includes the message:
    'Invalid request: maximum purchase limit of 12 places'
    """
    auth.login(club)
    response = client.post(
        "/purchase_places",
        data=dict(
            club=club["name"],
            competition=future_competition["name"],
            places=str(13 + affordable_places),
        ),
    )
    assert response.status_code == 403
    assert b"Invalid request: maximum purchase limit of 12 places"\
           in response.data


def test_cannot_purchase_more_than_twelve_places_per_competition(
    auth, client, pair_club_competition, places
):
    """
    GIVEN an authenticated test client
    WHEN a POST request is sent to '/purchasePlaces' page
    And more than 12 places have been bought for a competition
    THEN check that:
    1) A '403' status code is returned
    2) The response includes the message:
    'Invalid request: maximum purchase limit of 12 places per competition'
    """
    club = pair_club_competition["club"]
    competition = pair_club_competition["competition"]
    remaining_purchases = 12 - pair_club_competition["places_purchased"]

    auth.login(club)
    response = client.post(
        "/purchase_places",
        data=dict(
            club=club["name"],
            competition=competition["name"],
            places=remaining_purchases + places,
        ),
    )
    assert response.status_code == 403
    assert (
        b"Invalid request: maximum purchase limit of 12 places per competition"
        in response.data
    )


def test_can_purchase_for_future_competition(
    auth, client, club, future_competition, affordable_places
):
    """
    GIVEN an authenticated test client
    WHEN a POST request is sent to '/purchasePlaces' page
    for a competition that did not take place yet
    THEN check that a '200' status code is returned
    """
    auth.login(club)
    response = client.post(
        "/purchase_places",
        data=dict(
            club=club["name"],
            competition=future_competition["name"],
            places=affordable_places,
        ),
    )
    assert response.status_code == 200


def test_cannot_purchase_for_past_competition(
    auth, client, club, past_competition, places
):
    """
    GIVEN an authenticated test client
    WHEN a POST request is sent to '/purchasePlaces' page
    for a competition that already took place
    THEN check that a '403' status code is returned
    """
    auth.login(club)
    response = client.post(
        "/purchase_places",
        data=dict(
            club=club["name"],
            competition=past_competition["name"],
            places=places
        ),
    )
    assert response.status_code == 403


def test_access_points_board(client):
    """
    GIVEN a test client
    WHEN a GET request is sent to '/points_board' page
    THEN check that:
    1) A '200' status code is returned
    2) The response includes the message:
    'Points Board'
    3) The response includes the message:
    'GUDLFT Website'
    """

    response = client.get('/points_board')
    assert response.status_code == 200
    assert b"Points Board" in response.data
    assert b"GUDLFT Website" in response.data
