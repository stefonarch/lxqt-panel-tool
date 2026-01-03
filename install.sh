#!/bin/bash
until [[ action == [123] ]]; do
    clear
    read -s -n1 -p "
    This will install niri-settings. Please select

    1. Install only for user
    2. Install system-wide
    3. Quit

    Select 1, 2, or 3
" action
    case $action in
        1)
        echo "Installing to user..."
            mkdir -p ~/bin
            mkdir -p ~/.local/share/applications

            # Install binary and .desktop file
            cp -v lxqt-panel-tool.sh ~/bin/lxqt-panel-tool
            chmod a+x ~/bin/lxqt-panel-tool
            cp -v lxqt-panel-tool.desktop ~/.local/share/applications/

            # Install files
            #rm lxqt-panel-tool/translations/*.ts
            cp -av lxqt-panel-tool  ~/.local/share/

            echo ""

            # Posted by tripleee on stackoverflow
            # Retrieved 2025-12-10, License - CC BY-SA 3.0
            case :$PATH:
            in *:$HOME/bin:*) ;;
                *) echo "Note: $HOME/bin is not in $PATH" >&2
                   echo ""
                   echo "You need to add it, e.g. add a line" >&2
                   echo "    'PATH=\"$HOME/bin:\$PATH\"' in ~/.profile, or ~/.zshrc" >&2
                   echo "Otherwise lxqt-panel-tool cannot start." >&2 ;;
            esac
            echo "Installation finished."
        exit
        ;;
        2)
        echo "Installing to system..."

            # Install binary and .desktop file
            sudo cp -v lxqt-panel-tool.sh /usr/bin/lxqt-panel-tool
            sudo chmod a+x /usr/bin/lxqt-panel-tool
            sudo cp -v lxqt-panel-tool.desktop /usr/share/applications/

            # Install files
            #rm lxqt-panel-tool/translations/*.ts
            sudo cp -av lxqt-panel-tool/ /usr/share/

            echo ""
            echo "Installation finished."
        exit
    ;;
        3)
          echo "Goodbye!"
          exit
        ;;
      esac
done
