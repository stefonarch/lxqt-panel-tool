from PyQt6.QtWidgets import QApplication, QListView, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMessageBox, QFileDialog, QInputDialog, QStyle, QLabel
from PyQt6.QtCore import QStringListModel, QDir, Qt, QTranslator, QLocale, QLibraryInfo, QTimer, QFile
import sys, os, shutil, subprocess, filecmp
from configparser import ConfigParser

class NonEditableStringListModel(QStringListModel):
    def flags(self, index):
        # Remove the editable flag
        default_flags = super().flags(index)
        return default_flags & ~Qt.ItemFlag.ItemIsEditable

class FileListViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        self.model = NonEditableStringListModel()

        self.view = QListView()
        self.view.setModel(self.model)
        self.main_layout.addWidget(self.view)
        self.view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.user_layouts_dir = os.path.expanduser("~/.local/share/lxqt-panel-tool/layouts")
        self.load_directories_with_panel_conf(self.user_layouts_dir)

        self.button_layout = QHBoxLayout()
        self.button1_layout = QHBoxLayout()
        self.save_btn = QPushButton(self.tr('Save / Update'))
        self.load_btn = QPushButton(self.tr('Load'))
        self.rename_btn = QPushButton(self.tr('Rename'))
        self.delete_btn = QPushButton(self.tr('Trash'))

        self.load_btn.clicked.connect(self.load_panel_conf)
        self.load_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        self.load_btn.setToolTip(self.tr('Use the selected configuration'))
        self.load_btn.setEnabled(False)

        self.save_btn.clicked.connect(self.save_current_layout)
        self.save_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.save_btn.setToolTip(self.tr('Save or update this configuration'))
        self.save_btn.setEnabled(False)

        self.rename_btn.clicked.connect(self.rename_selected_directory)
        self.rename_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.rename_btn.setToolTip(self.tr('Rename the selected configuration'))
        self.rename_btn.setEnabled(False)

        self.delete_btn.clicked.connect(self.delete_selected_directory)
        self.delete_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.delete_btn.setToolTip(self.tr('Remove the selected configuration'))
        self.delete_btn.setEnabled(False)

        self.close_btn = QPushButton(self.tr("Quit"))
        self.close_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))
        self.close_btn.clicked.connect(self.close)

        self.button_layout.addWidget(self.load_btn)


        self.button_layout.addWidget(self.rename_btn)
        self.button_layout.addWidget(self.delete_btn)
        self.button1_layout.addWidget(self.save_btn)
        self.button1_layout.addStretch()
        self.button1_layout.addWidget(self.close_btn)

        self.status_label = QLabel()
        self.status_label.setIndent(15)
        self.main_layout.addWidget(self.status_label)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.button1_layout)

        self.setLayout(self.main_layout)
        self.setWindowTitle(self.tr("LXQt Panel Tool"))

    def load_directories_with_panel_conf(self, directory_path):
        dir = QDir(directory_path)
        dir.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        dir.setSorting(QDir.SortFlag.Time)  # newest first
        directories = dir.entryList()
        valid_directories = []
        for directory in directories:
            full_path = os.path.join(directory_path, directory)
            if os.path.exists(os.path.join(full_path, "panel.conf")):
                valid_directories.append(directory)

        valid_directories.insert(1, "·································")

        self.model.setStringList(valid_directories)

    def on_selection_changed(self):
        indexes = self.view.selectionModel().selectedIndexes()
        #self.status_label.setText("")
        self.hasupdates = False

        self.load_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.rename_btn.setEnabled(False)


        if not indexes:
            return
        index = indexes[0]
        value = index.data()
        self.show_diff()

        if "·······" in value:
            self.save_btn.setEnabled(False)

            self.save_btn.setEnabled(False)
            self.load_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.rename_btn.setEnabled(False)

        elif "In use" in value:
            self.save_btn.setEnabled(True)

        else:
            self.save_btn.setEnabled(False)
            self.load_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.rename_btn.setEnabled(True)

    def load_panel_conf(self):
        selected_index = self.view.currentIndex()
        selected_directory = self.model.data(selected_index)
        source_file = os.path.join(self.user_layouts_dir, selected_directory, "panel.conf")
        destination_file = os.path.expanduser("~/.config/lxqt/panel.conf")
        # check for qdbus name
        for prog in ("qdbus6", "qdbus-qt6", "qdbus"):
            qdbus = shutil.which(prog)
            if qdbus:
                break
            else:
                QMessageBox.critical(self, self.tr("Error"), self.tr("'qdbus' not found - please install it"))
                return False
        try:
            shutil.copy(source_file, destination_file)
            # create "In use"
            target_dir = os.path.join(self.user_layouts_dir, f"In use: {selected_directory}")
            #remove previous:
            for name in os.listdir(self.user_layouts_dir):
                if name.startswith("In use"):
                    shutil.rmtree(os.path.join(self.user_layouts_dir, name))
                    break
            os.makedirs(target_dir)
            shutil.copy(os.path.expanduser("~/.config/lxqt/panel.conf"), os.path.join(target_dir, "panel.conf"))
            self.load_directories_with_panel_conf(self.user_layouts_dir)

            subprocess.run("qdbus org.lxqt.session /LXQtSession org.lxqt.session.stopModule lxqt-panel.desktop; sleep 1", shell=True, check=True)
            subprocess.run("qdbus org.lxqt.session /LXQtSession org.lxqt.session.startModule lxqt-panel.desktop", shell=True, check=True)

        except PermissionError:
            self.status_label.setText(self.tr("Failed to copy panel.conf: Permission denied."))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy panel.conf: {str(e)}")

    def delete_selected_directory(self):
        selected_index = self.view.currentIndex()
        selected_directory = self.model.data(selected_index)
        directory_path = os.path.join(self.user_layouts_dir, selected_directory)

        config = self.tr("Move to trash the configuration '%s'?") % selected_directory
        reply = QMessageBox.question(self, self.tr("Confirm"),config,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                #shutil.rmtree(directory_path)
                QFile.moveToTrash(directory_path)
                self.model.removeRow(selected_index.row())
                self.status_label.setText(self.tr("Configuration moved to trash."))
                QTimer.singleShot(2000, lambda: self.status_label.setText(""))
            except PermissionError:
                self.status_label.setText(self.tr("Failed to trash configuration:\nPermission denied."))
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), f"Failed to trash configuration: {str(e)}")

    def rename_selected_directory(self):
        selected_index = self.view.currentIndex()
        selected_directory = self.model.data(selected_index)
        new_name, ok = QInputDialog.getText(self, self.tr("Rename configuration"), self.tr("Enter new name:"), text=selected_directory)

        if ok:
            if new_name.strip() == "":
                QMessageBox.warning(self, self.tr("Invalid Name"), self.tr("A name is required."))
                return

            old_path = os.path.join(self.user_layouts_dir, selected_directory)
            new_path = os.path.join(self.user_layouts_dir, new_name)

            try:
                os.rename(old_path, new_path)
                self.load_directories_with_panel_conf(self.user_layouts_dir)
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), f"Failed to rename configuration: {str(e)}")


    def save_current_layout(self):
        print(f"{self.hasupdates}")

        if self.hasupdates:
            self.update_configuration()


        else:
            name, ok = QInputDialog.getText(self, self.tr("Save Panel Configuration"), self.tr("Enter a name:"))

            if ok:
                if name.strip() == "":
                    QMessageBox.warning(self, self.tr("Invalid Name"), self.tr("A name is required."))
                    return
                target_dir = os.path.join(self.user_layouts_dir, name)

                if os.path.exists(target_dir):
                    reply = QMessageBox.question(
                        self, "Overwrite Existing",
                        f"A configuration named '{name}' already exists. Overwrite?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return

                try:
                    current_dir = os.path.join(self.user_layouts_dir, f"In use: {name}")
                    #remove previous:
                    for name in os.listdir(self.user_layouts_dir):
                        if name.startswith("In use"):
                            shutil.rmtree(os.path.join(self.user_layouts_dir, name))
                            break
                    os.makedirs(target_dir)
                    os.makedirs(current_dir)
                    shutil.copy(os.path.expanduser("~/.config/lxqt/panel.conf"), os.path.join(target_dir, "panel.conf"))
                    shutil.copy(os.path.expanduser("~/.config/lxqt/panel.conf"), os.path.join(current_dir, "panel.conf"))
                    self.load_directories_with_panel_conf(self.user_layouts_dir)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")

    def update_configuration(self):
        selected_index = self.view.currentIndex()
#        selected_index = self.model.index(0, 0) try that later
        current_directory = self.model.data(selected_index) # "In use: name"
        saved_directory= current_directory.replace("In use: ", "", 1) # "name"

        #directory_path = os.path.join(self.user_layouts_dir, dest_directory)
        displayed_file = os.path.join(self.user_layouts_dir, current_directory, "panel.conf")
        saved_file = os.path.join(self.user_layouts_dir, saved_directory, "panel.conf")
        loaded_file = os.path.expanduser("~/.config/lxqt/panel.conf")

        message = self.tr("Update the saved configuration '%s'\nwith the current configuration?") % saved_directory

        reply = QMessageBox.question(self, "Confirm Update", message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                shutil.copy(loaded_file, displayed_file)
                shutil.copy(loaded_file, saved_file)
                message = self.tr("Updated configuration '%s'.") % saved_directory
                self.status_label.setText(message)
                QTimer.singleShot(2000, lambda: self.status_label.setText(""))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update configuration: {str(e)}")

    def show_diff(self):
        selected_index = self.model.index(0, 0)
        current_directory = self.model.data(selected_index) # "In use: name"
        dest_directory = current_directory.replace("In use: ", "", 1)
        full_path = os.path.join(self.user_layouts_dir, dest_directory)

        if os.path.exists(full_path):
            loaded = os.path.expanduser("~/.config/lxqt/panel.conf")
            saved = os.path.join(self.user_layouts_dir, dest_directory, "panel.conf")

            if not filecmp.cmp(loaded, saved, shallow=False):
                self.status_label.setText(self.tr("Configuration in use has unsaved changes."))

                self.hasupdates = True
        else:
            return

def main():
    app = QApplication(sys.argv)
    app.setDesktopFileName("lxqt-panel-tool")

    # Setup translator with XDG_DATA_DIRS lookup
    locale = QLocale.system().name()  # e.g., "it_IT"
    language_only = locale.split('_')[0]  # e.g., "it"

    translator = QTranslator()
    translation_loaded = False

    # Get XDG_DATA_DIRS from environment with fallback
    xdg_data_dirs = os.environ.get('XDG_DATA_DIRS', '/usr/local/share/:/usr/share/')
    data_dirs = xdg_data_dirs.split(':')

    # Try both full locale and language-only versions
    locale_variants = [locale, language_only]

    qt_translator = QTranslator()
    qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if qt_translator.load(f"qt_{language_only}", qt_translations_path):
        app.installTranslator(qt_translator)

    for locale_var in locale_variants:
        for data_dir in data_dirs:
            trans_path = os.path.join(data_dir, "lxqt-panel-tool", "translations", f"lxqt-panel-tool_{locale_var}.qm")
            if os.path.exists(trans_path) and translator.load(trans_path):
                app.installTranslator(translator)
                print(f"Loaded translation: {trans_path}")
                translation_loaded = True
                break

    viewer = FileListViewer()
    viewer.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()

