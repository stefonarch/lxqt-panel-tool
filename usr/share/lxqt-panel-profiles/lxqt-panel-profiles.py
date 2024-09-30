from PyQt6.QtWidgets import QApplication, QListView, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMessageBox, QFileDialog, QInputDialog
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

        # Set up the main layout (vertical layout)
        self.main_layout = QVBoxLayout()

        # Create a NonEditableStringListModel
        self.model = NonEditableStringListModel()

        # Create a QListView and set the model
        self.view = QListView()
        self.view.setModel(self.model)

        # Add the QListView to the main layout
        self.main_layout.addWidget(self.view)

        # Auto-load directories from the specified path that contain a 'panel.conf' file
        self.user_layouts_dir = os.path.expanduser("~/.local/share/lxqt/layouts")
        self.load_directories_with_panel_conf(self.user_layouts_dir)

        # Create a horizontal layout for the buttons
        self.button_layout = QHBoxLayout()

        # Create five buttons
        self.button1 = QPushButton("Import")  # Import button
        self.button2 = QPushButton("Apply")  # Apply button
        self.button3 = QPushButton("Rename")  # Rename button
        self.button4 = QPushButton("Delete")  # Delete button
        self.button5 = QPushButton("Share")  # Share button

        # Connect the Import button to the import function
        self.button1.clicked.connect(self.import_panel_layout)

        # Connect the Apply button to the copy function
        self.button2.clicked.connect(self.copy_panel_conf)

        # Connect the Rename button to the rename function
        self.button3.clicked.connect(self.rename_selected_directory)

        # Connect the Delete button to the delete function
        self.button4.clicked.connect(self.delete_selected_directory)

        # Connect the Share button to the share function
        self.button5.clicked.connect(self.share_selected_directory)

        # Add buttons to the horizontal layout
        self.button_layout.addWidget(self.button1)
        self.button_layout.addWidget(self.button2)
        self.button_layout.addWidget(self.button3)
        self.button_layout.addWidget(self.button4)
        self.button_layout.addWidget(self.button5)

        # Add the button layout to the main layout (at the bottom)
        self.main_layout.addLayout(self.button_layout)

        # Create a Close button at the bottom
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)  # Connect to the close method
        self.main_layout.addWidget(self.close_button)  # Add Close button to the main layout

        # Set the layout to the window
        self.setLayout(self.main_layout)
        self.setWindowTitle("LXQt Panel Layouts")

    def load_directories_with_panel_conf(self, directory_path):
        # Use QDir to get a list of directories
        dir = QDir(directory_path)
        # List only directories (no files)
        dir.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)

        directories = dir.entryList()

        # Filter out directories that do not contain a 'panel.conf' file
        valid_directories = []
        for directory in directories:
            full_path = os.path.join(directory_path, directory)
            # Check if 'panel.conf' exists in the directory
            if os.path.exists(os.path.join(full_path, "panel.conf")):
                valid_directories.append(directory)

        # Add "Current Layout" as the first entry
        if "Current Layout" not in valid_directories:
            valid_directories.insert(0, "Current Layout")

        # Update the model with the list of valid directories
        self.model.setStringList(valid_directories)

    def import_panel_layout(self):
        # Open a file dialog to select a tar.gz file
        options = QFileDialog.Option(0)  # No specific options
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Panel Layout", "", "Tar Files (*.tar.gz);;All Files (*)", options=options)

        if file_name:
            # Extract the tar.gz file to the layouts directory
            try:
                with tarfile.open(file_name, "r:gz") as tar:
                    # Extract to user layouts directory
                    tar.extractall(path=self.user_layouts_dir)
                
                # Check if the extracted directory contains 'panel.conf'
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
                    QMessageBox.information(self, "Success", "Panel layout imported successfully!")
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
            subprocess.run("killall lxqt-panel && lxqt-panel &", shell=True, check=True)

            QMessageBox.information(self, "Success", "Panel Layout applied successfully.")
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
                QMessageBox.information(self, "Deleted", f"Panel Layout '{selected_directory}' has been deleted.")
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
    
    # Create an instance of the FileListViewer
    viewer = FileListViewer()
    viewer.show()
    
    # Run the application
    sys.exit(app.exec())
