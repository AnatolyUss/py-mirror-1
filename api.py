import os
import sys

from fastapi import FastAPI

cwd = os.getcwd()
sys.path.append(cwd)

app = FastAPI()


@app.post("/request")
def read_root():
    return {"Hello": "World"}


@app.get("/model")
def read_item():
    pass
