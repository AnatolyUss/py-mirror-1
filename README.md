# py-mirror-1
<b>For learning purposes only...</b>

Install GNU Make: <code>brew install make</code>

Run prior using <code>pyenv</code>: <code>source ~/.bash_profile</code>

Create venv: <code>python -m venv py_mirror_1_venv</code>

Activate venv: <code>. py_mirror_1_venv/bin/activate</code>

Deactivate venv: <code>. deactivate</code>

List all versions available: <code>pyenv install -l</code>

Install CPython 3.12.5: <code>pyenv install 3.12.5</code>

Switch to certain CPython version: <code>pyenv global 3.12.5</code>

Run linter: <code>ruff check && git status</code>
Run formatter: <code>ruff format && git status</code>

Run Mypy: <code>mypy -p py_mirror</code>

Run FastAPI: <code>fastapi dev api.py</code>
Run FastAPI Swagger: <code>http://127.0.0.1:8000/docs</code>

Install dependency via <code>pip</code>: <code>rm requirements.txt && pip install {..} && pip freeze >> requirements.txt</code>
For example: <code>rm requirements.txt && pip install confluent-kafka && pip freeze >> requirements.txt</code>

Install dependency via <code>requirements</code> file: <code>pip install -r requirements.txt && rm requirements.txt && pip freeze >> requirements.txt</code>
