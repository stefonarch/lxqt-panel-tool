#!/bin/bash
if [ ! -d "$XDG_DATA_HOME/lxqt-panel-profiles/" ]; then
    mkdir -p $XDG_DATA_HOME/lxqt-panel-profiles/
    #cp -r /usr/share/lxqt-panel-tools/layouts $XDG_DATA_HOME/lxqt-panel-profiles
    mkdir -p $XDG_DATA_HOME/lxqt-panel-profiles/layouts/lxqt-panel/
    mkdir -p $XDG_DATA_HOME/lxqt-panel-profiles/layouts/Default\ panel/
    cp /etc/xdg/lxqt/panel.conf $XDG_DATA_HOME/lxqt-panel-profiles/layouts/Default\ panel/
    cp $XDG_CONFIG_HOME/lxqt/panel.conf $XDG_DATA_HOME/lxqt-panel-profiles/layouts/lxqt-panel/
    cp $XDG_CONFIG_HOME/lxqt/panel.conf $XDG_DATA_HOME/lxqt-panel-profiles/layouts/xqt-panel/
    cp -a $XDG_DATA_HOME/lxqt-panel-profiles/layouts/lxqt-panel/ $XDG_DATA_HOME/lxqt-panel-profiles/layouts/In\ use:\ lxqt-panel/

fi

# first try local installation

if [ -f "$HOME/.local/share/lxqt-panel-tool/lxqt-panel-tool.py" ]; then
    exec python3 "$HOME/.local/share/lxqt-panel-tool/lxqt-panel-tool.py"
else
    exec python3 "/usr/share/lxqt-panel-tool/lxqt-panel-tool.py"
fi

#python3 /usr/share/lxqt-panel-tool/lxqt-panel-tool.py
#python /home/stef/git/stefonarch/lxqt-panel-tool/lxqt-panel-tool/lxqt-panel-tool.py
