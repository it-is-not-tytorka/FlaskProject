import requests
from http import HTTPStatus
from datetime import date
from app.tests.test_users import fake, ENDPOINT, create_user_payload


def test_add_comment():
    """TEST A ROUTE POST user/<user_id:int>/comments/add"""
    # create a test user
    user_payload = create_user_payload()
    create_user_response = requests.post(f"{ENDPOINT}/user/create", json=user_payload)
    assert (
        create_user_response.status_code == HTTPStatus.CREATED
    ), create_user_response.content
    user_data = create_user_response.json()
    user_id = user_data["id"]

    # create a folder to create an image inside
    folder_name = fake.name()
    folder_payload = {"folder_name": folder_name}
    create_folder_response = requests.post(
        f"{ENDPOINT}/user/{user_id}/folders/create", json=folder_payload
    )
    assert (
        create_folder_response.status_code == HTTPStatus.CREATED
    ), create_folder_response.content
    folder_id = create_folder_response.json()["folder_id"]

    # check that user has a created folder
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    get_user_data = get_user_response.json()
    assert len(get_user_data["folders"]) == 1
    assert get_user_data["folders"][0]["folder_id"] == folder_id
    assert get_user_data["folders"][0]["name"] == folder_name
    assert get_user_data["folders"][0]["folder_users"] == {str(user_id): "owner"}
    assert get_user_data["folders"][0]["images"] == []

    # create an image inside the folder to add comment
    image_title = fake.name()
    image_path = fake.image_url()
    image_payload = {"folder_id": folder_id, "title": image_title, "path": image_path}
    create_image_response = requests.post(
        f"{ENDPOINT}/user/{user_id}/images/create", json=image_payload
    )
    assert (
        create_image_response.status_code == HTTPStatus.CREATED
    ), create_image_response.content
    image_data = create_image_response.json()
    image_id = image_data["image_id"]
    assert image_data["folder_id"] == folder_id

    # check the image in the folder
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    assert len(get_user_response.json()["folders"]) == 1
    user_folder = get_user_response.json()["folders"][0]
    assert user_folder["folder_id"] == folder_id
    assert user_folder["name"] == folder_name
    assert len(user_folder["images"]) == 1
    folder_image = user_folder["images"][0]
    assert folder_image["image_id"] == image_id
    assert folder_image["path"] == image_path
    assert folder_image["comments"] == []
    assert folder_image["user_id"] == user_id
    assert folder_image["title"] == image_title

    # add comment
    comment_text = fake.sentence()
    add_comment_payload = {
        "folder_id": folder_id,
        "image_id": image_id,
        "comment_text": comment_text,
    }
    add_comment_response = requests.post(
        f"{ENDPOINT}/user/{user_id}/comments/add", json=add_comment_payload
    )
    assert (
        add_comment_response.status_code == HTTPStatus.CREATED
    ), add_comment_response.content
    comment_data = add_comment_response.json()
    assert comment_data["folder_id"] == folder_id
    assert comment_data["image_id"] == image_id
    comment_id = comment_data["comment_id"]

    # check the user has a comment
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    assert len(get_user_response.json()["folders"]) == 1
    user_folder = get_user_response.json()["folders"][0]
    assert user_folder["folder_id"] == folder_id
    assert user_folder["name"] == folder_name
    assert len(user_folder["images"]) == 1
    folder_image = user_folder["images"][0]
    assert folder_image["image_id"] == image_id
    assert folder_image["path"] == image_path
    assert folder_image["user_id"] == user_id
    assert folder_image["title"] == image_title
    assert len(folder_image["comments"]) == 1
    image_comment = folder_image["comments"][0]
    assert image_comment["comment_id"] == comment_id
    assert image_comment["comment_text"] == comment_text
    assert image_comment["user_id"] == user_id
    assert image_comment["date"] == str(date.today())

    # delete test user
    delete_user_response = requests.delete(f"{ENDPOINT}/user/{user_id}/delete")
    assert (
        delete_user_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_user_response.content


def test_delete_comment():
    """TEST A ROUTE DELETE user/<user_id:int>/comments/delete"""
    # create a test user
    user_payload = create_user_payload()
    create_user_response = requests.post(f"{ENDPOINT}/user/create", json=user_payload)
    assert (
        create_user_response.status_code == HTTPStatus.CREATED
    ), create_user_response.content
    user_data = create_user_response.json()
    user_id = user_data["id"]

    # create a folder to create an image inside
    folder_name = fake.name()
    folder_payload = {"folder_name": folder_name}
    create_folder_response = requests.post(
        f"{ENDPOINT}/user/{user_id}/folders/create", json=folder_payload
    )
    assert (
        create_folder_response.status_code == HTTPStatus.CREATED
    ), create_folder_response.content
    folder_id = create_folder_response.json()["folder_id"]

    # check that user has a created folder
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    get_user_data = get_user_response.json()
    assert len(get_user_data["folders"]) == 1
    assert get_user_data["folders"][0]["folder_id"] == folder_id
    assert get_user_data["folders"][0]["name"] == folder_name
    assert get_user_data["folders"][0]["folder_users"] == {str(user_id): "owner"}
    assert get_user_data["folders"][0]["images"] == []

    # create an image inside the folder to add comment
    image_title = fake.name()
    image_path = fake.image_url()
    image_payload = {"folder_id": folder_id, "title": image_title, "path": image_path}
    create_image_response = requests.post(
        f"{ENDPOINT}/user/{user_id}/images/create", json=image_payload
    )
    assert (
        create_image_response.status_code == HTTPStatus.CREATED
    ), create_image_response.content
    image_data = create_image_response.json()
    image_id = image_data["image_id"]
    assert image_data["folder_id"] == folder_id

    # check the image in the folder
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    assert len(get_user_response.json()["folders"]) == 1
    user_folder = get_user_response.json()["folders"][0]
    assert user_folder["folder_id"] == folder_id
    assert user_folder["name"] == folder_name
    assert len(user_folder["images"]) == 1
    folder_image = user_folder["images"][0]
    assert folder_image["image_id"] == image_id
    assert folder_image["path"] == image_path
    assert folder_image["comments"] == []
    assert folder_image["user_id"] == user_id
    assert folder_image["title"] == image_title

    # add comment
    comment_text = fake.sentence()
    add_comment_payload = {
        "folder_id": folder_id,
        "image_id": image_id,
        "comment_text": comment_text,
    }
    add_comment_response = requests.post(
        f"{ENDPOINT}/user/{user_id}/comments/add", json=add_comment_payload
    )
    assert (
        add_comment_response.status_code == HTTPStatus.CREATED
    ), add_comment_response.content
    comment_data = add_comment_response.json()
    assert comment_data["folder_id"] == folder_id
    assert comment_data["image_id"] == image_id
    comment_id = comment_data["comment_id"]

    # check the user has a comment
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    assert len(get_user_response.json()["folders"]) == 1
    user_folder = get_user_response.json()["folders"][0]
    assert user_folder["folder_id"] == folder_id
    assert user_folder["name"] == folder_name
    assert len(user_folder["images"]) == 1
    folder_image = user_folder["images"][0]
    assert folder_image["image_id"] == image_id
    assert folder_image["path"] == image_path
    assert folder_image["user_id"] == user_id
    assert folder_image["title"] == image_title
    assert len(folder_image["comments"]) == 1
    image_comment = folder_image["comments"][0]
    assert image_comment["comment_id"] == comment_id
    assert image_comment["comment_text"] == comment_text
    assert image_comment["user_id"] == user_id
    assert image_comment["date"] == str(date.today())

    # delete comment
    delete_comment_payload = {
        "folder_id": folder_id,
        "image_id": image_id,
        "comment_id": comment_id,
    }
    delete_comment_response = requests.delete(
        f"{ENDPOINT}/user/{user_id}/comments/delete", json=delete_comment_payload
    )
    assert (
        delete_comment_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_comment_response.content

    # check there's no comment anymore
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    assert len(get_user_response.json()["folders"]) == 1
    user_folder = get_user_response.json()["folders"][0]
    assert user_folder["folder_id"] == folder_id
    assert user_folder["name"] == folder_name
    assert len(user_folder["images"]) == 1
    folder_image = user_folder["images"][0]
    assert folder_image["image_id"] == image_id
    assert folder_image["path"] == image_path
    assert folder_image["user_id"] == user_id
    assert folder_image["title"] == image_title
    assert len(folder_image["comments"]) == 0

    # delete test user
    delete_user_response = requests.delete(f"{ENDPOINT}/user/{user_id}/delete")
    assert (
        delete_user_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_user_response.content
