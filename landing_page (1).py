import sys
import os
import shutil
import time

from PyQt5.QtWidgets import (
    QApplication, QWidget, QFrame, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFileDialog, QMessageBox, QProgressBar,
    QLineEdit, QComboBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

SCROLL_STYLE = """
QScrollArea {
    background-color: transparent;
    border: none;
}
QScrollBar:vertical {
    background: #E8EAF2; 
    width: 12px; 
    border-radius: 6px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: grey; 
    border-radius: 6px; 
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #555555; /* Darken handle on hover for tactile feedback */
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px; /* Hide the arrow buttons for a cleaner aesthetic */
}
"""

class logoScreen(QWidget):
    """
    The splash screen serves as the 'curtain raiser' for the application.
    By using FramelessWindowHint, we remove the ugly OS title bars,
    creating a floating, cinematic effect.
    """
    def __init__(self):
        super().__init__()

        self.setFixedSize(900, 900)
        
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("WELCOME")
        label.setFixedSize(800, 600)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            """
            background-color: black;
            border-radius: 30px;
            border: 2px solid #D4AF37;
            color: qlineargradient(
                spread:pad,
                x1:0, y1:0,
                x2:0, y2:1,
                stop:0 #FFD700,
                stop:1 #D4AF37
            );
            font-size: 80px;
            font-weight: bold;
            """
        )

        layout.addWidget(label)

