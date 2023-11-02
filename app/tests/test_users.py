from http import HTTPStatus
from faker import Faker
import requests
from icecream import ic

fake = Faker()

ENDPOINT = "http://127.0.0.1:5000"


def create_user_payload():
    random_first_name = fake.first_name()
    last_name = fake.last_name()
    random_phone_number = fake.numerify("+7##########")
    random_email = fake.email()
    return {
        "first_name": random_first_name,
        "last_name": last_name,
        "phone": random_phone_number,
        "email": random_email
    }

def test_user_create():
    """TEST OF A ROUTE user/create WITH RIGHT DATA

    Create user with right payload and check that user data
    and response of a route /user/<user_id:int>/info data are both right.
    In the end of the test we must delete created user to not remember him during tests.
    """
    payload = create_user_payload()

    create_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    assert create_response.status_code == HTTPStatus.CREATED, "Wrong payload data"

    user_data = create_response.json()
    # check user data and payload are both the same
    assert user_data["first_name"] == payload["first_name"]
    assert user_data["last_name"] == payload["last_name"]
    assert user_data["phone"] == payload["phone"]
    assert user_data["email"] == payload["email"]

    # check route /user/<int:user_id>/info
    user_id = user_data["id"]
    get_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_response.status_code == HTTPStatus.OK

    # check response and payload are the same
    got_user_info = get_response.json()
    assert got_user_info["first_name"] == payload["first_name"]
    assert got_user_info["last_name"] == payload["last_name"]
    assert got_user_info["phone"] == payload["phone"]
    assert got_user_info["email"] == payload["email"]

    # deleting created user
    delete_response = requests.delete(f"{ENDPOINT}/user/{user_id}/delete")
    assert delete_response.status_code == HTTPStatus.NO_CONTENT


def test_user_crete_with_wrong_data():
    """TEST OF A ROUTE /user/create WITH WRONG DATA

    Check creating user with invalid phone number or email
    """
    # create payload and spoilt email
    payload = create_user_payload()
    payload["email"] = payload["email"].replace("@", "")

    create_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    assert create_response.status_code == HTTPStatus.BAD_REQUEST

    # create payload and spoilt phone number
    payload = create_user_payload()
    payload["phone"] = "000" + payload["phone"]

    create_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    assert create_response.status_code == HTTPStatus.BAD_REQUEST


def test_get_uset_stats():
    # todo: release this test
    ...