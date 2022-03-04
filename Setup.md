## Setup

- Add new sudo user
```
useradd <username>
passwd <username>
usermod -aG sudo <username>
```

- Raspberry OS`aktuallisieren

```
sudo apt-get update
sudo apt-get upgrade
```

- Kamera Modul aktivieren

`sudo raspi-config` => Interfacing

- /boot/config anpassen

`````
sudo nano /boot/config
// Dann folgendes anpassen/anfügen
[all]
gpu_mem=192
// ggf. auch:
start_x=1
`````

  `libcamera-hello`

- Ports freigeben

```
sudo apt-get install ufw
sudo ufw disable
sudo ufw reset
sudo ufw limit ssh
sudo ufw enable
```


```
sudo ufw default deny incoming
sudo ufw default deny outgoing
sudo ufw allow ssh
sudo ufw allow git
sudo ufw allow out http
sudo ufw allow in http 
sudo ufw allow out https
sudo ufw allow in https
sudo ufw allow 53
sudo ufw allow 123
sudo ufw allow dns

sudo ufw allow 8000

sudo ufw logging on

sudo ufw enable

```