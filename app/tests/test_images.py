import requests
from http import HTTPStatus
from app.tests.test_users import fake, ENDPOINT, create_user_payload


def test_create_image():
    """TEST A ROUTE POST user/<user_id:int>/images/create"""
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

    # create an image inside the folder
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

    # delete test user
    delete_user_response = requests.delete(f"{ENDPOINT}/user/{user_id}/delete")
    assert (
        delete_user_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_user_response.content


def test_image_swap():
    """TEST A ROUTE GET user/<user_id:int>/images/swap"""
    # create a test user
    user_payload = create_user_payload()
    create_user_response = requests.post(f"{ENDPOINT}/user/create", json=user_payload)
    assert (
        create_user_response.status_code == HTTPStatus.CREATED
    ), create_user_response.content
    user_data = create_user_response.json()
    user_id = user_data["id"]

    # create a folder to create images inside
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

    # create first image inside the folder
    image_title_1 = fake.name()
    image_path_1 = fake.image_url()
    image_payload_1 = {
        "folder_id": folder_id,
        "title": image_title_1,
        "path": image_path_1,
    }
    create_image_response = requests.post(
        f"{ENDPOINT}/user/{user_id}/images/create", json=image_payload_1
    )
    assert (
        create_image_response.status_code == HTTPStatus.CREATED
    ), create_image_response.content
    image_data_1 = create_image_response.json()
    image_id_1 = image_data_1["image_id"]
    assert image_data_1["folder_id"] == folder_id

    # create second image inside the folder
    image_title_2 = fake.name()
    image_path_2 = fake.image_url()
    image_payload_2 = {
        "folder_id": folder_id,
        "title": image_title_2,
        "path": image_path_2,
    }
    create_image_response = requests.post(
        f"{ENDPOINT}/user/{user_id}/images/create", json=image_payload_2
    )
    assert (
        create_image_response.status_code == HTTPStatus.CREATED
    ), create_image_response.content
    image_data_2 = create_image_response.json()
    image_id_2 = image_data_2["image_id"]
    assert image_data_2["folder_id"] == folder_id

    # check first order of images in the folder
    order_image_1 = 0
    order_image_2 = 1
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    assert len(get_user_response.json()["folders"]) == 1
    user_folder = get_user_response.json()["folders"][0]
    assert user_folder["folder_id"] == folder_id
    assert user_folder["name"] == folder_name
    assert len(user_folder["images"]) == 2
    folder_image_1 = user_folder["images"][
        order_image_1
    ]  # here first image have index order_image_1
    assert folder_image_1["image_id"] == image_id_1
    assert folder_image_1["path"] == image_path_1
    assert folder_image_1["comments"] == []
    assert folder_image_1["user_id"] == user_id
    assert folder_image_1["title"] == image_title_1
    folder_image_2 = user_folder["images"][
        order_image_2
    ]  # here second image have index order_image_2
    assert folder_image_2["image_id"] == image_id_2
    assert folder_image_2["path"] == image_path_2
    assert folder_image_2["comments"] == []
    assert folder_image_2["user_id"] == user_id
    assert folder_image_2["title"] == image_title_2

    # swap images
    swap_payload = {
        "folder_id": folder_id,
        "first_image_id": image_id_1,
        "second_image_id": image_id_2,
    }
    swap_response = requests.get(
        f"{ENDPOINT}/user/{user_id}/images/swap", json=swap_payload
    )
    assert swap_response.status_code == HTTPStatus.NO_CONTENT, swap_response.content

    # check images change order
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    assert len(get_user_response.json()["folders"]) == 1
    user_folder = get_user_response.json()["folders"][0]
    assert user_folder["folder_id"] == folder_id
    assert user_folder["name"] == folder_name
    assert len(user_folder["images"]) == 2
    folder_image_1 = user_folder["images"][
        order_image_2
    ]  # but here first image must have index order_image_2
    assert folder_image_1["image_id"] == image_id_1
    assert folder_image_1["path"] == image_path_1
    assert folder_image_1["comments"] == []
    assert folder_image_1["user_id"] == user_id
    assert folder_image_1["title"] == image_title_1
    folder_image_2 = user_folder["images"][
        order_image_1
    ]  # and here second image must have index order_image_1
    assert folder_image_2["image_id"] == image_id_2
    assert folder_image_2["path"] == image_path_2
    assert folder_image_2["comments"] == []
    assert folder_image_2["user_id"] == user_id
    assert folder_image_2["title"] == image_title_2

    # delete test user
    delete_user_response = requests.delete(f"{ENDPOINT}/user/{user_id}/delete")
    assert (
        delete_user_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_user_response.content


def test_delete_image():
    """TEST A ROUTE DELETE user/<user_id:int>/images/delete"""
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

    # create an image inside the folder
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

    # delete the image
    delete_image_payload = {"folder_id": folder_id, "image_id": image_id}
    delete_image_response = requests.delete(
        f"{ENDPOINT}/user/{user_id}/images/delete", json=delete_image_payload
    )
    assert (
        delete_image_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_image_response.content

    # check there's no images in folder
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    get_user_data = get_user_response.json()
    assert len(get_user_data["folders"]) == 1
    assert get_user_data["folders"][0]["folder_id"] == folder_id
    assert get_user_data["folders"][0]["name"] == folder_name
    assert get_user_data["folders"][0]["folder_users"] == {str(user_id): "owner"}
    assert get_user_data["folders"][0]["images"] == []

    # delete test user
    delete_user_response = requests.delete(f"{ENDPOINT}/user/{user_id}/delete")
    assert (
        delete_user_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_user_response.content
