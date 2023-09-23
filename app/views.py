from app import app, USERS, models
from flask import request, Response
import json
import http


@app.post("/user/create")
def user_create():
    data = request.get_json()
    first_name = data["first_name"]
    last_name = data["last_name"]
    phone = data["phone"]
    email = data["email"]
    id = len(USERS)
    # check if phone number and email are valid
    if models.User.is_valid_phone(phone_numb=phone) and models.User.is_valid_email(
        email=email
    ):
        user = models.User(first_name, last_name, phone, email, id)
        user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "email": user.email,
            "id": user.id,
            "folders": user.folders
        }
        USERS.append(user)
        return Response(
            json.dumps(user_data),
            status=http.HTTPStatus.OK,
            mimetype="application/json",
        )

    else:
        return Response(status=http.HTTPStatus.BAD_REQUEST)


@app.get("/user/<int:user_id>")
def get_user_inf(user_id):
    if models.User.check_user(user_id):
        response = USERS[user_id].get_inf()
        return Response(
            json.dumps(response), status=http.HTTPStatus.OK, mimetype="application/json"
        )
    return Response(status=http.HTTPStatus.BAD_REQUEST)


@app.post("/user/<int:user_id>/folder/create")
def create_folder(user_id):
    data = request.get_json()
    folder_name = data["folder_name"]
    if models.User.check_user(user_id=user_id):
        user = USERS[user_id]
        folder_id = len(user.folders)
        folder = models.Folder(id=folder_id, name = folder_name)
        folder.create_folder(user=user)
        return Response(status=http.HTTPStatus.OK)
    return Response(http.HTTPStatus.BAD_REQUEST) 

@app.post("/user/<int:user_id>/folder/<int:folder_id>/append")
def append_photo_to_the_folder(user_id, folder_id):
    data = request.get_json()
    path = data["path"]
    if models.User.check_user(user_id=user_id) and models.User.check_folder(user=USERS[user_id], folder_id=folder_id):
        user = USERS[user_id] 
        photo_id = len(user.folders[folder_id]["images"])
        photo = models.Photo(id=photo_id, path=path)
        user.folders[folder_id]["images"][photo_id] = photo.data
        return Response(status=http.HTTPStatus.OK)
    return Response(status=http.HTTPStatus.BAD_REQUEST)
