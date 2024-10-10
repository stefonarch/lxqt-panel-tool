# LXQt Panel Profiles
## About
LXQt Panel Profiles is a program intended create an equivalent to XFCE's panel profiles program for LXQt. Users of this program will find that it behaves very similarly.

## Build the Debian Package (Debian 12 or higher)

```
cd lxqt-panel-profiles
sudo apt install debhelper
dpkg-buildpackage -b
```

This will generate a .deb file for the program in the directory above lxqt-panel profiles.
 
To install the package, run like so, assuming you are still in the lxqt-panel-profiles directory:

```
cd ..
sudo apt install ./lxqt-panel-profiles*.deb
```

## Manual Installation

First, install the dependencies on your system. Note: Some Fedora verisons are still using the Qt5 version of 
LXQt. This will not affect core functionality, but it WILL cause LXQt Panel Profiles to not follow the set system
theme on those systems. 

### Fedora 41: 
```
sudo dnf install lxqt-panel tar python3-pyqt6 qt6-qdbusviewer
```
### Fedora 40: 
```
sudo dnf install lxqt-panel tar python3-pyqt6 qt5-qdbusviewer
```

### Alpine Linux Edge: 
```
apk add lxqt-panel tar py3-pyqt6 qt6-qdbusviewer
```

### Arch Linux:
```
sudo pacman -S lxqt-panel tar python-pyqt6 qt6-tools
```

### Then for ALL of them:
```
cd lxqt-panel-profiles
cp -a usr/* /usr/
```

And done!


## Screenshots

TODO

