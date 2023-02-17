# aclue-dart-pi

Dieses Projekt stelle eine einfache API bereit um über eine Webcam oder ein Camera Modul ein Bild aufzunehmen.
Gedacht ist ein Einsatz auf einem RaspberryPi. 

## Dependencies

### With poetry
```
poetry install
poetry install --extras runtime # falls auf raspberry pi
poetry shell
````

### With `venv`

```
python3 -m venv env
source env/bin/activate
pip3 install xxx

```


### OpenCV
Die aktuelle Version kann aktuell (09.02.2023) nicht installiert werden. Als workaround nutzen wir eine ältere Version.

```
# this one doesn't work:
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host www.piwheels.org opencv-python

# this one does
pip3 install opencv-python==4.5.3.56 --trusted-host www.piwheels.org
```

OpenCV braucht manche dependencies welche nicht per default auf dem RaspberryPI installiert sind.

```
# open_cv dependencies

sudo apt-get install libcblas-dev
sudo apt-get install libhdf5-dev
sudo apt-get install libhdf5-serial-dev
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev 
sudo apt-get install libqtgui4 
sudo apt-get install libqt4-test
```

## Sync code Notebook <=> RaspberryPi
```
rsync -av --delete src/ pi@raspberrypi:~/dev/aclue-dart-pi/src/
```

## Server starten

```
cd src
uvicorn main:app --reload --host=0.0.0.0

=> http://localhost:8000/
```


## API Latenz messen
```
Get Image time:
curl -o /dev/null -s -w 'Total: %{time_total}s\n' http://raspberrypi:8000/api/imagev2
```

# Image capturing

Gibt verschiedene Möglichkeiten:
1) numpy array -> PIL -> BytesIO buffer
2) numpy array -> imageio -> BytesIO buffer
3) numpy array -> pypng.Writer -> BytesIO buffer

Auf einem MacBook Pro dauert es je 1.5s, 5s, 90ms.
PyPng ist also deutlich schneller. Auf dem RaspberryPi haben wir dadurch die Aufnahmezeit von ~3s auf 400ms-1300ms (720p vs 1080p) reduziert.