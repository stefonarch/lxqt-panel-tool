from PyQt6.QtWidgets import QApplication, QListView, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMessageBox, QFileDialog, QInputDialog, QStyle
from PyQt6.QtCore import QStringListModel, QDir, Qt
import sys
import os
import shutil
import subprocess
import tarfile

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
        self.user_layouts_dir = os.path.expanduser("~/.local/share/lxqt-panel-profiles/layouts")
        self.load_directories_with_panel_conf(self.user_layouts_dir)


        self.button_layout = QHBoxLayout()

        self.button1 = QPushButton()  # Import
        self.button2 = QPushButton()  # Apply
        self.button3 = QPushButton()  # Rename
        self.button4 = QPushButton()  # Delete
        self.button5 = QPushButton()  # Save current layout
        self.button6 = QPushButton()  # Share

        
        # Import Layout
        self.button1.clicked.connect(self.import_panel_layout)
        self.button1.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
        self.button1.setToolTip('Import')

        # Apply
        self.button2.clicked.connect(self.copy_panel_conf)
        self.button2.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        self.button2.setToolTip('Use selected profile')

        # Rename
        self.button3.clicked.connect(self.rename_selected_directory)
        self.button3.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.button3.setToolTip('Rename')

        # Delete
        self.button4.clicked.connect(self.delete_selected_directory)
        self.button4.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.button4.setToolTip('Delete')
        
        # Save current Layout
        self.button5.clicked.connect(self.save_current_layout)
        self.button5.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon))
        self.button5.setToolTip('Save current layout')


        # Share
        self.button6.clicked.connect(self.share_selected_directory)
        self.button6.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
        self.button6.setToolTip('Share')

        self.button_layout.addWidget(self.button1)
        self.button_layout.addWidget(self.button2)
        self.button_layout.addWidget(self.button3)
        self.button_layout.addWidget(self.button4)
        self.button_layout.addWidget(self.button5)
        self.button_layout.addWidget(self.button6)
        self.main_layout.addLayout(self.button_layout)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)  # Connect to the close method
        self.main_layout.addWidget(self.close_button)  # Add Close button to the main layout

        self.setLayout(self.main_layout)
        self.setWindowTitle("LXQt Panel Layouts")

    def load_directories_with_panel_conf(self, directory_path):
        dir = QDir(directory_path)
        # List only directories (no files)
        dir.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        directories = dir.entryList()
        valid_directories = []
        for directory in directories:
            full_path = os.path.join(directory_path, directory)
            if os.path.exists(os.path.join(full_path, "panel.conf")):
                valid_directories.append(directory)

        if "Current Layout" not in valid_directories:
            valid_directories.insert(0, "Current Layout")

        self.model.setStringList(valid_directories)

    def import_panel_layout(self):
        options = QFileDialog.Option(0)
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Panel Layout", "", "Tar Files (*.tar.gz);;All Files (*)", options=options)

        if file_name:
            try:
                with tarfile.open(file_name, "r:gz") as tar:
                    tar.extractall(path=self.user_layouts_dir)
                
                extracted_dirs = os.listdir(self.user_layouts_dir)
                valid_layout = False
                for directory in extracted_dirs:
                    if os.path.exists(os.path.join(self.user_layouts_dir, directory, "panel.conf")):
                        valid_layout = True
                        break
                
                if not valid_layout:
                    # If no valid layout found, clean up and show message
                    shutil.rmtree(self.user_layouts_dir)  # Remove all extracted directories
                    QMessageBox.warning(self, "Invalid Layout", "Not a valid Panel Layout.")
                else:
                    # If valid layout, update the view
                    self.load_directories_with_panel_conf(self.user_layouts_dir)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import panel layout: {str(e)}")

    def copy_panel_conf(self):
        # Get the selected index from the QListView
        selected_index = self.view.currentIndex()
        if not selected_index.isValid():
            QMessageBox.warning(self, "No Selection", "Please select a panel layout from the list.")
            return
        
        selected_directory = self.model.data(selected_index)

        # Handle "Current Layout" specifically
        if selected_directory == "Current Layout":
            source_file = os.path.expanduser("~/.config/lxqt/panel.conf")
        else:
            source_file = os.path.join(self.user_layouts_dir, selected_directory, "panel.conf")

        destination_file = os.path.expanduser("~/.config/lxqt/panel.conf")

        # Copy the panel.conf file and overwrite the destination
        try:
            shutil.copy(source_file, destination_file)
	    # Restart lxqt-panel
            subprocess.run("qdbus org.lxqt.session /LXQtSession org.lxqt.session.stopModule lxqt-panel.desktop; sleep 1", shell=True, check=True)
            subprocess.run("qdbus org.lxqt.session /LXQtSession org.lxqt.session.startModule lxqt-panel.desktop", shell=True, check=True)
        except PermissionError:
            QMessageBox.critical(self, "Permission Denied", f"Failed to copy panel.conf: Permission denied.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy panel.conf: {str(e)}")

    def delete_selected_directory(self):
        # Get the selected index from the QListView
        selected_index = self.view.currentIndex()
        if not selected_index.isValid():
            QMessageBox.warning(self, "No Selection", "Please select a layout from the list.")
            return
        
        selected_directory = self.model.data(selected_index)
        
        # Prevent deletion of the current layout
        if selected_directory == "Current Layout":
            QMessageBox.warning(self, "Invalid Operation", "Cannot delete the current layout.")
            return
        
        directory_path = os.path.join(self.user_layouts_dir, selected_directory)

        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Delete",
            f"Are you sure you want to delete the panel layout '{selected_directory}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                shutil.rmtree(directory_path)  # Delete the directory and its contents
                self.model.removeRow(selected_index.row())  # Remove the directory from the list view
            except PermissionError:
                QMessageBox.critical(self, "Permission Denied", f"Failed to delete directory: Permission denied.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete layout: {str(e)}")

    def rename_selected_directory(self):
        # Get the selected index from the QListView
        selected_index = self.view.currentIndex()
        if not selected_index.isValid():
            QMessageBox.warning(self, "No Selection", "Please select a layout from the list.")
            return
        
        selected_directory = self.model.data(selected_index)

        # Prevent renaming of the current layout
        if selected_directory == "Current Layout":
            QMessageBox.warning(self, "Invalid Operation", "Cannot rename the current layout.")
            return

        # Open a dialog to get the new name for the directory
        new_name, ok = QInputDialog.getText(self, "Rename Layout", "Enter new name:", text=selected_directory)

        if ok and new_name:
            # Ensure the new name is not empty
            if new_name.strip() == "":
                QMessageBox.warning(self, "Invalid Name", "Name cannot be empty.")
                return
            
            old_path = os.path.join(self.user_layouts_dir, selected_directory)
            new_path = os.path.join(self.user_layouts_dir, new_name)

            # Rename the directory
            try:
                os.rename(old_path, new_path)
                self.load_directories_with_panel_conf(self.user_layouts_dir)  # Reload the view
                QMessageBox.information(self, "Renamed", f"Layout renamed to '{new_name}'.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rename layout: {str(e)}")
                
                
    def save_current_layout(self):
        # Get the name for the new layout
        new_name, ok = QInputDialog.getText(self, "Save Current Layout", "Enter layout name:")

        if ok and new_name:
            # Ensure the new name is not empty and doesn't already exist
            new_name = new_name.strip()
            if not new_name:
                QMessageBox.warning(self, "Invalid Name", "Name cannot be empty.")
                return
            new_path = os.path.join(self.user_layouts_dir, new_name)

            if os.path.exists(new_path):
                QMessageBox.warning(self, "Duplicate Name", "A layout with this name already exists.")
                return

            try:
                # Create the new directory for the layout
                os.makedirs(new_path)

                # Copy the current layout (panel.conf) to the new directory
                current_layout_file = os.path.expanduser("~/.config/lxqt/panel.conf")
                shutil.copy(current_layout_file, os.path.join(new_path, "panel.conf"))

                # Reload the view to include the new layout
                self.load_directories_with_panel_conf(self.user_layouts_dir)

                QMessageBox.information(self, "Success", f"Current layout saved as '{new_name}'.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save layout: {str(e)}")


    def share_selected_directory(self):
        # Get the selected index from the QListView
        selected_index = self.view.currentIndex()
        if not selected_index.isValid():
            QMessageBox.warning(self, "No Selection", "Please select a layout from the list.")
            return
        
        selected_directory = self.model.data(selected_index)

        # Handle "Current Layout" specifically
        if selected_directory == "Current Layout":
            # Open a file dialog to select where to save the tar.gz file
            options = QFileDialog.Option(0)  # No specific options
            directory_to_share = os.path.expanduser("~/.config/lxqt/panel.conf")
        else:
            directory_to_share = os.path.join(self.user_layouts_dir, selected_directory)

        # Open a file dialog to select where to save the tar.gz file
        file_name, _ = QFileDialog.getSaveFileName(self, "Share Panel Layout", "", "Tar Files (*.tar.gz);;All Files (*)", options=options)

        if file_name:
            # Ensure the file name ends with .tar.gz
            if not file_name.endswith(".tar.gz"):
                file_name += ".tar.gz"

            # Create a new directory named after the file (without the extension)
            export_directory_name = os.path.basename(file_name[:-7])  # Strip '.tar.gz'
            export_directory_path = os.path.join(self.user_layouts_dir, export_directory_name)

            try:
                if not os.path.exists(export_directory_path):
                    os.makedirs(export_directory_path)  # Create the directory

                # Copy the current layout or selected layout into the new directory
                if selected_directory == "Current Layout":
                    shutil.copyfile(directory_to_share, os.path.join(export_directory_path, "panel.conf"))
                else:
                    shutil.copy(os.path.join(self.user_layouts_dir, selected_directory, "panel.conf"),
                                os.path.join(export_directory_path, "panel.conf"))

                # Create a tar.gz file from the new directory
                with tarfile.open(file_name, "w:gz") as tar:
                    tar.add(export_directory_path, arcname=os.path.basename(export_directory_path))

                QMessageBox.information(self, "Success", "Panel layout shared successfully!")

                # Cleanup: Remove the temporary directory
                shutil.rmtree(export_directory_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to share panel layout: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    viewer = FileListViewer()
    viewer.show()
    
    sys.exit(app.exec())
