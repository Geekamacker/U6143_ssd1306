[README.md](https://github.com/user-attachments/files/33848545/README.md)
# U6143_ssd1306 (Geekamacker fork)

UCTRONICS 0.91\" SSD1306 I2C OLED display + a **systemd** service installer, with a rotating multi-page status dashboard.  
This fork also supports **time-synced page rotation** so multiple Raspberry Pis can stay aligned.

---

## What it displays (7 pages)

Pages rotate in order `0..6` (3 seconds per page; 21-second cycle):

- **Page 0**: CPU Temperature + CPU Load  
- **Page 1**: RAM (**USED / TOTAL**)  
- **Page 2**: SD card storage (**USED / TOTAL**)  
- **Page 3**: Hostname + Date/Time  
- **Page 4**: MAC Address + Ping `8.8.8.8` (**OK/FAIL**)  
- **Page 5**: Current-boot SD card / MMC `cmd error -110` **count** + **days since last** (false count of 1 with no logs fixed)
- **Page 6**: **Previous boot status** + any failure-related **journal clue** (see below)

**Top line:** shows the Pi’s IP address (or your custom label via `CUSTOM_DISPLAY`) across all pages.

> **IP note (this fork):** IP is detected automatically from the default route, so it works even if your interface isn’t `eth0`/`wlan0`.

---


## Previous-boot crash diagnostics (page 6)

The installer sets up `uctronics-boot-diagnostics.service` alongside the existing
`uctronics-display.service`. On startup, it reads a marker from the previous boot:

- `PREV: CLEAN` / `LOG: N/A`: systemd stopped the diagnostic service normally.
- `PREV: UNCLEAN` / `LOG: NO CAUSE`: an orderly stop was **not recorded**, and the retained journal did not capture a recognizable failure. **The root cause remains unknown.**
- `PREV: UNCLEAN` / `LOG: MMC ERROR`, `LOG: PANIC/LOCKUP`, etc.: a relevant log message appeared in the *final hour of saved log entries* from the previous boot. **It is a clue, not proof of the cause.**
- `PREV: UNCLEAN` / `LOG: NOT SAVED`: the previous boot's journal wasn't accessible.
- `PREV: UNTRACKED` / `LOG: NO BASELINE`: the first boot after installation; there is no earlier shutdown marker to compare.

Page 6 is a **post-reboot summary**. If the whole Pi freezes, the OLED code also
freezes and cannot diagnose the cause live. A power loss, kernel stall, or SD
card failure may leave **no final log**, so this page cannot guarantee an answer.
For evidence outside the OLED's two short lines, run:

```bash
sudo bash ~/U6143_ssd1306/boot_diagnostics.sh report
sudo journalctl -b -1 -p warning..alert --no-pager
sudo journalctl -k -b -1 --no-pager | tail -100
```

Evidence and clean-shutdown markers are stored in:

- `/var/lib/uctronics-display/last_boot_status` — two OLED lines
- `/var/lib/uctronics-display/last_boot_report.txt` — previous boot and matching journal evidence
- `/var/lib/uctronics-display/boot_state` — marker for normal vs abrupt stop

The status recorder runs once at boot and once at orderly service shutdown;
**it does not poll or continuously write metrics to the SD card**. The MMC
page still polls the current boot's kernel journal as before. It now uses
quiet journal output and closes its process handle correctly.

**Persistent journaling is required** to analyze logs across reboots. On
Raspberry Pi OS, a vendor `40-rpi-volatile-storage.conf` setting can override
an earlier filename. If you want retained logs, create a later
`/etc/systemd/journald.conf.d/90-persistent.conf` with:

```ini
[Journal]
Storage=persistent
SystemMaxUse=100M
```

Then restart and flush journald. Verify the effective configuration with
`systemd-analyze cat-config systemd/journald.conf` and check that
`sudo journalctl --directory=/var/log/journal --list-boots` sees retained boots.
The installer **does not change** journald settings automatically.

### Upgrade on a Pi already using this fork

Copy the updated files into your existing `~/U6143_ssd1306` directory, keeping
any local modifications you need. Then run:

```bash
cd ~/U6143_ssd1306
sudo bash ./setup_display_service.sh
```

Enter `y` when prompted to replace the existing display service. The installer
compiles as your regular user, installs the diagnostic service and **restarts**
the display so the new binary is actually used. It does not update Pi-hole,
change storage devices, or alter your kernel/watchdog configuration.

Check operation:

```bash
systemctl status uctronics-display.service uctronics-boot-diagnostics.service
sudo bash ~/U6143_ssd1306/boot_diagnostics.sh report
```

## Ubuntu on Raspberry Pi notes (if needed)

This repo works on **Ubuntu on Raspberry Pi** (Server/Desktop), with a couple of extra prerequisites.

### 1) Install prerequisites

```bash
sudo apt-get update
sudo apt-get install -y git build-essential i2c-tools
```

- `build-essential` provides `make` + `gcc` needed to compile.
- `i2c-tools` provides `i2cdetect` for quick verification.

### 2) Enable I2C (Ubuntu on Pi)

Ubuntu Pi images commonly use:

- `/boot/firmware/config.txt`

```bash
sudo nano /boot/firmware/config.txt
```
or

if diskless:

- `/boot/firmware/config.txt`

```bash
sudo nano /boot/config.txt
```

Make sure this line exists:

```txt
dtparam=i2c_arm=on
```

Reboot after enabling:

```bash
sudo reboot
```

### 3) Verify the OLED is detected

```bash
ls -l /dev/i2c-*
sudo apt-get update
sudo apt-get install -y i2c-tools
sudo i2cdetect -y 1
```

You will typically see `3c` (the SSD1306 default I2C address) if wiring/address is correct.

> On Ubuntu, `raspi-config` may not be installed, so the installer will skip that part automatically.

---


## Install

### 1) Install Git

```bash
sudo apt-get update
sudo apt-get install -y git
sudo apt-get install -y build-essential
```

### 2) Clone this repo

```bash
cd ~
git clone https://github.com/Geekamacker/U6143_ssd1306.git
cd U6143_ssd1306
```

### 3) Run the installer

```bash
cd ~/U6143_ssd1306
chmod +x setup_display_service.sh
sudo ./setup_display_service.sh
```

### 5) Verify it’s running
```bash
sudo systemctl status uctronics-display.service --no-pager
```

The installer will:
- Attempt to **enable I2C** (via `raspi-config` when available)
- Ensure `dtparam=i2c_arm=on` is set (when possible)
- Load I2C modules (best effort)
- Install `i2c-tools` if missing and run `i2cdetect -y 1`
- Compile the C program and set up the `uctronics-display` systemd service
- Enable `uctronics-boot-diagnostics.service` to record a persistent clean/unclean boot marker and show available journal clues

> If the script reports I2C was enabled in config, a **reboot may be required**.

### 4) Syncing in a display cluster

This will refresh/force timesync in a diskless set up.

```bash
sudo timedatectl set-ntp true
sudo systemctl restart systemd-timesyncd
sleep 5
timedatectl status
```

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

Follow the steps from the install section.
