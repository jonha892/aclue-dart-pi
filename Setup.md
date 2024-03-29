# Setup

1. SD Karte mit Raspberry PI imager aufsetzen https://www.raspberrypi.com/software/
   In den Einstellungen
   - Netzwerknamen setzen
   - WLAN einrichten
   - Passwort setzen
   - SSH mit username & passwort erlauben
2. Mit dem Pi verbinden & updaten. Firemware update kann ein wenig dauern
   ```
   ssh pi@raspberrypi
   sudo apt update
   sudo rpi-update
   ```
3. Reboot
   ```
   sudo reboot
   ```
4. Enable legacy camera (skip falls wir webcam benutzen)

   ```
   sudo raspi-config
   => Interface Options => Legacy Camera => Yes => Finish => reboot
   ```

   1. Boot config anpassen. Teilwise sind die Werte schon gesetzt

      ```
      sudo nano /boot/config

      gpu_mem=192
      start_x=1

      dtoverlay=vc4-fkms-v3d
      #dtoverlay=imx219 (dieses overlay funktioniert mit der legacy camera nicht)
      ```

   2. Camera testen
      ```
      raspistill -o test.jpt
      ```
      `libcamera-hello` funktioniert mit der legacy camera nicht.

5. Firewall configurieren. (Damit der Python server über das lokale Netzwerk erreichbar ist)

   ```
   sudo apt install ufw
   sudo ufw default deny incoming
   sudo ufw default deny outgoing
   sudo ufw allow ssh
   sudo ufw allow git
   sudo ufw allow out http
   sudo ufw allow in http
   sudo ufw allow out https
   sudo ufw allow in https
   sudo ufw allow 53
   sudo ufw allow out 53
   sudo ufw allow 123
   sudo ufw allow dns
   sudo ufw allow 8000
   sudo ufw logging on

   sudo ufw enable
   ```

6. Python version prüfen
   ```
   python --version
   ```
7. Repo code auf den PI kopieren

   ```
   (auf dem PI)
   mkdir ~/dev
   mkdir ~/dev/aclue-dart-pi
   (auf dem Host)
   rsync -avz --exclude 'env' --exclude '.git' . pi@raspberrypi:~/develop/aclue-dart-pi
   ```

8. Python venv aufsetzen & dependencies
   ```
   python -m venv env
   source env/bin/activate
   pip install picamera
   pip install "fastapi[all]"
   ```
9. Anwendung starten
   ```
   source env/bin/activate
   cd src
   uvicorn main:app --reload --port=8000 --host=0.0.0.0
   ```
10. Änderungen von Host auf PI pushen
    ```
    rsync -av --delete --exclude ~/Dev/aclue-dart-pi/env ~/Dev/aclue-dart-pi/ pi@raspberrypi:~/dev/aclue-dart-pi/
    ```
