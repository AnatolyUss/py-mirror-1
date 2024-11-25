import os
import sys
import asyncio

import uvicorn

cwd = os.getcwd()
sys.path.append(cwd)
mode = sys.argv[1]

if mode == "--init-db":
    from py_mirror.app.storage.pg.data_source import DataSource

    asyncio.run(DataSource().init_db())
elif mode == "--run-api":
    from dotenv import dotenv_values
    from py_mirror.app.api.main import get_api

    env_vars = {**dotenv_values(".env"), **os.environ}
    api = get_api()
    uvicorn.run(api, host="localhost", port=int(str(env_vars.get("HTTP_PORT"))))
else:
    sys.exit(f"Invalid mode {mode}")  # Exit status is "1", meaning failure.
