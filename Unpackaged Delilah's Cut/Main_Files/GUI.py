# GUI Imports
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer, pyqtSlot
from PyQt6.QtWidgets import (
    QFrame,
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QStackedWidget,
    QPushButton,
    QSpinBox,
    QCheckBox,
    QSlider,
    QLineEdit,
    QTextEdit,
    QScrollArea,
    QMessageBox,
)
from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette

# Basic Library Imports
import sys
import os
import markdown
import json

# Other File imports
from Main_Files.processing import MRNA
from Main_Files.exclusion_and_scoring import *
from Main_Files.PDFresults import *
import Main_Files.settings as settings


def resource_path(relative_path):
    # When using PyInstaller, 'sys._MEIPASS' will hold the temp directory where resources are extracted
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class BackendThread(QThread):
    backend_finished = pyqtSignal()  # Signal to notify when backend is done

    def run(self):
        runBackend()  # This is your backend function
        self.backend_finished.emit()  # Emit signal when done


class MainWindow(QMainWindow):
    def __init__(self, basicNeedsDict, exclusionAndScoringDict):
        super().__init__()

        # Store the basic needs dictionary
        self.basicNeedsDict = basicNeedsDict
        self.exclusionAndScoringDict = exclusionAndScoringDict

        self.setWindowTitle("Delilah's Cut V1.1")

        self.setWindowIcon(QIcon(resource_path("Assets/Delilah's_Cut_Logo.png")))
        self.setGeometry(100, 100, 1200, 800)

        self.setupPalette()
        # Stacked Widget to manage different screens
        self.stackedWidget = QStackedWidget()

        # Create screens
        self.startUpWidget = self.createStartUpWidget()
        self.homeWidget = self.createHomeWidget()
        self.infoWidget = self.createInfoWidget()
        self.usageWidget = self.createUsageWidget()
        self.settingsScreen1 = self.createSettingsScreen1()

        self.stackedWidget.addWidget(self.startUpWidget)  # index 0
        self.stackedWidget.addWidget(self.homeWidget)  # index 1
        self.stackedWidget.addWidget(self.infoWidget)  # index 2
        self.stackedWidget.addWidget(self.usageWidget)  # index 3
        self.stackedWidget.addWidget(self.settingsScreen1)  # index 4

        # Set central widget
        self.setCentralWidget(self.stackedWidget)

        # Backend thread setup
        self.backend_thread = BackendThread()
        self.backend_thread.backend_finished.connect(self.on_backend_finished)

    def setupPalette(self):
        dark_color = QColor(33, 33, 33)  # Background and base color
        light_tan = QColor(245, 239, 229)  # Text color and tooltip base
        pastel_highlight = QColor(250, 215, 160)  # Highlight and tooltip text color
        checked_color = QColor(0, 150, 136)  # Teal for checked state (toggle buttons)
        unchecked_color = dark_color  # Background color for unchecked state
        checkbox_checked = QColor(
            250, 215, 160
        )  # Light pastel tan for checked checkboxes
        checkbox_unchecked = QColor(77, 77, 77)  # Dark grey for unchecked checkboxes

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, dark_color)
        palette.setColor(QPalette.ColorRole.WindowText, light_tan)
        palette.setColor(QPalette.ColorRole.Base, dark_color)
        palette.setColor(QPalette.ColorRole.AlternateBase, dark_color)
        palette.setColor(QPalette.ColorRole.ToolTipBase, light_tan)
        palette.setColor(QPalette.ColorRole.ToolTipText, light_tan)
        palette.setColor(QPalette.ColorRole.Text, light_tan)
        palette.setColor(QPalette.ColorRole.Button, dark_color)
        palette.setColor(QPalette.ColorRole.ButtonText, pastel_highlight)
        palette.setColor(QPalette.ColorRole.Highlight, pastel_highlight)
        palette.setColor(QPalette.ColorRole.HighlightedText, dark_color)
        self.setPalette(palette)

        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {unchecked_color.name()};
                color: #F5EFE5;
                border: 2px solid #FAD7A0;
                border-radius: 10px;
                padding: 8px;
            }}
            QPushButton:checked {{
                background-color: {checked_color.name()};
                color: #F5EFE5;
            }}
            QPushButton:hover {{
                background-color: #FAD7A0;
                color: #212121;
            }}
            QLabel {{
                color: #F5EFE5;
            }}
            QLineEdit, QTextEdit, QSpinBox, QSlider {{
                background-color: #333333;
                color: #F5EFE5;
                border: 1px solid #FAD7A0;
                border-radius: 5px;
            }}
            QCheckBox {{
                color: #F5EFE5;
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 1px solid #FAD7A0;
                background-color: {checkbox_unchecked.name()};
            }}
            QCheckBox::indicator:checked {{
                background-color: {checkbox_checked.name()};
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid #FAD7A0;
                background-color: #FAD7A0;
            }}
            QScrollArea {{
                border: none;
            }}
            """
        )

    @pyqtSlot()
    def on_backend_finished(self):
        # Generate the results screen and add it to the stacked widget
        self.createAndShowResultsScreen()
        self.stackedWidget.setCurrentIndex(
            self.stackedWidget.count() - 1
        )  # Go to results screen

    def beginBackend(self):
        self.backend_thread.start()  # Start the backend thread

    def updateSettingsDicts(self):

        settings.basicNeedsDict = self.basicNeedsDict
        settings.sequence_dict = self.sequence_dict
        settings.exclusionAndScoringDict = self.exclusionAndScoringDict

    def createAndShowResultsScreen(self):
        # Create the main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        main_widget.setLayout(main_layout)

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")

        # Create the content widget for the scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)
        content_widget.setLayout(content_layout)

        # Key information labels
        info_label = QLabel("Results of Analysis")
        info_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #FFFFFF;")
        content_layout.addWidget(info_label)

        # Display the reports
        reports = resultsReport

        for report in reports:
            for line in report:
                report_label = QLabel(line)
                report_label.setFont(QFont("Arial", 14))
                report_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                report_label.setWordWrap(True)
                # Apply color coding based on line content
                if "positive" in line.lower():
                    report_label.setStyleSheet("color: #4CAF50;")  # Green for positive
                elif "negative" in line.lower():
                    report_label.setStyleSheet("color: #F44336;")  # Red for negative
                else:
                    report_label.setStyleSheet("color: #FFFFFF;")  # White for neutral

                content_layout.addWidget(report_label)

        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)

        # Add the scroll area to the main layout with stretch
        main_layout.addWidget(scroll_area, stretch=9)

        # Create a horizontal layout for the buttons at the bottom
        button_layout = QHBoxLayout()

        # Add Exit Program button
        exit_button = QPushButton("Exit Program")
        exit_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        exit_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FAD7A0;
                color: #333333;
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
            """
        )
        exit_button.clicked.connect(QApplication.instance().quit)
        button_layout.addWidget(exit_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # Add Save as PDF button
        save_button = QPushButton("Save as PDF")
        save_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        save_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FAD7A0;
                color: #333333;
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
            """
        )
        save_button.clicked.connect(lambda: self.savePdfAndDisableButton(save_button))
        button_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Add the button layout to the main layout, sticking to the bottom
        main_layout.addStretch()
        main_layout.addLayout(button_layout, stretch=1)

        # Add the results screen to the stacked widget
        self.stackedWidget.addWidget(main_widget)
        self.stackedWidget.setCurrentWidget(main_widget)

    def savePdfAndDisableButton(self, button):
        # Generate the PDF
        pdf_name = settings.basicNeedsDict["OutputFileName"] + ".pdf"
        generate_results_pdf(resultsReport, pdf_name)

        # Update the button text and disable it
        button.setText("Saved to 'PDF_Outputs' Folder")
        button.setEnabled(False)
        button.setStyleSheet(
            """
            QPushButton {
                background-color: #B0BEC5;
                color: #333333;
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 10px;
            }
            """
        )

    def createLoadingScreen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)  # Add margins for better spacing
        layout.setSpacing(30)  # Add spacing between elements
        widget.setLayout(layout)

        # Loading Label
        loading_label = QLabel("Processing, please wait...")
        loading_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("color: #FAD7A0;")
        layout.addWidget(loading_label)

        # Add a loading spinner or animation (simple text-based for now)
        animation_label = QLabel("◴ ◷ ◶ ◵")
        animation_label.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        animation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        animation_label.setStyleSheet("color: #F5EFE5;")
        layout.addWidget(animation_label)

        # Timer for updating the spinner animation
        self.animation_index = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(
            lambda: self.updateAnimation(animation_label)
        )
        self.animation_timer.start(200)  # Change the spinner every 200ms

        return widget

    def updateAnimation(self, label):
        spinner_frames = ["◴", "◷", "◶", "◵"]
        self.animation_index = (self.animation_index + 1) % len(spinner_frames)
        label.setText(spinner_frames[self.animation_index])

    def processAndGoToNextSequenceScreen(self):
        # Process the cDNA vs mRNA choice again if needed
        self.basicNeedsDict["cDNA(T)/mRNA(F)"] = self.cDNAOptionInput.isChecked()

        # Retrieve the sequence and file name from input
        if self.basicNeedsDict["textFile(T)/CopyPasted(F)"] == False:
            sequence = self.sequenceInput.toPlainText()
            file_name = None
        else:
            sequence = None
            file_name = self.sequenceInputFileName.text().strip().lower()

        saveFileName = self.fileNameInput.text().strip()
        self.basicNeedsDict["OutputFileName"] = saveFileName

        # Create a dictionary to pass these values to the backend
        self.sequence_dict = {
            "sequence": sequence,
            "file_name": file_name,
            "RNAObjs": [],
        }
        # Send to backend
        self.updateSettingsDicts()

        allGood, ErrorMessages = self.runSequenceErrorChecks()

        if allGood == True:
            # Show loading screen and run backend
            self.stackedWidget.setCurrentWidget(self.loadingScreen)
            self.beginBackend()
        else:
            self.showSequenceErrors(ErrorMessages)

    def showSequenceErrors(self, errorMessages):
        # Create a list to store multiple error labels
        if not hasattr(self, "sequence_error_labels"):
            self.sequence_error_labels = []

        # Create and display each error message as a separate label
        for error in errorMessages:
            error_label = QLabel(error)
            error_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #FF6347;")  # Red color for the error

            # Insert the error message at the top of the layout
            layout = self.stackedWidget.currentWidget().layout()
            layout.insertWidget(0, error_label)

            # Add the error label to the list for tracking
            self.sequence_error_labels.append(error_label)

        # Scroll to the top to make sure the error is visible
        scroll_area = self.findChild(QScrollArea, "sequenceScrollArea")
        if scroll_area:
            scroll_area.verticalScrollBar().setValue(0)

        # Set a QTimer to remove all error messages after 10 seconds
        QTimer.singleShot(10000, self.clearSequenceErrorMessages)

    def clearSequenceErrorMessages(self):
        # Iterate over the list of error labels and remove them
        if hasattr(self, "sequence_error_labels"):
            for error_label in self.sequence_error_labels:
                error_label.deleteLater()

            # Clear the list after all labels are removed
            self.sequence_error_labels = []

    def runSequenceErrorChecks(self):
        allGood = True
        errorMessages = []

        # Checking Textfile Mode
        if self.basicNeedsDict["textFile(T)/CopyPasted(F)"] == True:
            if ".txt" in self.sequence_dict["file_name"]:
                pass
            else:
                allGood = False
                errorMessages.append(
                    "Input File Not a .txt, make sure to include .txt in the entry"
                )

            try:
                f = self.sequence_dict["file_name"]

                # Construct the path to the "Sequence_Inputs" directory in the parent directory
                path = get_input_file_path(f)

                with open(path, "r") as fil:
                    # Read file and remove newlines
                    test = fil.read().replace("\n", " ")
            except FileNotFoundError:
                allGood = False
                errorMessages.append(
                    "File not found in Sequence_Inputs Folder. Must be .txt and in correct location."
                )
        else:
            if self.sequence_dict["sequence"] == "":
                allGood = False
                errorMessages.append("Please input sequence.")

            if self.basicNeedsDict["cDNA(T)/mRNA(F)"] == True:
                if "u" in self.sequence_dict["sequence"]:
                    allGood = False
                    errorMessages.append(
                        "Sequence contains 'U', are you sure aren't checking mRNA?"
                    )
            else:
                if "t" in self.sequence_dict["sequence"]:
                    allGood = False
                    errorMessages.append(
                        "Sequence contains 'T', are you sure aren't checking cDNA?"
                    )

        if self.basicNeedsDict["OutputFileName"] == "":
            allGood = False
            errorMessages.append(
                "Please enter a name for the Output files, excluding filetypes"
            )
        else:
            for item in [
                ".",
                " ",
                "'",
                '"',
            ]:
                if item in self.basicNeedsDict["OutputFileName"]:
                    allGood = False
                    errorMessages.append(
                        "Improper Character in OutputFileName: " + item
                    )
        return allGood, errorMessages

    def createSequenceInputScreen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)  # Add margins for better spacing
        layout.setSpacing(30)  # Space between elements
        widget.setLayout(layout)

        # Title Block
        title_label = QLabel("Sequence Input")
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FAD7A0;")
        layout.addWidget(title_label)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #FAD7A0;")
        layout.addWidget(separator)

        # Dynamic Instructions and Input
        if not self.basicNeedsDict["textFile(T)/CopyPasted(F)"]:
            instructions_text = (
                "Please enter the sequence you wish to analyze and specify a file name to save the results. "
                "\nAnything not a base (AGC and T/U) in entry box will be ignored by program."
                "\nMake sure to review the cDNA vs mRNA option if necessary."
            )
            sequence_widget = self.createSequenceTextInput()
        else:
            instructions_text = (
                "Please enter the filename (must be a .txt placed in the 'Input_Files' folder) in order to retrieve sequence."
                "\nINCLUDE the .txt in your entry. "
                "Sequence can be either mRNA or cDNA as specified by the checkbox below."
            )
            sequence_widget = self.createSequenceFileInput()

        # Instructions Block
        instructions_label = QLabel(instructions_text)
        instructions_label.setFont(QFont("Arial", 16))
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        instructions_label.setWordWrap(True)
        instructions_label.setStyleSheet("color: #F5EFE5;")
        layout.addWidget(instructions_label)

        layout.addWidget(sequence_widget)

        # cDNA or mRNA Checkbox
        self.cDNAOptionInput = QCheckBox("Is this sequence cDNA? (Unchecked = mRNA)")
        self.cDNAOptionInput.setChecked(self.basicNeedsDict["cDNA(T)/mRNA(F)"])
        self.cDNAOptionInput.setFont(QFont("Arial", 16))
        self.cDNAOptionInput.setStyleSheet(
            """
            QCheckBox {
                color: #F5EFE5;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid #FAD7A0;
                background-color: #333333;
            }
            QCheckBox::indicator:checked {
                background-color: #FAD7A0;
                border: 2px solid #FAD7A0;
            }
            """
        )
        self.cDNAOptionInput.stateChanged.connect(self.togglecDNAOptionInput)
        layout.addWidget(self.cDNAOptionInput)

        # File Name Input Block
        self.fileNameInput = QLineEdit()
        self.fileNameInput.setPlaceholderText(
            "Enter Run Title Here (Exclude spaces, periods, commas, quotes)"
        )
        self.fileNameInput.setFont(QFont("Arial", 14))
        self.fileNameInput.setStyleSheet(
            "background-color: #333333; color: #F5EFE5; border: 1px solid #FAD7A0; border-radius: 5px;"
        )
        layout.addWidget(
            self.createLabeledWidget(
                "Run Name (used to name files):", self.fileNameInput
            )
        )

        # Add some space between the input fields and the button
        layout.addStretch()

        # Next Button centered and updated
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Add space to the left of the button

        next_button = QPushButton("Begin Generating siRNAs")
        next_button.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        next_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FAD7A0;
                color: #333333;
                border: 2px solid #333333;
                border-radius: 15px;
                padding: 15px 25px;  /* Increased padding for a larger button */
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
            """
        )
        next_button.clicked.connect(self.processAndGoToNextSequenceScreen)
        button_layout.addWidget(next_button)

        button_layout.addStretch()  # Add space to the right of the button
        layout.addLayout(button_layout)

        return widget

    def createSequenceTextInput(self):
        """Create the input section for directly entered sequences."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        widget.setLayout(layout)

        self.sequenceInput = QTextEdit()
        self.sequenceInput.setPlaceholderText("Enter your sequence here")
        self.sequenceInput.setFixedHeight(150)
        self.sequenceInput.setFont(QFont("Arial", 14))
        self.sequenceInput.setStyleSheet(
            "background-color: #333333; color: #F5EFE5; border: 1px solid #FAD7A0; border-radius: 5px;"
        )
        layout.addWidget(self.createLabeledWidget("Sequence:", self.sequenceInput))

        return widget

    def createSequenceFileInput(self):
        """Create the input section for loading sequences from a file."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        widget.setLayout(layout)

        self.sequenceInputFileName = QLineEdit()
        self.sequenceInputFileName.setPlaceholderText(
            "Enter the file name of your sequence."
        )
        self.sequenceInputFileName.setFont(QFont("Arial", 14))
        self.sequenceInputFileName.setStyleSheet(
            "background-color: #333333; color: #F5EFE5; border: 1px solid #FAD7A0; border-radius: 5px;"
        )
        layout.addWidget(
            self.createLabeledWidget(
                "Sequence file name (include .txt):", self.sequenceInputFileName
            )
        )

        return widget

    def togglecDNAOptionInput(self):
        self.basicNeedsDict["cDNA(T)/mRNA(F)"] = self.cDNAOptionInput.isChecked()

    def showNextSettingsScreen(self):
        next_index = self.stackedWidget.currentIndex() + 1
        self.stackedWidget.setCurrentIndex(next_index)

    def updateInputFromSlider(self, key, value):
        self.inputs[key].setText(str(value))

    def updateSliderFromInput(self, key, value):
        if value.isdigit():
            self.sliders[key].setValue(int(value))

    def processAndGoToNextSettingsScreen2(self):
        # Update the exclusionary settings in the dict and move to the next screen
        for key, checkbox in self.checkboxes.items():
            for param in self.exclusionAndScoringDict:
                if param["propName"] == key:
                    param["exclusionary"] = checkbox.isChecked()

        self.settingsScreen3 = self.createSettingsScreen3()
        self.stackedWidget.addWidget(self.settingsScreen3)  # index 6

        self.stackedWidget.setCurrentIndex(6)

    def processAndGoToNextSettingsScreen3(self):
        # Update the score values in the dict and complete the settings process
        for key, slider in self.sliders.items():
            for param in self.exclusionAndScoringDict:
                if param["propName"] == key:
                    param["scoreVal"] = slider.value()

        # Create and add the sequence input screen dynamically at index 7
        self.sequenceInputScreen = self.createSequenceInputScreen()
        self.stackedWidget.addWidget(self.sequenceInputScreen)  # index 7

        # Create loading Screen and at at index 8
        self.loadingScreen = self.createLoadingScreen()
        self.stackedWidget.addWidget(self.loadingScreen)  # index 6

        # Navigate to the sequence input screen
        self.stackedWidget.setCurrentIndex(7)

    def createSettingsScreen3(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")  # Clean look

        # Main container widget and layout
        container_widget = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(50, 50, 50, 50)
        container_layout.setSpacing(20)
        container_widget.setLayout(container_layout)

        # Title
        title_label = QLabel("Settings - Scoring Parameters")
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FAD7A0;")
        container_layout.addWidget(title_label)

        # Introduction/Instruction
        intro_label = QLabel(
            "Adjust the scoring parameters to fine-tune how different RNA sequences are evaluated."
        )
        intro_label.setFont(QFont("Arial", 16))
        intro_label.setStyleSheet("color: #F5EFE5;")
        intro_label.setWordWrap(True)
        container_layout.addWidget(intro_label)

        self.sliders = {}
        self.inputs = {}

        # Add sliders and inputs for non-exclusionary parameters
        for param in self.exclusionAndScoringDict:
            if not param["exclusionary"]:
                # Question label and scoring info
                question_layout = QHBoxLayout()
                question_label = QLabel(param["question"])
                question_label.setFont(QFont("Arial", 18))
                question_label.setStyleSheet("color: #F5EFE5;")
                question_layout.addWidget(question_label)

                # Scoring info based on wantedVal
                scoring_info = "Scores if " + (
                    "True" if param["wantedVal"] else "False"
                )
                scoring_label = QLabel(f"({scoring_info})")
                scoring_label.setFont(QFont("Arial", 14))
                scoring_label.setStyleSheet("color: #FAD7A0;")
                question_layout.addWidget(scoring_label)

                question_layout.addStretch()  # Add spacing to the right of the scoring label
                container_layout.addLayout(question_layout)

                slider_layout = QHBoxLayout()

                # Replace the slider creation with NoScrollSlider
                slider = NoScrollSlider(Qt.Orientation.Horizontal)
                slider.setRange(0, 500)
                slider.setValue(param["scoreVal"])
                slider.setSingleStep(1)
                slider.setStyleSheet(
                    """
                    QSlider::groove:horizontal {
                        border: 1px solid #FAD7A0;
                        height: 8px;
                        background: #333333;
                        margin: 2px 0;
                        border-radius: 4px;
                    }
                    QSlider::handle:horizontal {
                        background: #FAD7A0;
                        border: 2px solid #FAD7A0;
                        width: 18px;
                        height: 18px;
                        margin: -8px 0;
                        border-radius: 9px;
                    }
                    """
                )
                slider.setFocusPolicy(
                    Qt.FocusPolicy.NoFocus
                )  # Disable focus to prevent wheel interaction
                self.sliders[param["propName"]] = slider
                slider_layout.addWidget(slider)

                # Input box
                input_box = QLineEdit()
                input_box.setFixedWidth(50)
                input_box.setText(str(param["scoreVal"]))
                input_box.setFont(QFont("Arial", 16))
                input_box.setStyleSheet(
                    """
                    QLineEdit {
                        background-color: #333333;
                        color: #F5EFE5;
                        border: 1px solid #FAD7A0;
                        border-radius: 5px;
                        padding: 4px;
                    }
                    """
                )
                self.inputs[param["propName"]] = input_box
                slider_layout.addWidget(input_box)

                container_layout.addLayout(slider_layout)

                # Connect the slider and input box
                slider.valueChanged.connect(
                    lambda value, key=param["propName"]: self.updateInputFromSlider(
                        key, value
                    )
                )
                input_box.textChanged.connect(
                    lambda value, key=param["propName"]: self.updateSliderFromInput(
                        key, value
                    )
                )

        # Next button
        next_button = QPushButton("Next")
        next_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        next_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FAD7A0;
                color: #333333;
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
            """
        )
        next_button.clicked.connect(self.processAndGoToNextSettingsScreen3)
        container_layout.addWidget(next_button)

        # Set the container widget as the scrollable area
        scroll_area.setWidget(container_widget)

        return scroll_area

    def createSettingsScreen2(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")  # Remove border for a clean look

        # Main container widget and layout
        container_widget = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(50, 50, 50, 50)
        container_layout.setSpacing(20)
        container_widget.setLayout(container_layout)

        # Title
        title_label = QLabel("Settings - Exclusionary Parameters")
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FAD7A0;")
        container_layout.addWidget(title_label)

        # Introduction/Instruction
        intro_label = QLabel(
            "Below are the exclusionary parameters for your siRNA design. "
            "Adjust them as needed to refine your analysis."
        )
        intro_label.setFont(QFont("Arial", 16))
        intro_label.setStyleSheet("color: #F5EFE5;")
        intro_label.setWordWrap(True)
        container_layout.addWidget(intro_label)

        self.checkboxes = {}

        # Separate parameters into initially exclusionary and non-exclusionary
        initiallyExc = []
        initiallyNonexc = []
        for parameter in self.exclusionAndScoringDict:
            if parameter["exclusionary"]:
                initiallyExc.append(parameter)
            else:
                initiallyNonexc.append(parameter)

        paramOrder = initiallyExc
        paramOrder.extend(initiallyNonexc)

        # Display initially exclusionary parameters with "excluded if" message
        for param in paramOrder:
            question_label = QLabel(param["question"])
            question_label.setFont(QFont("Arial", 18))
            question_label.setStyleSheet("color: #F5EFE5;")
            container_layout.addWidget(question_label)

            excluded_label_font = QFont("Arial", 14)
            excluded_label_font.setItalic(True)
            excluded_label = QLabel(
                f"Excluded if {'False' if param['wantedVal'] else 'True'}"
            )
            excluded_label.setFont(excluded_label_font)
            excluded_label.setStyleSheet("color: #FAD7A0;")
            container_layout.addWidget(excluded_label)

            checkbox = QCheckBox("Exclusionary")
            checkbox.setChecked(param["exclusionary"])
            checkbox.setFont(QFont("Arial", 16))
            checkbox.setStyleSheet(
                """
                QCheckBox {
                    color: #F5EFE5;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    border: 2px solid #FAD7A0;
                    background-color: #333333;
                }
                QCheckBox::indicator:checked {
                    background-color: #FAD7A0;
                    border: 2px solid #FAD7A0;
                }
                """
            )
            self.checkboxes[param["propName"]] = checkbox
            container_layout.addWidget(checkbox)

        # Next button
        next_button = QPushButton("Next")
        next_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        next_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FAD7A0;
                color: #333333;
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
            """
        )
        next_button.clicked.connect(self.processAndGoToNextSettingsScreen2)
        container_layout.addWidget(next_button)

        # Set the container widget as the scrollable area
        scroll_area.setWidget(container_widget)

        return scroll_area

    def createSettingsScreen1(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        widget.setLayout(layout)

        # Add a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")

        # Create a container widget for the scroll area
        container_widget = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(20)
        container_widget.setLayout(container_layout)

        # Title
        title_label = QLabel("Settings - Basic Parameters")
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FAD7A0;")
        container_layout.addWidget(title_label)

        # Load settings label and button
        load_label = QLabel("Would you like to load settings from a previous run?")
        load_label.setFont(QFont("Arial", 16))
        load_label.setStyleSheet("color: #F5EFE5;")
        container_layout.addWidget(load_label)

        self.loadSettingsButton = QPushButton("No", checkable=True, checked=False)
        self.loadSettingsButton.setFont(QFont("Arial", 18))
        self.loadSettingsButton.setStyleSheet(
            """
            QPushButton {
                background-color: #333333;
                color: #FAD7A0;
                border: 2px solid #FAD7A0;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:checked {
                background-color: #FAD7A0;
                color: #333333;
            }
            """
        )
        self.loadSettingsButton.clicked.connect(self.toggleLoadSettings)
        container_layout.addWidget(self.loadSettingsButton)

        # Hidden section for loading settings
        self.loadSettingsSection = QWidget()
        load_settings_layout = QVBoxLayout()
        self.loadSettingsSection.setLayout(load_settings_layout)
        self.loadSettingsSection.setVisible(False)

        file_name_label = QLabel("Enter the file name to load settings:")
        file_name_label.setFont(QFont("Arial", 16))
        file_name_label.setStyleSheet("color: #F5EFE5;")
        load_settings_layout.addWidget(file_name_label)

        self.fileNameInput = QLineEdit()
        self.fileNameInput.setPlaceholderText("Enter file name without extension")
        self.fileNameInput.setFont(QFont("Arial", 14))
        self.fileNameInput.setStyleSheet(
            "background-color: #333333; color: #F5EFE5; border: 1px solid #FAD7A0; border-radius: 5px;"
        )
        load_settings_layout.addWidget(self.fileNameInput)

        # Buttons for loading settings
        button_layout = QHBoxLayout()
        self.load_all_button = QPushButton("Load All Settings")
        self.load_all_button.setFont(QFont("Arial", 16))
        self.load_all_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FAD7A0;
                color: #333333;
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
            """
        )
        self.load_all_button.clicked.connect(self.loadAllSettings)
        button_layout.addWidget(self.load_all_button)

        self.load_scoring_button = QPushButton("Load Scoring and Exclusion")
        self.load_scoring_button.setFont(QFont("Arial", 16))
        self.load_scoring_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FAD7A0;
                color: #333333;
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
            """
        )
        self.load_scoring_button.clicked.connect(self.loadScoringAndExclusionSettings)
        button_layout.addWidget(self.load_scoring_button)

        load_settings_layout.addLayout(button_layout)
        container_layout.addWidget(self.loadSettingsSection)

        # Description for TextFile(T)/CopyPasted(F)
        desc_label = QLabel(
            "Choose between using a text file or directly inputting your sequence."
        )
        desc_label.setFont(QFont("Arial", 16))
        desc_label.setStyleSheet("color: #F5EFE5;")
        container_layout.addWidget(desc_label)

        # TextFile(T)/CopyPasted(F)
        self.textFileOption = QPushButton(
            "Direct Input",
            checkable=True,
            checked=self.basicNeedsDict["textFile(T)/CopyPasted(F)"],
        )
        self.textFileOption.setFont(QFont("Arial", 18))
        self.textFileOption.setStyleSheet(
            """
            QPushButton {
                background-color: #333333;
                color: #FAD7A0;
                border: 2px solid #FAD7A0;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:checked {
                background-color: #FAD7A0;
                color: #333333;
            }
            """
        )
        self.textFileOption.clicked.connect(self.toggleTextFileOption)
        container_layout.addWidget(self.textFileOption)

        # Description for cDNA(T)/mRNA(F)
        desc_label = QLabel("Select whether your input is cDNA or mRNA.")
        desc_label.setFont(QFont("Arial", 16))
        desc_label.setStyleSheet("color: #F5EFE5;")
        container_layout.addWidget(desc_label)

        # cDNA(T)/mRNA(F)
        self.cDNAOption = QPushButton(
            "cDNA (Containing T)",
            checkable=True,
            checked=self.basicNeedsDict["cDNA(T)/mRNA(F)"],
        )
        self.cDNAOption.setFont(QFont("Arial", 18))
        self.cDNAOption.setStyleSheet(
            """
            QPushButton {
                background-color: #333333;
                color: #FAD7A0;
                border: 2px solid #FAD7A0;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:checked {
                background-color: #FAD7A0;
                color: #333333;
            }
            """
        )
        self.cDNAOption.clicked.connect(self.togglecDNAOption)
        container_layout.addWidget(self.cDNAOption)

        # Description for Min Length
        desc_label = QLabel("Set the minimum length of the RNA sequences generated.")
        desc_label.setFont(QFont("Arial", 16))
        desc_label.setStyleSheet("color: #F5EFE5;")
        container_layout.addWidget(desc_label)

        # Min Length
        self.minLengthInput = QSpinBox()
        self.minLengthInput.setRange(1, 100)
        self.minLengthInput.setValue(self.basicNeedsDict["minLengthChecked"])
        self.minLengthInput.setFixedSize(200, 50)  # Increased width and height
        self.minLengthInput.setStyleSheet(
            """
            QSpinBox {
                padding-right: 30px;
                font-size: 18px;
                height: 40px;
                border: 2px solid #FAD7A0;
                border-radius: 5px;
                background-color: #333333;
                color: #F5EFE5;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 25px;
                height: 25px;
            }
            """
        )
        self.minLengthInput.valueChanged.connect(self.updateMinLength)
        container_layout.addWidget(
            self.createLabeledWidget("Minimum Length", self.minLengthInput)
        )

        # Description for Max Length
        desc_label = QLabel("Set the maximum length of the RNA sequences generated.")
        desc_label.setFont(QFont("Arial", 16))
        desc_label.setStyleSheet("color: #F5EFE5;")
        container_layout.addWidget(desc_label)

        # Max Length
        self.maxLengthInput = QSpinBox()
        self.maxLengthInput.setRange(1, 100)
        self.maxLengthInput.setValue(self.basicNeedsDict["maxLengthCHecked"])
        self.maxLengthInput.setFixedSize(200, 50)  # Increased width and height
        self.maxLengthInput.setStyleSheet(
            """
            QSpinBox {
                padding-right: 30px;
                font-size: 18px;
                height: 40px;
                border: 2px solid #FAD7A0;
                border-radius: 5px;
                background-color: #333333;
                color: #F5EFE5;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 25px;
                height: 25px;
            }
            """
        )
        self.maxLengthInput.valueChanged.connect(self.updateMaxLength)
        container_layout.addWidget(
            self.createLabeledWidget("Maximum Length", self.maxLengthInput)
        )

        # Description for How Many RNA Output
        desc_label = QLabel(
            "Specify how many of the top-ranked siRNAs you would like to see."
        )
        desc_label.setFont(QFont("Arial", 16))
        desc_label.setStyleSheet("color: #F5EFE5;")
        container_layout.addWidget(desc_label)

        # How Many RNA Output
        self.howManyRNAInput = QSpinBox()
        self.howManyRNAInput.setRange(1, 100)
        self.howManyRNAInput.setValue(self.basicNeedsDict["HowManyRNAOutput"])
        self.howManyRNAInput.setFixedSize(200, 50)  # Increased width and height
        self.howManyRNAInput.setStyleSheet(
            """
            QSpinBox {
                padding-right: 30px;
                font-size: 18px;
                height: 40px;
                border: 2px solid #FAD7A0;
                border-radius: 5px;
                background-color: #333333;
                color: #F5EFE5;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 25px;
                height: 25px;
            }
            """
        )
        self.howManyRNAInput.valueChanged.connect(self.updateHowManyRNAOutput)
        container_layout.addWidget(
            self.createLabeledWidget("How Many RNA Outputs", self.howManyRNAInput)
        )

        # Description for Run Default Parameters
        desc_label = QLabel(
            "Would you like to use current exclusion and scoring parameters? (Default Unless Settings Loaded)"
        )
        desc_label.setFont(QFont("Arial", 16))
        desc_label.setStyleSheet("color: #F5EFE5;")
        container_layout.addWidget(desc_label)

        # Run Default Parameters
        self.runDefaultOption = QPushButton(
            "Run Current Parameters",
            checkable=True,
            checked=self.basicNeedsDict["RunDefaultParam"],
        )
        self.runDefaultOption.setFont(QFont("Arial", 18))
        self.runDefaultOption.setStyleSheet(
            """
            QPushButton {
                background-color: #333333;
                color: #FAD7A0;
                border: 2px solid #FAD7A0;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:checked {
                background-color: #FAD7A0;
                color: #333333;
            }
            """
        )
        self.runDefaultOption.clicked.connect(self.toggleRunDefaultOption)
        container_layout.addWidget(self.runDefaultOption)

        # Description for Save Settings
        desc_label = QLabel("Would you like to save these settings for future use?")
        desc_label.setFont(QFont("Arial", 16))
        desc_label.setStyleSheet("color: #F5EFE5;")
        container_layout.addWidget(desc_label)

        # Save Settings
        self.saveSettingsOption = QPushButton(
            "Save Settings",
            checkable=True,
            checked=self.basicNeedsDict["saveSettings"],
        )
        self.saveSettingsOption.setFont(QFont("Arial", 18))
        self.saveSettingsOption.setStyleSheet(
            """
            QPushButton {
                background-color: #333333;
                color: #FAD7A0;
                border: 2px solid #FAD7A0;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:checked {
                background-color: #FAD7A0;
                color: #333333;
            }
            """
        )
        self.saveSettingsOption.clicked.connect(self.toggleSaveSettingsOption)
        container_layout.addWidget(self.saveSettingsOption)

        # Next button
        next_button = QPushButton("Next")
        next_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        next_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FAD7A0;
                color: #333333;
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
            """
        )
        next_button.clicked.connect(self.processAndGoToNextSettingsScreen)
        container_layout.addWidget(next_button)

        # Add the container widget to the scroll area
        scroll_area.setWidget(container_widget)

        # Add the scroll area to the main layout
        layout.addWidget(scroll_area)

        return widget

    def toggleLoadSettings(self):
        self.loadSettingsSection.setVisible(self.loadSettingsButton.isChecked())
        self.loadSettingsButton.setText(
            "Yes" if self.loadSettingsButton.isChecked() else "No"
        )

    def loadAllSettings(self):

        fileName = self.fileNameInput.text().strip()

        # Get the path of the parent directory ("Delilah's Cut")

        if fileName:
            if ".json" not in fileName:
                fileName += ".json"

            # Get the full path to the settings file in 'Saved_Settings'
            path = get_settings_file_path(fileName)

            if os.path.exists(path):
                with open(path, "r") as file:
                    data = json.load(file)
                    self.basicNeedsDict.update(data.get("basicNeedsDict", {}))
                    self.exclusionAndScoringDict = data.get(
                        "exclusionAndScoringDict", []
                    )
                    self.updateUIFromSettings()
                self.load_all_button.setText("Loaded!")
                self.load_all_button.setEnabled(False)
            else:
                self.showSettingsErrors1(
                    ["File not found. Please check the file name and try again."]
                )

    def loadScoringAndExclusionSettings(self):
        fileName = self.fileNameInput.text().strip()
        if fileName:
            if ".json" not in fileName:
                fileName += ".json"

            # Get the full path to the settings file in 'Saved_Settings'
            path = get_settings_file_path(fileName)

            if os.path.exists(path):
                with open(path, "r") as file:
                    data = json.load(file)
                    self.exclusionAndScoringDict = data.get(
                        "exclusionAndScoringDict", []
                    )
                    self.updateUIFromSettings()
                self.load_scoring_button.setText("Loaded!")
                self.load_scoring_button.setEnabled(False)
            else:
                self.showSettingsErrors1(
                    ["File not found. Please check the file name and try again."]
                )

    def updateUIFromSettings(self):
        # Update basic settings
        self.textFileOption.setChecked(self.basicNeedsDict["textFile(T)/CopyPasted(F)"])
        self.textFileOption.setText(
            "Text File"
            if self.basicNeedsDict["textFile(T)/CopyPasted(F)"]
            else "Direct Input"
        )

        self.cDNAOption.setChecked(self.basicNeedsDict["cDNA(T)/mRNA(F)"])
        self.cDNAOption.setText(
            "cDNA (Containing T)"
            if self.basicNeedsDict["cDNA(T)/mRNA(F)"]
            else "mRNA (Containing U)"
        )

        self.minLengthInput.setValue(self.basicNeedsDict["minLengthChecked"])
        self.maxLengthInput.setValue(self.basicNeedsDict["maxLengthCHecked"])
        self.howManyRNAInput.setValue(self.basicNeedsDict["HowManyRNAOutput"])

        self.runDefaultOption.setChecked(self.basicNeedsDict["RunDefaultParam"])
        self.saveSettingsOption.setChecked(self.basicNeedsDict["saveSettings"])

        # Update exclusion and scoring settings
        if hasattr(self, "checkboxes") and hasattr(self, "sliders"):
            for param in self.exclusionAndScoringDict:
                if param["exclusionary"]:
                    if param["propName"] in self.checkboxes:
                        self.checkboxes[param["propName"]].setChecked(
                            param["exclusionary"]
                        )
                else:
                    if param["propName"] in self.sliders:
                        self.sliders[param["propName"]].setValue(param["scoreVal"])
                        self.inputs[param["propName"]].setText(str(param["scoreVal"]))

    def updateMinLength(self, value):
        self.basicNeedsDict["minLengthChecked"] = value

    def updateMaxLength(self, value):
        self.basicNeedsDict["maxLengthCHecked"] = value

    def updateHowManyRNAOutput(self, value):
        self.basicNeedsDict["HowManyRNAOutput"] = value

    def createLabeledWidget(self, label_text, widget):
        container = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(10)
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 16))
        label.setStyleSheet("color: #F5EFE5;")
        layout.addWidget(label)
        layout.addWidget(widget)
        container.setLayout(layout)
        return container

    def showNextSettingsScreen(self):
        next_index = self.stackedWidget.currentIndex() + 1
        self.stackedWidget.setCurrentIndex(next_index)

    def toggleTextFileOption(self):
        self.basicNeedsDict["textFile(T)/CopyPasted(F)"] = not self.basicNeedsDict[
            "textFile(T)/CopyPasted(F)"
        ]
        self.textFileOption.setText(
            "Text File"
            if self.basicNeedsDict["textFile(T)/CopyPasted(F)"]
            else "Direct Input"
        )

    def togglecDNAOption(self):
        self.basicNeedsDict["cDNA(T)/mRNA(F)"] = not self.basicNeedsDict[
            "cDNA(T)/mRNA(F)"
        ]
        self.cDNAOption.setText(
            "cDNA (Containing T)"
            if self.basicNeedsDict["cDNA(T)/mRNA(F)"]
            else "mRNA (Containing U)"
        )

    def toggleRunDefaultOption(self):
        self.basicNeedsDict["RunDefaultParam"] = not self.basicNeedsDict[
            "RunDefaultParam"
        ]

    def toggleSaveSettingsOption(self):
        self.basicNeedsDict["saveSettings"] = not self.basicNeedsDict["saveSettings"]

    def processAndGoToNextSettingsScreen(self):
        self.basicNeedsDict["minLengthChecked"] = self.minLengthInput.value()
        self.basicNeedsDict["maxLengthCHecked"] = self.maxLengthInput.value()
        self.basicNeedsDict["HowManyRNAOutput"] = self.howManyRNAInput.value()

        allGood, ErrorMessage = self.runChecksOnSettings1()
        if allGood == True:

            self.settingsScreen2 = self.createSettingsScreen2()
            self.stackedWidget.addWidget(self.settingsScreen2)  # index 5
            if self.basicNeedsDict["RunDefaultParam"] == False:
                self.showNextSettingsScreen()
            else:
                self.skipToSequenceInput()
        else:
            self.showSettingsErrors1(ErrorMessage)

    def showSettingsErrors1(self, errorMessages):
        # Create a list to store multiple error labels
        if not hasattr(self, "settings_error_labels"):
            self.settings_error_labels = []

        # Create and display each error message as a separate label
        for error in errorMessages:
            error_label = QLabel("Error: " + error)
            error_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #FF6347;")  # Red color for the error

            # Insert the error message at the top of the layout
            layout = self.stackedWidget.currentWidget().layout()
            layout.insertWidget(0, error_label)

            # Add the error label to the list for tracking
            self.settings_error_labels.append(error_label)

        # Optionally, scroll to the top of the screen to make sure the error is visible
        scroll_area = self.findChild(QScrollArea, "settingsScrollArea")
        if scroll_area:
            scroll_area.verticalScrollBar().setValue(0)

        # Set a QTimer to remove all error messages after 10 seconds
        QTimer.singleShot(10000, self.clearErrorMessage)

    def clearErrorMessage(self):
        # Iterate over the list of error labels and remove them
        if hasattr(self, "settings_error_labels"):
            for error_label in self.settings_error_labels:
                error_label.deleteLater()

            # Clear the list after all labels are removed
            self.settings_error_labels = []

    def runChecksOnSettings1(self):
        allGood = True
        settingsErrors = []
        if (
            self.basicNeedsDict["minLengthChecked"]
            > self.basicNeedsDict["maxLengthCHecked"]
        ):
            settingsErrors.append("Minimum Length Must be shorter than Maximum Length")
            allGood = False
        return (allGood, settingsErrors)

    def skipToSequenceInput(self):
        # Adds to stack anyway but skips over them

        self.settingsScreen3 = self.createSettingsScreen3()
        self.stackedWidget.addWidget(self.settingsScreen3)  # index 6
        # Create and add the sequence input screen dynamically at index 7
        self.sequenceInputScreen = self.createSequenceInputScreen()
        self.stackedWidget.addWidget(self.sequenceInputScreen)  # index 7

        # Create loading Screen and at at index 8
        self.loadingScreen = self.createLoadingScreen()
        self.stackedWidget.addWidget(self.loadingScreen)  # index 6

        # Navigate to the sequence input screen
        self.stackedWidget.setCurrentIndex(7)

    def createHomeWidget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        widget.setLayout(layout)

        # Welcome Label
        welcome_label = QLabel("Welcome to Delilah's Cut!")
        welcome_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: #FAD7A0;")
        layout.addWidget(welcome_label)

        # Subtext Label
        welcome_label2 = QLabel(
            "This tool is designed to help you make the perfect cut. Explore the information, learn how to best utilize this program, and begin your analysis journey."
        )
        welcome_label2.setFont(QFont("Arial", 20))
        welcome_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label2.setWordWrap(True)
        welcome_label2.setStyleSheet("color: #F5EFE5;")
        layout.addWidget(welcome_label2)

        # Optional Decorative Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet("color: #FAD7A0;")
        layout.addWidget(divider)

        # Inspirational Quote
        quote_label = QLabel("")
        quote_font = QFont("Arial", 16)
        quote_font.setItalic(True)
        quote_label.setFont(quote_font)
        quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quote_label.setStyleSheet("color: #F5EFE5;")
        layout.addWidget(quote_label)

        # Spacer
        layout.addStretch()

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Information Button
        info_button = QPushButton("Information")
        info_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        info_button.setFixedHeight(60)
        info_button.setStyleSheet(
            """
            QPushButton {
                background-color: #212121;
                color: #F5EFE5;
                border: 2px solid #FAD7A0;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #FAD7A0;
                color: #212121;
            }
            """
        )
        info_button.clicked.connect(self.showInfoScreen)
        button_layout.addWidget(info_button)

        # Usage Button
        usage_button = QPushButton("Usage")
        usage_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        usage_button.setFixedHeight(60)
        usage_button.setStyleSheet(
            """
            QPushButton {
                background-color: #212121;
                color: #F5EFE5;
                border: 2px solid #FAD7A0;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #FAD7A0;
                color: #212121;
            }
            """
        )
        usage_button.clicked.connect(self.showUsageScreen)
        button_layout.addWidget(usage_button)

        # Begin Analysis Button
        analysis_button = QPushButton("Begin Analysis")
        analysis_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        analysis_button.setFixedHeight(60)
        analysis_button.setStyleSheet(
            """
            QPushButton {
                background-color: #212121;
                color: #F5EFE5;
                border: 2px solid #FAD7A0;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #FAD7A0;
                color: #212121;
            }
            """
        )
        analysis_button.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.settingsScreen1)
        )
        button_layout.addWidget(analysis_button)

        layout.addLayout(button_layout)

        # Spacer to balance the layout
        layout.addStretch()

        return widget

    def createInfoWidget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)  # Add padding around the content
        layout.setSpacing(20)  # Add space between elements
        widget.setLayout(layout)

        # Title label
        title_label = QLabel("Program Information")
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #FAD7A0;")  # Match the highlight color
        layout.addWidget(separator)

        # Read and convert Markdown to HTML
        markdown_file_path = resource_path("MarkDownFiles/InformationPage.md")
        with open(markdown_file_path, "r", encoding="utf-8") as file:
            markdown_content = file.read()
        html_content = markdown.markdown(markdown_content)

        # Create a QTextEdit widget to display the HTML content
        info_text_edit = QTextEdit()
        info_text_edit.setReadOnly(True)
        info_text_edit.setHtml(html_content)
        info_text_edit.setFont(QFont("Arial", 16))
        info_text_edit.setStyleSheet(
            "color: #F5EFE5; background-color: #333333; border: none;"
        )

        # Add a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(info_text_edit)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #212121;")
        # Make the scroll area take up 90% of the available vertical space
        layout.addWidget(scroll_area, stretch=9)

        # Spacer to push the Back button to the bottom
        layout.addStretch()

        # Back button
        back_button = QPushButton("Back to Home")
        back_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        back_button.setFixedHeight(50)
        back_button.setStyleSheet(
            """
            QPushButton {
                background-color: #212121;
                color: #F5EFE5;
                border: 2px solid #FAD7A0;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #FAD7A0;
                color: #212121;
            }
            """
        )
        back_button.clicked.connect(self.showHomeScreen)
        layout.addWidget(back_button)

        return widget

    def createUsageWidget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)  # Add padding around the content
        layout.setSpacing(20)  # Add space between elements
        widget.setLayout(layout)

        # Title label
        title_label = QLabel("Usage Information")
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #FAD7A0;")  # Match the highlight color
        layout.addWidget(separator)

        # Read and convert Markdown to HTML
        markdown_file_path = resource_path("MarkDownFiles/UsagePage.md")
        with open(markdown_file_path, "r", encoding="utf-8") as file:
            markdown_content = file.read()
        html_content = markdown.markdown(markdown_content)

        # Create a QTextEdit widget to display the HTML content
        info_text_edit = QTextEdit()
        info_text_edit.setReadOnly(True)
        info_text_edit.setHtml(html_content)
        info_text_edit.setFont(QFont("Arial", 16))
        info_text_edit.setStyleSheet(
            "color: #F5EFE5; background-color: #333333; border: none;"
        )

        # Add a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(info_text_edit)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #212121;")
        # Make the scroll area take up 90% of the available vertical space
        layout.addWidget(scroll_area, stretch=9)

        # Spacer to push the Back button to the bottom
        layout.addStretch()

        # Back button
        back_button = QPushButton("Back to Home")
        back_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        back_button.setFixedHeight(50)
        back_button.setStyleSheet(
            """
            QPushButton {
                background-color: #212121;
                color: #F5EFE5;
                border: 2px solid #FAD7A0;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #FAD7A0;
                color: #212121;
            }
            """
        )
        back_button.clicked.connect(self.showHomeScreen)
        layout.addWidget(back_button)

        return widget

    def showInfoScreen(self):
        self.stackedWidget.setCurrentIndex(2)

    def showUsageScreen(self):
        self.stackedWidget.setCurrentIndex(3)

    def showHomeScreen(self):
        self.stackedWidget.setCurrentIndex(1)

    def createStartUpWidget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)  # Add padding around the content
        layout.setSpacing(20)  # Add space between elements
        widget.setLayout(layout)

        # Add logo
        logo = QLabel()
        logo.setPixmap(
            QPixmap(resource_path("Assets/Delilah's_Cut_Logo.png")).scaled(
                400,
                400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # Add a line separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #FAD7A0;")  # Match the highlight color
        layout.addWidget(separator)

        # Add typing label
        self.typing_label = QLabel()
        self.typing_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.typing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.typing_label)

        # Start the typing animation
        QTimer.singleShot(0, self.start_typing)

        return widget

    def start_typing(self):
        text = "Delilah's Cut: an siRNA design tool"
        self.current_text = ""
        self.index = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.update_text(text))
        self.timer.start(50)

    def update_text(self, text):
        if self.index < len(text):
            self.current_text += text[self.index]
            self.typing_label.setText(self.current_text)
            self.index += 1
        else:
            self.timer.stop()
            QTimer.singleShot(1000, self.move_to_next_widget)

    @pyqtSlot()
    def move_to_next_widget(self):
        self.stackedWidget.setCurrentIndex(1)


class NoScrollSlider(QSlider):
    def wheelEvent(self, event):
        event.ignore()  # Ignore the wheel event to prevent interaction


"""
CODE BELOW THIS PART NOT GUI, INCLUDED IN THIS FILE FOR CONVIENCE

