from fastapi import FastAPI, Query, Path
from enum import Enum
import random, math

app=FastAPI()

@app.get("/about")
def about():
    return {"Full Name":"Shabalin Egor Konstantinovich", 
    "GroupID":"T-333901-IST", 
    "Course Number":"III", 
    "University Name":"NTI UrFU", 
    "GitHub Page":"https://github.com/nmadnorangen"}

@app.get("/rnd")
def rnd(a:int=Query(default=1, ge=1, le=100), b:int=Query(default=100, ge=1, le=100)):
    if a > b:
        return{"error":"start is greater than finish!"}
    return {"number":random.randint(a, b)}

@app.post("/t_square")
def t_square(a:int=Query(ge=1), b:int=Query(ge=1), c:int=Query(ge=1)):
    if (a+b<c or a+c<b or b+c<a):
        return{"error":"triangle doesn't exist!"}
    P=a+b+c
    p=P/2
    S=math.sqrt(p*(p-a)*(p-b)*(p-c))
    
    return{"perimeter":P, "square":S}

class Temperatures(str, Enum):
    celsius="celsius"
    fahrenheit="fahrenheit"

@app.get("/convert/{from_unit}/{to_unit}/{value}")
def convert(from_unit:Temperatures, to_unit:Temperatures, value:float):
    if from_unit == to_unit:
        result = value
    elif from_unit == Temperatures.celsius and to_unit == Temperatures.fahrenheit:
        result = (value * 1.8) + 32
    elif from_unit == Temperatures.fahrenheit and to_unit == Temperatures.celsius:
        result = (value - 32) / 1.8
    else:
        return{"error":"an error occured"}
    return{"result":f"{result} {to_unit.value}", "value":f"{value} {from_unit.value}"}