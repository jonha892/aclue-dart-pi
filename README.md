# aclue-dart-pi

```
poetry install
poetry install --extras runtime # falls auf raspberry pi
poetry shell

cd src
uvicorn main:app --reload --host=0.0.0.0

=> http://localhost:8000/
```