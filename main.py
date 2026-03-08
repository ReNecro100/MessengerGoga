import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit,
    QPushButton, QVBoxLayout, QLabel, QSizePolicy, QScrollArea)
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QFont
from Database_Interactions import MessengerGogaDatabase

import json

#Č, č
#Š, š
#Ž, ž
#Ş, ş

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        #inicyalizacyja v baze dannyh
        dbconfig = json.load(open('dbconfig.json', 'r', encoding='utf-8'))
        db_connection = MessengerGogaDatabase(dbconfig["db"],
                                              dbconfig["user"],
                                              dbconfig["password"],
                                              dbconfig["host"],
                                              dbconfig["port"])
        with open('config.txt', 'r', encoding='utf-8') as config_file:
            login = config_file.readline().replace('\n', '')
            password = config_file.readline().replace('\n', '')
        can_enter = False
        for i in db_connection.query('SELECT * from "MessengerGoga".users;'):
            if (login == i[1]) and (password == i[2]):
                self.user_id = i[0]
                can_enter = True
                break
        if can_enter:
            self.db_connection = db_connection
            self.login = login
            self.password = password

            self.timer = QTimer()
            self.timer.timeout.connect(self.get_messages)  # Что выполнять
            self.timer.start(500)

            #Šrift
            self.font = QFont("Arial", 14)
            self.setFont(self.font)

            #Glavnyje nastrojki okna
            self.setWindowTitle("Messenger Goga bDj-0")
            self.setFixedSize(QSize(1280, 768))

            #Glavnyj lejaut
            self.main_layout = QVBoxLayout()
            self.main_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

            self.scroll = QScrollArea()
            self.scroll.setWidgetResizable(True)  # Важно! Позволяет содержимому растягиваться
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.scroll_widget = QWidget()

            #ГОЛЙДА!!!
            #Siuda prihodiat vse soobşenija
            self.messages_layout = QVBoxLayout(self.scroll_widget)
            self.messages_layout.addStretch()
            self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

            #Otkuda pečatatj nado
            self.message_writer = QVBoxLayout()
            self.message_writer.setAlignment(Qt.AlignmentFlag.AlignBottom)

            #Dobavlenije vseh lejautov
            self.main_layout.addWidget(self.scroll)
            self.main_layout.addLayout(self.messages_layout)
            self.main_layout.addLayout(self.message_writer)
            #self.scroll_widget.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.scroll.setWidget(self.scroll_widget)

            # 1. Create the QLineEdit widget
            self.entry_field = QLineEdit()
            self.entry_field.setPlaceholderText("Enter your message")  # Optional placeholder
            self.message_writer.addWidget(self.entry_field, alignment=Qt.AlignmentFlag.AlignBottom)

            # 2. Create a button to submit the input
            self.submit_button = QPushButton("Submit")
            self.submit_button.clicked.connect(self.on_submit)
            self.message_writer.addWidget(self.submit_button)

            # Optional: Connect the Enter key press to the submit function
            self.entry_field.returnPressed.connect(self.on_submit)

            #Glavnyj lejaut sdelalsia glavoj ugla
            self.setLayout(self.main_layout)

    def on_submit(self):
        message = self.entry_field.text()
        if message:
            #Dobavlenije soobşenija v bazu dannyh
            self.db_connection.query('insert into '+'"MessengerGoga"'+f".messages (userid, chatid, message) values ({self.user_id}, 1, '{message}')")
        self.entry_field.clear()

    def get_messages(self):
        messages_query_result = self.db_connection.query(
            'select * from "MessengerGoga".messages m join "MessengerGoga".users u on u.userid=m.userid;')
        self.clearLayout(self.messages_layout)
        for i in messages_query_result:
            self.message_label(i[4], i[7])

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                elif item.layout() is not None:
                    layout.clearLayout(item.layout())
                del item

    def message_label(self, message, username):
        # Make border color depending on username somehow
        r = 0
        g = 0
        b = 0
        for i in enumerate(username):
            if i[0]%3==0:
                r+=ord(i[1])
            if i[0]%3==1:
                g+=ord(i[1])
            if i[0]%3==2:
                b+=ord(i[1])
        r%=256
        g%=256
        b%=256
        print(r, g, b)
        # Message text
        words = f"{username}:\n{message}"
        message_label = QLabel(words)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("min-width: 640px;"
                                    "max-width: 640px;"
                                    f"border-top: 2px solid rgba({r},{g},{b},0.2);"
                                    "margin: 1rem;"
                                    "padding: 0.5em;")
        message_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.MinimumExpanding
        )
        message_label.setFont(self.font)

        # Adding to layout
        self.messages_layout.addWidget(message_label, alignment=Qt.AlignmentFlag.AlignBottom)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())