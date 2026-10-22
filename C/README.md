# U6143_ssd1306
## Enable i2c 
```bash
sudo raspi-config
```
Choose Interface Options 
Enable i2c

##  Download library 
```bash
git clone https://github.com/Geekamacker/U6143_ssd1306.git
```
## Compile the source code 
```bash
cd U6143_ssd1306/C 
```
```bash
make 
```


## Run the display

```bash 
cd U6143_ssd1306/C 
```
```bash 
./display 
```




## Previous-boot diagnostic display

Display page 6 reads `/var/lib/uctronics-display/last_boot_status`, populated
by `../boot_diagnostics.sh` and its systemd service after boot. See the top-level
README for installation and interpretation. The OLED cannot diagnose a fully
frozen Raspberry Pi until it restarts, and may show `LOG: NO CAUSE`.
