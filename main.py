import os
import sys
import asyncio

from dotenv import dotenv_values

from py_mirror.app.storage.pg.data_source import DataSource

cwd = os.getcwd()
sys.path.append(cwd)
env = {**dotenv_values(".env"), **os.environ}
mode = sys.argv[1]

if mode == "--init-db":
    asyncio.run(DataSource().init_db())
elif mode == "--run-api":
    pass
else:
    sys.exit(f"Invalid mode {mode}")  # Exit status is "1", meaning failure.

# from fastapi import FastAPI
# app = FastAPI()


# @app.post("/request")
# def read_root():
#     return {"Hello": "World"}
#
#
# @app.get("/model")
# def read_item():
#     pass
