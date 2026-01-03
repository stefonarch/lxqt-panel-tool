#!/bin/bash
if [ ! -d "$XDG_DATA_HOME/lxqt-panel-tool/" ]; then
    mkdir -p $XDG_DATA_HOME/lxqt-panel-tool/
    cp -av /usr/share/lxqt-panel-tool/layouts $XDG_DATA_HOME/lxqt-panel-tool/
    mkdir -p $XDG_DATA_HOME/lxqt-panel-tool/layouts/panel-"$USER"/
    mkdir -p $XDG_DATA_HOME/lxqt-panel-tool/layouts/Default\ panel/
    cp /etc/xdg/lxqt/panel.conf $XDG_DATA_HOME/lxqt-panel-tool/layouts/Default\ panel/
    cp $XDG_CONFIG_HOME/lxqt/panel.conf $XDG_DATA_HOME/lxqt-panel-tool/layouts/panel-"$USER"/
    cp -a $XDG_DATA_HOME/lxqt-panel-tool/layouts/panel-"$USER"/ $XDG_DATA_HOME/lxqt-panel-tool/layouts/In\ use:\ panel-"$USER"/

    # Import lxqt-panel-profiles
    if [ -d "$XDG_DATA_HOME/lxqt-panel-profiles/" ]; then
        echo "Found lxqt-panel-profiles, importing..."
    cp -av $XDG_DATA_HOME/lxqt-panel-profiles/layouts/* $XDG_DATA_HOME/lxqt-panel-tool/layouts/
    fi
fi

# first try local installation

if [ -f "$XDG_DATA_HOME/lxqt-panel-tool/lxqt-panel-tool.py" ]; then
    exec python3 "$XDG_DATA_HOME/lxqt-panel-tool/lxqt-panel-tool.py"
else
    exec python3 "/usr/share/lxqt-panel-tool/lxqt-panel-tool.py"
fi
