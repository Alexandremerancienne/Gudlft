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
    response = client.post("/showSummary", data=dict(email=club["email"]))
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
    response = client.post("/showSummary", data=dict(email=club["email"]))
    assert response.status_code == 403
    assert b'Unknown user: please enter a valid email' in response.data


def test_logout_works(client):
    """
    GIVEN a test client
    WHEN a POST request is sent to '/logout' page
    THEN check that headers will have 'localhost' as Location header
    """
    response = client.get("/logout")
    assert response.status_code == 302
    assert "http://localhost/" == response.headers["Location"]


def test_select_a_competition_returns_competition_details(auth, client, club, competition):
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

