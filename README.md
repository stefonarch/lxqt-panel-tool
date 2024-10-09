# LXQt Panel Profiles
## About
LXQt Panel Profiles is a program intended create an equivalent to XFCE's panel profiles program for LXQt. Users of this program will find that it behaves very similarly.

## Installation
### For Debian:

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

### Arch: 
TODO
