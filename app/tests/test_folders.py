from http import HTTPStatus
import requests
from app.tests.test_users import fake, ENDPOINT, create_user_payload
import pytest


def test_create_folder():
    """TEST A ROUTE POST user/<user_id:int>/folders/create"""
    # create a test user
    payload = create_user_payload()
    create_user_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    assert (
        create_user_response.status_code == HTTPStatus.CREATED
    ), create_user_response.content
    user_data = create_user_response.json()
    user_id = user_data["id"]

    # create a folder
    folder_name = fake.name()
    create_folder_payload = {"folder_name": folder_name}
    create_folder_response = requests.post(
        f"{ENDPOINT}/user/{user_id}/folders/create", json=create_folder_payload
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

    # delete test user
    delete_user_response = requests.delete(f"{ENDPOINT}/user/{user_id}/delete")
    assert (
        delete_user_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_user_response.content


def test_swap_folders():
    """TEST A ROUTE GET user/<user_id:int>/folders/swap"""
    # create a test user
    payload = create_user_payload()
    create_user_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    assert (
        create_user_response.status_code == HTTPStatus.CREATED
    ), create_user_response.content
    user_id = create_user_response.json()["id"]

    # create two folders
    payload_first_folder = {"folder_name": fake.name()}
    payload_second_folder = {"folder_name": fake.name()}
    create_first_folder_response = requests.post(
        f"{ENDPOINT}/user/{user_id}/folders/create", json=payload_first_folder
    )
    assert (
        create_first_folder_response.status_code == HTTPStatus.CREATED
    ), create_first_folder_response.content
    first_folder_id = create_first_folder_response.json()["folder_id"]
    create_second_folder_response = requests.post(
        f"{ENDPOINT}/user/{user_id}/folders/create", json=payload_second_folder
    )
    assert (
        create_second_folder_response.status_code == HTTPStatus.CREATED
    ), create_second_folder_response.content
    second_folder_id = create_second_folder_response.json()["folder_id"]

    # find out old order of folders
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    user_data = get_user_response.json()
    old_first_folder_place = 0
    old_second_folder_place = 1
    assert user_data["folders"][old_first_folder_place]["folder_id"] == first_folder_id
    assert (
        user_data["folders"][old_second_folder_place]["folder_id"] == second_folder_id
    )

    # swap these folders
    swap_payload = {
        "first_folder_id": first_folder_id,
        "second_folder_id": second_folder_id,
    }
    swap_response = requests.get(
        f"{ENDPOINT}/user/{user_id}/folders/swap", json=swap_payload
    )
    assert swap_response.status_code == HTTPStatus.NO_CONTENT, swap_response.content

    # get user info and check the folders changed places
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    user_data = get_user_response.json()
    assert user_data["folders"][old_first_folder_place]["folder_id"] == second_folder_id
    assert user_data["folders"][old_second_folder_place]["folder_id"] == first_folder_id

    delete_user_response = requests.delete(f"{ENDPOINT}/user/{user_id}/delete")
    assert (
        delete_user_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_user_response.content


def test_delete_folder():
    """TEST A ROUTE DELETE user/<user_id:int>/folders/delete"""
    # create a test user
    payload = create_user_payload()
    create_user_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    assert (
        create_user_response.status_code == HTTPStatus.CREATED
    ), create_user_response.content
    user_id = create_user_response.json()["id"]

    # create a folder
    create_folder_payload = {"folder_name": fake.name()}
    create_folder_response = requests.post(
        f"{ENDPOINT}/user/{user_id}/folders/create", json=create_folder_payload
    )
    assert (
        create_folder_response.status_code == HTTPStatus.CREATED
    ), create_folder_response.content
    folder_id = create_folder_response.json()["folder_id"]

    # delete folder
    delete_folder_payload = {"folder_id": folder_id}
    delete_folder_response = requests.delete(
        f"{ENDPOINT}/user/{user_id}/folders/delete", json=delete_folder_payload
    )
    assert (
        delete_folder_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_folder_response.content

    # check user doesn't have the folder
    get_user_response = requests.get(f"{ENDPOINT}/user/{user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    user_data = get_user_response.json()
    assert user_data["folders"] == []

    # delete a test user
    delete_user_response = requests.delete(f"{ENDPOINT}/user/{user_id}/delete")
    assert (
        delete_user_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_user_response.content


@pytest.mark.parametrize("access_edit", [True, False])
def test_share_folder(access_edit):
    """TEST A ROUTE GET user/<user_id:int>/folders/share"""
    # create a test owner user
    payload = create_user_payload()
    create_user_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    assert (
        create_user_response.status_code == HTTPStatus.CREATED
    ), create_user_response.content
    owner_user_id = create_user_response.json()["id"]

    # create a test receiver user
    payload = create_user_payload()
    create_user_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    assert (
        create_user_response.status_code == HTTPStatus.CREATED
    ), create_user_response.content
    receiver_user_id = create_user_response.json()["id"]

    # create a folder
    folder_name = fake.name()
    create_folder_payload = {"folder_name": folder_name}
    create_folder_response = requests.post(
        f"{ENDPOINT}/user/{owner_user_id}/folders/create", json=create_folder_payload
    )
    assert (
        create_folder_response.status_code == HTTPStatus.CREATED
    ), create_folder_response.content
    folder_id = create_folder_response.json()["folder_id"]

    # share folder from owner to receiver
    access_edit = True
    share_folder_payload = {
        "user_to_receive_id": receiver_user_id,
        "shared_folder_id": folder_id,
        "access_edit": access_edit,
    }
    share_folder_response = requests.get(
        f"{ENDPOINT}/user/{owner_user_id}/folders/share", json=share_folder_payload
    )
    assert (
        share_folder_response.status_code == HTTPStatus.NO_CONTENT
    ), share_folder_response.content

    # check receive user got the folder
    get_receive_user_response = requests.get(f"{ENDPOINT}/user/{owner_user_id}/info")
    assert (
        get_receive_user_response.status_code == HTTPStatus.OK
    ), get_receive_user_response.content
    receiver_user_folders = get_receive_user_response.json()["folders"]
    assert len(receiver_user_folders) == 1
    assert receiver_user_folders[0]["folder_id"] == folder_id
    assert receiver_user_folders[0]["name"] == folder_name
    assert receiver_user_folders[0]["folder_users"] == {
        str(owner_user_id): "owner",
        str(receiver_user_id): "moderator" if access_edit else "reader",
    }
    assert receiver_user_folders[0]["images"] == []

    # delete test users
    delete_user_response = requests.delete(f"{ENDPOINT}/user/{owner_user_id}/delete")
    assert (
        delete_user_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_user_response.content
    delete_user_response = requests.delete(f"{ENDPOINT}/user/{receiver_user_id}/delete")
    assert (
        delete_user_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_user_response.content


@pytest.mark.parametrize("access_edit", [True, False])
def test_unshare_folder(access_edit):
    """TEST A ROUTE GET user/<user_id:int>/folders/share"""
    # create a test owner user
    payload = create_user_payload()
    create_user_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    assert (
        create_user_response.status_code == HTTPStatus.CREATED
    ), create_user_response.content
    owner_user_id = create_user_response.json()["id"]

    # create a test receiver user
    payload = create_user_payload()
    create_user_response = requests.post(f"{ENDPOINT}/user/create", json=payload)
    assert (
        create_user_response.status_code == HTTPStatus.CREATED
    ), create_user_response.content
    receiver_user_id = create_user_response.json()["id"]

    # create a folder
    folder_name = fake.name()
    create_folder_payload = {"folder_name": folder_name}
    create_folder_response = requests.post(
        f"{ENDPOINT}/user/{owner_user_id}/folders/create", json=create_folder_payload
    )
    assert (
        create_folder_response.status_code == HTTPStatus.CREATED
    ), create_folder_response.content
    folder_id = create_folder_response.json()["folder_id"]

    # share folder from owner to receiver
    share_folder_payload = {
        "user_to_receive_id": receiver_user_id,
        "shared_folder_id": folder_id,
        "access_edit": access_edit,
    }
    share_folder_response = requests.get(
        f"{ENDPOINT}/user/{owner_user_id}/folders/share", json=share_folder_payload
    )
    assert (
        share_folder_response.status_code == HTTPStatus.NO_CONTENT
    ), share_folder_response.content

    # check receive user got the folder
    get_receive_user_response = requests.get(f"{ENDPOINT}/user/{owner_user_id}/info")
    assert (
        get_receive_user_response.status_code == HTTPStatus.OK
    ), get_receive_user_response.content
    receiver_user_folders = get_receive_user_response.json()["folders"]
    assert len(receiver_user_folders) == 1
    assert receiver_user_folders[0]["folder_id"] == folder_id
    assert receiver_user_folders[0]["name"] == folder_name
    assert receiver_user_folders[0]["folder_users"] == {
        str(owner_user_id): "owner",
        str(receiver_user_id): "moderator" if access_edit else "reader",
    }
    assert receiver_user_folders[0]["images"] == []

    # unshare folder
    unshare_payload = {"user_to_unshare_id": receiver_user_id, "folder_id": folder_id}
    unshare_response = requests.get(
        f"{ENDPOINT}/user/{owner_user_id}/folders/unshare", json=unshare_payload
    )
    assert (
        unshare_response.status_code == HTTPStatus.NO_CONTENT
    ), unshare_response.content

    # check receiver user doesn't have the folder
    get_user_response = requests.get(f"{ENDPOINT}/user/{receiver_user_id}/info")
    assert get_user_response.status_code == HTTPStatus.OK, get_user_response.content
    user_folders = get_user_response.json()["folders"]
    assert user_folders == []

    # delete test users
    delete_user_response = requests.delete(f"{ENDPOINT}/user/{owner_user_id}/delete")
    assert (
        delete_user_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_user_response.content
    delete_user_response = requests.delete(f"{ENDPOINT}/user/{receiver_user_id}/delete")
    assert (
        delete_user_response.status_code == HTTPStatus.NO_CONTENT
    ), delete_user_response.content
