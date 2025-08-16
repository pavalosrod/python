from PyQt6.QtWidgets import *
from gui import *
import csv
import os

class Logic(QMainWindow, Ui_StudentGPADatabase):
    def __init__(self) -> None:
        """Initialize the main application window and connect button actions"""
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Student GPA Database")
        self.setFixedSize(self.size())

        self.course_input_area = QVBoxLayout()
        self.course_input_container.setLayout(self.course_input_area)
        self.course_widgets: list[tuple[QComboBox, QLineEdit, QComboBox, QComboBox]] = []

        self.submit_button.clicked.connect(self.create_course_inputs)
        self.button_save.clicked.connect(self.input_process)

    def create_course_inputs(self) -> None:
        """
        Creates class input rows based on user input
        Validates that maximum of 4 classes allowed. Shows error message if invalid.
        """
        student_id = self.student_ID.text().strip()
        if not (student_id.isdigit() and len(student_id) == 8):
            self.label_message.setStyleSheet("color: red;")
            self.label_message.setText("Student ID must contain only numbers and be exactly 8 digits long.")
            return None
        
        for row in self.course_widgets:
            for item in row:
                item.deleteLater()
        self.course_widgets = []

        class_count_text = self.num_classes.text()
        if class_count_text.isdigit():
            class_count = int(class_count_text)
        else:
            self.label_message.setStyleSheet("color: red;")
            self.label_message.setText("Enter a valid number of classes.")
            return

        if class_count <= 0 or class_count > 4:
            self.label_message.setStyleSheet("color: red;")
            self.label_message.setText("You can only enter at least 1 and a maximum of 4 classes at a time.")
            return
        else:
            self.label_message.setStyleSheet("color: black;")
            self.label_message.setText("")

        for i in range(class_count):
            layout = QHBoxLayout()

            grade_label = QLabel(f"Class {i + 1}:")
            grade_box = QComboBox()
            grade_box.addItems(["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"])

            credit_label = QLabel("Credits:")
            credit_input = QLineEdit()

            retake_label = QLabel("Retake?")
            retake_box = QComboBox()
            retake_box.addItems(["No", "Yes"])

            old_grade_label = QLabel("Previous Grade:")
            old_grade_box = QComboBox()
            old_grade_box.addItems(["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"])
            old_grade_box.setEnabled(False)


            retake_box.currentIndexChanged.connect(
                lambda _, box=retake_box, old=old_grade_box: old.setEnabled(box.currentText() == "Yes")
            )


            layout.addWidget(grade_label)
            layout.addWidget(grade_box)
            layout.addWidget(credit_label)
            layout.addWidget(credit_input)
            layout.addWidget(retake_label)
            layout.addWidget(retake_box)
            layout.addWidget(old_grade_label)
            layout.addWidget(old_grade_box)

            container = QWidget()
            container.setLayout(layout)
            self.course_input_area.addWidget(container)

            self.course_widgets.append((grade_box, credit_input, retake_box, old_grade_box))

    def input_process(self) -> None:
        """
        Validates user input, calculates GPA, saves student ID, new gpa and quality points to CSV, and clears the form.
        """
        result = self.validate_inputs()
        if result is None:
            return

        student_id, total_credits, total_quality_points, new_gpa, old_gpa = result
        self.save_to_csv(student_id, total_credits, total_quality_points, new_gpa, old_gpa)

        self.student_ID.clear()
        self.num_classes.clear()
        while self.course_input_area.count():
            item = self.course_input_area.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.course_widgets = []

    def validate_inputs(self) -> tuple[str, float, float, float, float] | None:
        """
        Validates all user inputs and calculates the updated GPA. 
        Returns:
        tuple containing the student ID as a string 
        total credits as a float
        total quality points as a float
        New GPA and previous GPA as a float if present otherwise none.
        """
        student_id = self.student_ID.text().strip()
        if not (student_id.isdigit() and len(student_id) == 8):
            self.label_message.setStyleSheet("color: red;")
            self.label_message.setText("Student ID must contain only numbers and be exactly 8 digits long.")
            return None

        grade_points = {"A":4.0,"A-":3.7,"B+":3.3,"B":3.0,"B-":2.7,"C+":2.3,"C":2.0,"C-":1.7,"D+":1.3,"D":1.0,"F":0.0}
        rows = []
        found = False
        old_credits = 0.0
        old_quality_points = 0.0
        old_gpa = None

        if os.path.exists("student_gpa_data.csv"):
            with open("student_gpa_data.csv", "r") as file:
                reader = csv.reader(file)
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 4:
                        if row[0] == student_id:
                            found = True
                            old_credits = float(row[1])
                            old_quality_points = float(row[2])
                            old_gpa = float(row[3])
                        else:
                            rows.append(row)

        for grade_box, credit_input, retake_box, old_grade_box in self.course_widgets:
            if retake_box.currentText() == "Yes" and not found:
                self.label_message.setStyleSheet("color: red;")
                self.label_message.setText("Error: No prior coursework found. Cannot update GPA.")
                return None

        new_quality_points = 0.0
        new_credits = 0.0

        for grade_box, credit_input, retake_box, old_grade_box in self.course_widgets:
            credit_text = credit_input.text()
            if credit_text.replace('.', '', 1).isdigit():
                credit = float(credit_text)
            else:
                self.label_message.setStyleSheet("color: red;")
                self.label_message.setText("Enter valid credit values")
                return None

            if credit <= 0:
                self.label_message.setStyleSheet("color: red;")
                self.label_message.setText("Credits must be greater than 0")
                return None

            grade = grade_box.currentText()
            point = grade_points[grade]

            if retake_box.currentText() == "Yes":
                old_grade = old_grade_box.currentText()
                if old_grade not in grade_points:
                    self.label_message.setStyleSheet("color: red;")
                    self.label_message.setText("Invalid previous grade input")
                    return None
                old_point = grade_points[old_grade]
                new_quality_points -= old_point * credit

            new_quality_points += point * credit
            new_credits += credit

        total_credits = old_credits + new_credits
        total_quality_points = old_quality_points + new_quality_points

        if total_credits == 0:
            new_gpa = 0.0
        else:
            new_gpa = round(total_quality_points / total_credits, 2)

        return student_id, total_credits, total_quality_points, new_gpa, old_gpa

    def save_to_csv(self, student_id: str, total_credits: float, total_quality_points: float, new_gpa: float, old_gpa: float) -> None:
        """
        Writes GPA data to the CSV file. Updates row if student ID already present.
        """
        updated_rows = []
        if os.path.exists("student_gpa_data.csv"):
            with open("student_gpa_data.csv", "r") as file:
                reader = csv.reader(file)
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 4 and row[0] != student_id:
                        updated_rows.append(row)

        updated_rows.append([student_id, total_credits, round(total_quality_points, 2), new_gpa])

        with open("student_gpa_data.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Student ID", "Total Credits", "Quality Points", "Cumulative GPA"])
            for row in updated_rows:
                writer.writerow(row)

        self.label_message.setStyleSheet("color: black;")
        if old_gpa is not None:
            self.label_message.setText(f"Previous GPA: {old_gpa}   New cumulative GPA: {new_gpa}")
        else:
            self.label_message.setText(f"New cumulative GPA: {new_gpa}")