class LoginPage(QWidget):
    """
    The main application interface. 
    Designed with a focus on 'Flow'—guiding the user from folder selection 
    to organization without unnecessary clicks.
    """
    def __init__(self):
        super().__init__()

        self.undo_stack = []
        

        self.category_rows = []

        # WINDOW CONFIGURATION
        self.setWindowTitle("Organize files")
        self.setFixedSize(800, 820)
        
        self.setStyleSheet("background-color: #E8EAF2;")

        # MAIN ARCHITECTURE
        # We use a vertical layout as the primary skeleton.
        self.main_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(SCROLL_STYLE)

        container = QWidget()
        container.setStyleSheet("background-color: #E8EAF2;")

        self.container_layout = QVBoxLayout(container)
        self.container_layout.setContentsMargins(40, 40, 40, 40)
        self.container_layout.setSpacing(25)

        self.build_header()            
        self.build_path_selector()      
        self.build_progress_bar()       
        self.build_description_panel() 
        self.build_custom_panel()     
        self.build_action_buttons()     
        self.build_undo_button()    

        scroll.setWidget(container)
        self.main_layout.addWidget(scroll)


    def build_header(self):
        """Creates the primary brand heading at the top of the interface."""
        title = QLabel("My File Organizer")
        # #121038 is a deep 'Space Blue'—it provides high contrast and authority.
        title.setStyleSheet(
            "font-size: 52px; font-weight: bold; color: #121038;"
        )
        self.container_layout.addWidget(
            title,
            alignment=Qt.AlignCenter
        )

    def build_path_selector(self):
        """Constructs the folder selection area."""
        row = QHBoxLayout()

        label = QLabel("File Path:")
        label.setStyleSheet(
            "font-size: 22px; color: #2b2b2b; font-weight: 500;"
        )


        self.dir_container = QPushButton(
            "C:/Users/Documents/Files"
        )
        self.dir_container.setFixedSize(450, 55)
        self.dir_container.setStyleSheet(
            """
            background-color: white;
            border-radius: 12px;
            border: 1px solid #dcdcdc;
            font-size: 16px;
            color: #555;
            text-align: left;
            padding-left: 15px;
            """
        )

        row.addStretch()
        row.addWidget(label)
        row.addWidget(self.dir_container)
        row.addStretch()

        self.container_layout.addLayout(row)

        # SELECT FOLDER BUTTON: The primary call to action.
        btn = QPushButton("Select Folder")
        btn.setFixedSize(250, 60)
        btn.setStyleSheet(
            """
            background-color: #2E7D32; /* Forest Green implies 'action' and 'safety' */
            border-radius: 12px;
            font-size: 22px;
            color: white;
            font-weight: bold;
            """
        )
        btn.clicked.connect(self.select_folder)

        self.container_layout.addWidget(
            btn,
            alignment=Qt.AlignCenter
        )

    def build_progress_bar(self):
        """Visual progress tracking is essential for long-running operations."""
        self.pbar = QProgressBar()
        self.pbar.setVisible(False)
        self.pbar.setFixedSize(650, 20)
        self.pbar.setStyleSheet(
            """
            QProgressBar {
                background: #ddd;
                border-radius: 10px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2E7D32;
                border-radius: 10px;
            }
            """
        )

        self.container_layout.addWidget(
            self.pbar,
            alignment=Qt.AlignCenter
        )

    def build_description_panel(self):
        """Provides the user with a quick guide on how to use the app."""
        frame = QFrame()
        frame.setFixedSize(650, 220)
        frame.setStyleSheet(
            "background-color: white; border-radius: 20px;"
        )
        # Shadows add a layer of 'Z-depth', making the frame 'pop' from the background.
        self.apply_shadow(frame)

        layout = QVBoxLayout(frame)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(SCROLL_STYLE)

        label = QLabel(
            "● Default Organization\n"
            "Automatically sorts into standard folders like Images, Docs, and Media. "
            "Perfect for a quick clean-up of your desktop or downloads folder.\n\n"
            "● Custom Organization (The Kini)\n"
            "Take full control. Define your own folder names and decide exactly "
            "which types of files should live there."
        )
        label.setWordWrap(True)
        label.setStyleSheet(
            "font-size: 16px; color: #444; padding: 15px;"
        )

        scroll.setWidget(label)
        layout.addWidget(scroll)

        self.container_layout.addWidget(
            frame,
            alignment=Qt.AlignCenter
        )

    def build_custom_panel(self):
        """
        THE KINI ENGINE:
        This panel is hidden by default. It contains the logic for creating 
        one-to-one mappings between folder names and file categories.
        """
        self.custom_panel = QFrame()
        self.custom_panel.setVisible(False) 
        self.custom_panel.setFixedSize(650, 240)
        self.custom_panel.setStyleSheet(
            "background-color: white; border-radius: 20px;"
        )
        self.apply_shadow(self.custom_panel)

        vbox = QVBoxLayout(self.custom_panel)

        # Internal scroll area for mapping rows
        self.rows_scroll = QScrollArea()
        self.rows_scroll.setWidgetResizable(True)
        self.rows_scroll.setStyleSheet(SCROLL_STYLE)

        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setAlignment(Qt.AlignTop)

        self.rows_scroll.setWidget(self.rows_container)


        add_btn = QPushButton("+ Add Mapping Rule")
        add_btn.setStyleSheet(
            "color: #121038; font-weight: bold; border: none; font-size: 14px;"
        )
        add_btn.clicked.connect(self.add_category_row)


        run_btn = QPushButton("Execute Custom Sort")
        run_btn.setStyleSheet(
            """
            background: #121038;
            color: white;
            font-weight: bold;
            height: 40px;
            border-radius: 10px;
            """
        )
        run_btn.clicked.connect(self.execute_custom_sort)

        vbox.addWidget(self.rows_scroll)
        vbox.addWidget(add_btn)
        vbox.addWidget(run_btn)

        self.container_layout.addWidget(
            self.custom_panel,
            alignment=Qt.AlignCenter
        )

    def build_action_buttons(self):
        """The main two modes of the application: Default or Custom."""
        row = QHBoxLayout()

        # DEFAULT MODE: For users who want the app to 'just handle it'.
        default_btn = QPushButton("Organize(Default)")
        default_btn.setFixedSize(260, 65)
        default_btn.setStyleSheet(
            """
            background-color: #2E7D32;
            border-radius: 12px;
            font-size: 20px;
            color: white;
            font-weight: bold;
            """
        )
        default_btn.clicked.connect(self.default_organize)

        # CUSTOM MODE: For users who have specific workflows.
        custom_btn = QPushButton("Organize(Custom)")
        custom_btn.setFixedSize(260, 65)
        custom_btn.setStyleSheet(
            """
            background-color: #121038;
            border-radius: 12px;
            font-size: 20px;
            color: white;
            font-weight: bold;
            """
        )
        custom_btn.clicked.connect(self.toggle_custom)

        row.addStretch()
        row.addWidget(default_btn)
        row.addWidget(custom_btn)
        row.addStretch()

        self.container_layout.addLayout(row)

    def build_undo_button(self):
        """The 'Time Machine' button—reverses the last organization run."""
        self.undo_btn = QPushButton("Undo Last Action")
        self.undo_btn.setVisible(False)
        self.undo_btn.setFixedSize(250, 45)
        self.undo_btn.setStyleSheet(
            """
            background-color: #B22222; /* Crimson Red for high visibility */
            border-radius: 10px;
            color: white;
            font-weight: bold;
            """
        )
        self.undo_btn.clicked.connect(self.undo_last_action)

        self.container_layout.addWidget(
            self.undo_btn,
            alignment=Qt.AlignCenter
        )

    # --------------------------------------------------------------------------
    # CORE LOGIC: THE BRAIN OF THE ORGANIZER
    # --------------------------------------------------------------------------

    def apply_shadow(self, widget):
        """
        Adds a soft drop shadow to a widget. 
        Shadows are essential in 'Material Design' to represent object hierarchy.
        """
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 60)) # Subtle alpha (60/255) for realism
        widget.setGraphicsEffect(shadow)

    def add_category_row(self):
        """
        Creates a new rule row dynamically. 
        This is a 'Kini'—allowing the user to map a name to a file type.
        """
        row = QWidget()
        layout = QHBoxLayout(row)

        # Input for the folder name
        name = QLineEdit()
        name.setPlaceholderText("New Folder Name...")
        name.setStyleSheet("background: #f9f9f9; padding: 5px; border-radius: 5px;")

        # Dropdown for file type selection
        combo = QComboBox()
        combo.addItems([
            "Documents", "Images", "Media",
            "Archives", "Executables",
            "Data", "Web"
        ])
        combo.setStyleSheet("background: #f9f9f9; padding: 5px; border-radius: 5px;")

        # Remove rule button
        remove = QPushButton("✕")
        remove.setFixedSize(30, 30)
        remove.setStyleSheet("color: red; font-weight: bold; background: transparent;")
        remove.clicked.connect(
            lambda: self.remove_row(row)
        )

        layout.addWidget(name)
        layout.addWidget(combo)
        layout.addWidget(remove)

        self.rows_layout.addWidget(row)
        
        # We store references so we can extract values during execution.
        self.category_rows.append(
            {"widget": row, "input": name, "combo": combo}
        )

    def remove_row(self, widget):
        """Cleans up the UI and the data structure when a rule is deleted."""
        for i, row in enumerate(self.category_rows):
            if row["widget"] is widget:
                widget.deleteLater() # Safely remove from GUI
                self.category_rows.pop(i) # Remove from logic
                break

    def toggle_custom(self):
        """Switches the custom panel on/off with basic logic to add a row if empty."""
        visible = not self.custom_panel.isVisible()
        self.custom_panel.setVisible(visible)
        
        # Friction reduction: If opening for the first time, give them a row to start with.
        if visible and not self.category_rows:
            self.add_category_row()

    def select_folder(self):
        """Native OS dialog for folder selection—ensures a familiar UX."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder to Organize"
        )
        if folder:
            self.dir_container.setText(folder)

    def default_organize(self):
        """Standard 'Clean-up' mode using a pre-defined extension map."""
        target = self.dir_container.text()
        if not os.path.exists(target):
            return

        # Our core extension dictionary. 
        # You can expand this with more extensions (.zip, .rar, .json, etc.)
        mapping = {
            "Documents": [".pdf", ".docx", ".txt", ".rtf", ".odt"],
            "Images": [".jpg", ".png", ".jpeg", ".gif", ".svg"],
            "Media": [".mp4", ".mp3", ".mov", ".wav", ".avi"]
        }
        self.run_sort(target, mapping)

    def execute_custom_sort(self):
        """Gathers user-defined rules and prepares them for the sorting engine."""
        target = self.dir_container.text()
        if not os.path.exists(target):
            return

        # Reference map for what 'Documents', 'Images', etc., actually mean.
        ext_map = {
            "Documents": [".pdf", ".docx", ".txt", ".xls", ".pptx"],
            "Images": [".jpg", ".png", ".webp", ".heic"],
            "Media": [".mp4", ".mp3", ".mkv", ".flac"],
            "Archives": [".zip", ".rar", ".7z", ".tar"],
            "Executables": [".exe", ".msi", ".bat", ".sh"],
            "Data": [".xlsx", ".csv", ".json", ".xml"],
            "Web": [".html", ".css", ".js", ".php"]
        }

        # List Comprehension to build the final instruction set.
        mapping = {
            row["input"].text().strip(): ext_map[row["combo"].currentText()]
            for row in self.category_rows
            if row["input"].text().strip()
        }

        if mapping:
            self.run_sort(target, mapping)
        else:
            QMessageBox.warning(self, "Input Required", "Please name your folders before sorting.")

    def run_sort(self, target, mapping):
        """
        THE SORTING ENGINE:
        This method performs the physical moving of files. 
        It is designed to be safe, creating directories only when needed, 
        and logging every move for the Undo functionality.
        """
        # Step 1: Identify all files in the directory (ignoring subfolders).
        files = [
            f for f in os.listdir(target)
            if os.path.isfile(os.path.join(target, f))
        ]

        if not files:
            QMessageBox.information(self, "All Clean", "No files found to organize!")
            return

        self.pbar.setVisible(True)
        self.pbar.setMaximum(len(files))

        # A list to store (destination, source) tuples for the Undo stack.
        moves = []

        # Step 2: Loop through files and match extensions against our mapping.
        for i, file in enumerate(files):
            ext = os.path.splitext(file)[1].lower()
            for folder, exts in mapping.items():
                if ext in exts:
                    dest = os.path.join(target, folder)
                    
                    # Ensure the sub-folder exists.
                    os.makedirs(dest, exist_ok=True)

                    src = os.path.join(target, file)
                    dst = os.path.join(dest, file)

                    # Logic to prevent overwriting: if a file exists, we could rename it,
                    # but here we simply move it.
                    try:
                        shutil.move(src, dst)
                        moves.append((dst, src))
                    except Exception as e:
                        print(f"Failed to move {file}: {e}")

            # Update the progress bar to keep the user informed.
            self.pbar.setValue(i + 1)
            
            # This is crucial: it prevents the GUI from 'freezing' 
            # while the OS is busy moving files.
            QApplication.processEvents()

        # Finalize the run.
        if moves:
            self.undo_stack.append(moves)
            self.undo_btn.setVisible(True)
            QMessageBox.information(self, "Done", f"Organized {len(moves)} files successfully!")
        
        self.pbar.setVisible(False)

    def undo_last_action(self):
        """
        The 'Ctrl+Z' for your file system. 
        Iterates through the last 'move log' and puts everything back.
        """
        if not self.undo_stack:
            return

        last_moves = self.undo_stack.pop()
        
        # We loop through the log in reverse to ensure file integrity.
        for new_location, old_location in last_moves:
            if os.path.exists(new_location):
                try:
                    shutil.move(new_location, old_location)
                except Exception as e:
                    print(f"Undo failed for {new_location}: {e}")

        # If there are no more actions left in the history, hide the button.
        if not self.undo_stack:
            self.undo_btn.setVisible(False)
            
        QMessageBox.information(self, "Undo Success", "Your files have been returned to the original path.")

if __name__ == "__main__":
    # Create the application instance.
    app = QApplication(sys.argv)

    # Launch the Splash Screen.
    splash = logoScreen()
    splash.show()

    # Pre-load the Main Window in the background.
    main = LoginPage()

    QTimer.singleShot(
        2500,
        lambda: (main.show(), splash.close())
    )

    # Start the event loop.
    sys.exit(app.exec_())
