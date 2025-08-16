from PyQt6.QtWidgets import QApplication
from student_database import Logic 

def main():
    student_database = QApplication([])
    window = Logic()
    window.show()
    student_database.exec()

if __name__ == "__main__":
    main()
