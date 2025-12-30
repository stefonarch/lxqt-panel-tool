## LXQt Panel Tool

> LXQt Panel Tool creates backups and switches different lxqt-panel configurations.
> It is a fork of https://codeberg.org/MrReplikant/lxqt-panel-profiles.git

![Screenshot of lxqt-panel-tool](lxqt-panel-tool.png)

## Arch Linux and derivatives

Install the [AUR package](https://aur.archlinux.org/packages/lxqt-panel-tool).

## Manual Installation

First, install the dependencies on your system.
Note: As is also the case with Debian and Ubuntu, some Fedora versions are still using the Qt5 version of LXQt.
This will not affect core functionality, but it WILL cause LXQt Panel Profiles not following the themes on those systems.

### Fedora 41:
```
sudo dnf install lxqt-panel tar python3-pyqt6 qt6-qdbusviewer
```
### Fedora 40:
```
```

### Alpine Linux Edge:
```
apk add lxqt-panel tar py3-pyqt6 qt6-qdbusviewer
```

### Arch Linux:
```
sudo pacman -S lxqt-panel python-pyqt6 qt6-tools
```

### Then for ALL of them:
```
git clone https://codeberg.org/MrReplikant/lxqt-panel-profiles.git
cd lxqt-panel-profiles
sudo cp -a usr/* /usr/
```

And done!


## Screenshots

### MX Linux
![img](screenshots/MX-Linux.jpg)

### MATE
![img](screenshots/MATE-profile.jpg)

### Redmond (win95)
![img](screenshots/Redmond.jpg)