Code below works to call other functions to perform the RNA functions




"""


# Run the application
def runApp():
    app = QApplication(sys.argv)
    window = MainWindow(settings.basicNeedsDict, settings.exclusionAndScoringDict)
    window.show()
    sys.exit(app.exec())


# BACKEND


def runBackend():

    # gets mRNA from user or specified source and returns string with just agcu lowercase
    mRNA = MRNA()

    # gets mRNA all set up with its attributes
    mRNA.getMRNA()

    # generates subsequences of REVERSE COMPLIMENT of input as list of RNA objects
    siRNAs = mRNA.generatesiRNASeq(
        settings.basicNeedsDict["minLengthChecked"],
        settings.basicNeedsDict["maxLengthCHecked"],
    )

    # Excludes RNA based on input parameters and returns touple of Lists 'keptRNAs, excludedRNAs' which contain RNA Objects
    kept, removed = basicExclusion(siRNAs, settings.exclusionAndScoringDict)

    # Score RNAs
    scoredRNA = scoreRNA(kept, settings.exclusionAndScoringDict)

    # sort by highest to lowest score
    sortedRNA = bubbleSortRNAs(scoredRNA)

    # gets top n RNAs
    topRNAs = topNRNAs(sortedRNA, settings.basicNeedsDict["HowManyRNAOutput"])

    # saves Settings file
    if (
        settings.basicNeedsDict["saveSettings"] == True
        and settings.basicNeedsDict["OutputFileName"] != ""
    ):

        settings.saveDataJson(settings.basicNeedsDict["OutputFileName"])

    # generates and saves reports to global variable
    RNAreports = generateRNAreports(topRNAs, settings.exclusionAndScoringDict)
    OverviewReport = generateOverviewReport()

    reports = []
    reports.append(OverviewReport)
    reports.extend(RNAreports)
    global resultsReport
    resultsReport = reports


def get_base_dir():
    """
    Returns the base directory of the executable. This will be the directory
    where the exe is located when packaged, or the script's directory in development.
    """
    if getattr(sys, "frozen", False):
        # The application is frozen (packaged by PyInstaller)
        base_dir = os.path.dirname(sys.executable)
    else:
        # The application is running as a normal Python script
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return base_dir


def get_settings_file_path(filename):
    """
    Returns the path to the settings file in the 'Saved_Settings' directory.
    """
    base_dir = get_base_dir()
    return os.path.join(base_dir, "Saved_Settings", filename)


def get_input_file_path(filename):
    """
    Returns the path to the input file in the 'Sequence_Inputs' directory.
    """
    base_dir = get_base_dir()
    return os.path.join(base_dir, "Sequence_Inputs", filename)
