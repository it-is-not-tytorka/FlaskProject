import requests
from http import HTTPStatus
from faker import Faker
from icecream import ic


fake = Faker()

ENDPOINT = "http://127.0.0.1:5000"

def create_user_payload():
    random_first_name = fake.first_name()
    random_last_name = fake.last_name()
    random_phone_number = fake.numerify("+7##########")
    random_email = fake.email()
    return {
        "first_name": random_first_name,
        "last_name": random_last_name,
        "phone": random_phone_number,
        "email": random_email
    }


def test_create_image():
    """TEST A ROUTE POST user/<user_id:int>/images/create"""
    # create a test user
    user_payload = create_user_payload()
    create_user_response = requests.post(f"{ENDPOINT}/user/create", json=user_payload)
    assert create_user_response.status_code == HTTPStatus.CREATED
    user_data = create_user_response.json()
    user_id = user_data["id"]

    # create a folder to create an image inside
    folder_name = fake.name()
    folder_payload = {
        "folder_name": folder_name
    }
    create_folder_response = requests.post(f"{ENDPOINT}/user/{user_id}/folders/create", json=folder_payload)
    assert create_folder_response.status_code == HTTPStatus.CREATED
    folder_id = create_folder_response.json()["folder_id"]

    # check that user has a created folder
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK
    get_user_data = get_user_response.json()
    assert len(get_user_data["folders"]) == 1
    assert get_user_data["folders"][0]["folder_id"] == folder_id
    assert get_user_data["folders"][0]["name"] == folder_name
    assert get_user_data["folders"][0]["folder_users"] == {str(user_id): "owner"}
    assert get_user_data["folders"][0]["images"] == []

    # create an image inside the folder
    image_title = fake.name()
    image_path = fake.image_url()
    image_payload = {
        "folder_id": folder_id,
        "title": image_title,
        "path": image_path
    }
    create_image_response = requests.post(f"{ENDPOINT}/user/{user_id}/images/create", json=image_payload)
    assert create_image_response.status_code == HTTPStatus.CREATED
    image_data = create_image_response.json()
    image_id = image_data["image_id"]
    assert image_data["folder_id"] == folder_id

    # check the image in the folder
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK
    assert len(get_user_response.json()["folders"]) == 1
    user_folder = get_user_response.json()["folders"][0]
    assert user_folder["folder_id"] == folder_id
    assert user_folder["name"] == folder_name
    assert len(user_folder["images"]) == 1
    folder_images = user_folder["images"][0]
    assert folder_images["image_id"] == image_id
    assert folder_images["path"] == image_path
    assert folder_images["comments"] == []
    assert folder_images["user_id"] == user_id
    assert folder_images["title"] == image_title


    # delete test user
    del_user_response = requests.delete(f"{ENDPOINT}/user/{user_id}/delete")
    assert del_user_response.status_code == HTTPStatus.NO_CONTENT
