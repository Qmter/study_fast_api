import json
import pytest



@pytest.mark.parametrize(
        'username, password, expected_status, expected_username',
        [
            ('yara', 'yara', 200, 'yara'),
            ('iva', 'iva', 200, 'iva'),
            (1, 'yara', 422, None),
            (None, 'iva', 422, None)

        ]
    )
@pytest.mark.anyio
async def test_register(async_client, username, password, expected_status, expected_username):
    response = await async_client.post('/register', json={'username': username, 'password': password})

    assert response.status_code == expected_status


    if expected_status == 200:
            assert response.json() == {"username": expected_username}
    elif expected_status == 422:
        data = response.json()
        assert data["detail"][0]["type"] == "string_type"
        assert data["detail"][0]["loc"] == ["body", "username"]
        assert data["detail"][0]["msg"] == "Input should be a valid string"
        assert data["detail"][0]["input"] == username
        assert data["body"] == {"username": username, "password": password}




@pytest.mark.parametrize(
        'username, password, expected_status, expected_username',
        [
            ('yara', 'yara', 200, 'yara, Welcome!'),
            ('iva', 'iva', 200, 'iva, Welcome!'),
            (1, 'yara', 422, None),
            (None, 'iva', 422, None),
            ('pasha', 'pasha', 404, None),
            ('yara', 'yar', 401, None)
        ]
    )
@pytest.mark.anyio
async def test_login(async_client, username, password, expected_status, expected_username):
    response = await async_client.post('/login', json={'username': username, 'password': password})

    assert response.status_code == expected_status


    if expected_status == 200:
            assert response.json() == {'success login': f'{username}, Welcome!'}

    elif expected_status == 422:
        data = response.json()
        assert data["detail"][0]["type"] == "string_type"
        assert data["detail"][0]["loc"] == ["body", "username"]
        assert data["detail"][0]["msg"] == "Input should be a valid string"
        assert data["detail"][0]["input"] == username
        assert data["body"] == {"username": username, "password": password}

    elif expected_status == 404:
         assert response.json() == {
              "status_code": 404,
              "detail": "User Not Found",
              "message": "Try to change username"
              }
    elif expected_status == 401:
         assert response.json() == {
              "status_code": 401,
              "detail": "You are not authorized",
              "message": "Invalid password"
              }
