# U6143_ssd1306 (Geekamacker fork)

UCTRONICS 0.91\" SSD1306 I2C OLED display + a **systemd** service installer, with a rotating multi-page status dashboard.  
This fork also supports **time-synced page rotation** so multiple Raspberry Pis can stay aligned.

---

## What it displays (6 pages)

Pages rotate in order `0..5`:

- **Page 0**: CPU Temperature + CPU Load  
- **Page 1**: RAM (**USED / TOTAL**)  
- **Page 2**: SD card storage (**USED / TOTAL**)  
- **Page 3**: Hostname + Date/Time  
- **Page 4**: MAC Address + Ping `8.8.8.8` (**OK/FAIL**)  
- **Page 5**: SD card / MMC `cmd error -110` **count** + **days since last**

**Top line:** shows the Pi’s IP address (or your custom label via `CUSTOM_DISPLAY`) across all pages.

> **IP note (this fork):** IP is detected automatically from the default route, so it works even if your interface isn’t `eth0`/`wlan0`.

---

## Install

### 1) Clone this repo

```bash
cd ~
git clone https://github.com/Geekamacker/U6143_ssd1306.git
cd U6143_ssd1306
```

### 2) Run the installer

```bash
chmod +x setup_display_service.sh
sudo ./setup_display_service.sh
```

The installer will:
- Attempt to **enable I2C** (via `raspi-config` when available)
- Ensure `dtparam=i2c_arm=on` is set (when possible)
- Load I2C modules (best effort)
- Install `i2c-tools` if missing and run `i2cdetect -y 1`
- Compile the C program and set up the `uctronics-display` systemd service

> If the script reports I2C was enabled in config, a **reboot may be required**.

---

## Service management

```bash
sudo systemctl status uctronics-display.service
sudo systemctl restart uctronics-display.service
sudo systemctl stop uctronics-display.service
sudo journalctl -u uctronics-display.service -f
```

---

## Multi-Pi synced page rotation

Page selection can be based on wall clock time so multiple Pis show the same page at the same time.

Make sure time is synced:

```bash
timedatectl status
```

Look for: `System clock synchronized: yes`

---

## For older 0.91\" LCD without MCU (Python demo)

For the older version LCD without MCU controller, you can use the Python demo.

Install dependent libraries:

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil
sudo pip3 install adafruit-circuitpython-ssd1306
```

Test demo:

```bash
cd ~/U6143_ssd1306/python
sudo python3 ssd1306_stats.py
```

---

## Configuration

### Temperature unit (Celsius vs Fahrenheit)

Open `C/ssd1306_i2c.h` and modify `TEMPERATURE_TYPE`.

![EasyBehavior](https://github.com/UCTRONICS/pic/blob/master/OLED/select_temperature.jpg)

### Top line: IP vs custom label

Open `C/ssd1306_i2c.h`:

- Set `IP_SWITCH` to show IP or `CUSTOM_DISPLAY`
- Set `CUSTOM_DISPLAY` to your label (example: `"GEEKAPI"`)

![EasyBehavior](https://github.com/UCTRONICS/pic/blob/master/OLED/custom_display.jpg)

---

## Uninstall / switch from upstream to this fork

If you installed the upstream UCTRONICS repo first and want to remove it cleanly:

### 1) Stop + disable the service

```bash
sudo systemctl stop uctronics-display.service
sudo systemctl disable uctronics-display.service
```

### 2) Remove the service file + reload systemd

```bash
sudo rm -f /etc/systemd/system/uctronics-display.service
sudo systemctl daemon-reload
```

(Optional) confirm it’s gone:

```bash
systemctl status uctronics-display.service
```

### 3) Remove the old repo folder

If the old one is in `~/U6143_ssd1306`:

```bash
rm -rf ~/U6143_ssd1306
```

(Optional) list matching folders first:

```bash
ls -la ~ | grep U6143
```

### 4) Install this fork

```bash
cd ~
git clone https://github.com/Geekamacker/U6143_ssd1306.git
cd U6143_ssd1306
chmod +x setup_display_service.sh
sudo ./setup_display_service.sh
```

### 5) Verify it’s running

```bash
sudo systemctl status uctronics-display.service
```
