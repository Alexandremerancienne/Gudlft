from ..conftest import load_future_competition

load_future_competition()


def test_logout_then_login(auth, client):
    """
    GIVEN a test client
    WHEN:
    1) A POST request is sent to '/logout' page
    2) A GET request is sent to the '/' page
    THEN check that:
    1) A '200' status code is returned
    2) The response includes the message:
    'Welcome to the GUDLIFT Registration Portal!'
    """

    auth.logout()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the GUDLFT Registration Portal!" in response.data


def test_login_then_view_points_board(auth, club, client):
    """
    GIVEN a test client
    WHEN:
    1) A GET request is sent to '/' page
    2) A GET request is sent to '/points_board' page
    THEN check that:
    1) A '200' status code is returned
    2) The response includes the message:
    'Points Board'
    3) The response includes the message:
    'GUDLFT Website'
    """

    auth.login(club)
    response = client.get('/points_board')
    assert response.status_code == 200
    assert b"Points Board" in response.data
    assert b"GUDLFT Website" in response.data


def test_view_points_board_then_login(client):
    """
    GIVEN a test client
    WHEN:
    1) A GET request is sent to '/points_board' page
    2) A GET request is sent to the '/' page
    THEN check that:
    1) A '200' status code is returned
    2) The response includes the message:
    'Points Board'
    3) The response includes the message:
    'GUDLFT Website'
    """

    client.get('/points_board')
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the GUDLFT Registration Portal!" in response.data





