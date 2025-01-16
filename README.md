# FastAPI Users example

setup virtualenv:
```
python -m venv .venv
.venv\scripts\activate
pip install -r requirements.txt
```

run:
```
fastapi dev
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Creating a superuser

To create a superuser you have to edit the db directly:
```sql
UPDATE user SET is_superuser=1 WHERE id=3
```