from fastapi import FastAPI
import random

app=FastAPI()

@app.get("/test1")
def test1():
    return {"message":"Мой первый эндпоинт"}

@app.get("/random1")
def random1():
    return {"random_num":random.randint(0, 10)}