from http import HTTPStatus
from faker import Faker
import requests
from icecream import ic

fake = Faker()

ENDPOINT = "http://127.0.0.1:5000"

def test_user_create():
    """TEST OF A ROUTE user/create

    """
    ENDPOINT = "http://127.0.0.1:5000"
    random_first_name = fake.first_name()
    last_name = fake.last_name()
    random_phone_number = fake.numerify("+7##########")
    random_email = fake.email()
    payload = {
        "first_name": random_first_name,
        "last_name": last_name,
        "phone": random_phone_number,
        "email": random_email
    }
    create_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    assert create_response.status_code == HTTPStatus.CREATED, "The user wasn't created"

    user_data = create_response.json()
    assert user_data["first_name"] == payload["first_name"]
    assert user_data["last_name"] == payload["last_name"]
    assert user_data["phone"] == payload["phone"]
    assert user_data["email"] == payload["email"]

    user_id = user_data["id"]
    get_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_response.status_code == HTTPStatus.OK

    got_user_info = get_response.json()
    assert got_user_info["first_name"] == payload["first_name"]
    assert got_user_info["last_name"] == payload["last_name"]
    assert got_user_info["phone"] == payload["phone"]
    assert got_user_info["email"] == payload["email"]


def test_user_crete_with_wrong_data():
    random_first_name = fake.first_name()
    random_last_name = fake.last_name()
    random_phone_number = fake.numerify("+7##########")
    random_email = fake.email()
    wrong_email = random_email.replace("@", "")
    payload = {
        "first_name": random_first_name,
        "last_name": random_last_name,
        "phone": random_phone_number,
        "email": wrong_email
    }

    create_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    assert create_response.status_code == HTTPStatus.BAD_REQUEST

    wrong_phone_number = "000" + random_phone_number
    payload["email"] = random_email
    payload["phone"] = wrong_phone_number
    create_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    ic(payload)
    assert create_response.status_code == HTTPStatus.BAD_REQUEST
