## Setup

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

- Ports freigeben
  - https://serverfault.com/questions/416727/ufw-blocking-apt-and-dns
  - https://serverfault.com/questions/468907/ufw-blocking-apt


```
sudo apt-get install ufw
sudo ufw disable
sudo ufw reset
sudo ufw limit ssh
sudo ufw enable
```

