from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from db_models.mongo_setup import global_init
from db_models.models.post_model import Posts
from db_models.models.user_model import UserModel
import face_recognition
import pickle
import os
import globals
import base64


app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

global_init()

for user in UserModel.objects:
    globals.add_to_embeddings(username=user.user_name, encoding=pickle.loads(user.encoding))


@app.post("/register/")
def register(
        file: UploadFile = File(...),
        user_name: str = Form(...),
        email: str = Form(...),
        description: str = Form(...),
        full_name: str = Form(...)
):
    try:
        UserModel.objects.get(user_name=user_name)
        return False
    except UserModel.DoesNotExist:
        user_model_obj = UserModel()
        file_name = file.filename
        with open(file_name, 'wb') as f:
            f.write(file.file.read())
        face_image = face_recognition.load_image_file(file_name)
        face_encoding = face_recognition.face_encodings(face_image)[0]
        binary_encoding = pickle.dumps(face_encoding)
        user_model_obj.user_name = user_name
        user_model_obj.full_name = full_name
        user_model_obj.encoding = binary_encoding
        user_model_obj.email = email
        user_model_obj.description = description
        with open(file_name, 'rb') as fd:
            user_model_obj.img.put(fd)
        os.remove(file_name)
        user_model_obj.save()
        return True


@app.post("/post/")
def post(location: str, file: UploadFile = File(...)):
    post_model_obj = Posts()
    file_name = file.filename
    with open(file_name, 'wb') as f:
        f.write(file.file.read())
    embeddings = []
    for dic in globals.embeddings:
        embeddings.append(dic["encoding"])
    face_image = face_recognition.load_image_file(file_name)
    uname = None
    try:
        print(uname)
        face_encoding = face_recognition.face_encodings(face_image)[0]
        face_distances = face_recognition.face_distance(embeddings, face_encoding)
        for i, face_distance in enumerate(face_distances):
            if face_distance < 0.6:
                user_dic = globals.embeddings[i]
                uname = user_dic["name"]
    except IndexError:
        return None
    if uname is None:
        os.remove(file_name)
        return None
    else:
        user_obj = UserModel.objects.get(user_name=uname)
        post_model_obj.user = user_obj
        with open(file_name, 'rb') as fd:
            post_model_obj.post = fd.read()
        post_model_obj.location = location
        user_obj.points = user_obj.points + 10
        user_obj.save()
        post_model_obj.save()
        os.remove(file_name)
        return uname


@app.get("/")
def fetch(skip: int = 0):
    skip = skip * 10
    limit = skip + 10
    posts = []
    for post_obj in Posts.objects[skip:limit].order_by('-date'):
        post_dict = dict()
        user_obj = post_obj.user
        post_dict["user_name"] = user_obj.user_name
        post_dict["full_name"] = user_obj.full_name
        post_dict["date"] = post_obj.date
        post_dict["location"] = post_obj.location
        post_dict["img"] = base64.b64encode(post_obj.post)
        posts.append(post_dict)
    return posts


@app.get("/u/")
def fetch(user_name: str):
    try:
        UserModel.objects.get(user_name=user_name)
        posts = []
        user_obj = UserModel.objects.get(user_name=user_name)
        post_objects = Posts.objects(user=user_obj)
        user_dict = dict()
        for obj in post_objects:
            post_dict = dict()
            post_dict["date"] = obj.date
            post_dict["img"] = base64.b64encode(obj.post)
            post_dict["location"] = obj.location
            posts.append(post_dict)
        user_dict["user_name"] = user_obj.user_name
        user_dict["full_name"] = user_obj.full_name
        user_dict["profile_pic"] = base64.b64encode(user_obj.img.read())
        user_dict["description"] = user_obj.description
        user_dict["points"] = user_obj.points
        user_dict["posts"] = posts
        return user_dict

    except UserModel.DoesNotExist:
        return False
