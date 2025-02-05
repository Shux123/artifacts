import time
from character import Character
from PySide6.QtCore import (
    Qt,
    QSize, 
    QThreadPool, 
    QRunnable, 
    Slot, 
    Signal,
    QObject,
)
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QSpinBox,
    QLineEdit
)

FONT_SIZE = 18

names_for_btns = {
    'resource': ['Gathering'],
    'monster': ['Fight'],
    'workshop': ['Craft', 'Recycling'],
    'bank': ['Deposit', 'Withdraw', 'Depo $', 'Withdraw $'],
    'tasks_master': ['New task', 'Task trade', 'Complete task',
        'Cancel task', 'Task exchange'],
    'grand_exchange': [],
    'santa_claus': []
}

class WorkerSignal(QObject):
    finished = Signal()

class Worker(QRunnable):
    def __init__(self, cooldown):
        super().__init__()
        self.cooldown = cooldown
        self.signals = WorkerSignal()
    
    @Slot()
    def run(self):
        while self.cooldown >= 0:
            time.sleep(1)
            window.cooldown_label.setText(str(self.cooldown))
            self.cooldown -= 1
        window.cooldown_label.setText('0')
        self.signals.finished.emit()
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.char = Character('shuxart')

        self.threadpool = QThreadPool()

        self.my_font = QFont('Times', FONT_SIZE)
        self.btns_pointers = []

        self.name_label = QLabel(self.char.name)
        self.name_label.setFont(QFont('Times', FONT_SIZE+6))
        self.name_label.setStyleSheet("QLabel{ color: blue; }")
        self.level_label = QLabel()
        self.level_label.setFont(self.my_font)
        self.hp_label = QLabel()
        self.hp_label.setFont(self.my_font)
        self.xp_label = QLabel()
        self.xp_label.setFont(self.my_font)
        self.gold_label = QLabel()
        self.gold_label.setFont(self.my_font)
        self.cooldown_label = QLabel('0')
        self.cooldown_label.setStyleSheet("QLabel{ color: red; }")
        self.cooldown_label.setFont(self.my_font)
        self.cooldown_label.setAlignment(Qt.AlignCenter)
        info_layout = QHBoxLayout()
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.level_label)
        info_layout.addWidget(self.hp_label)
        info_layout.addWidget(self.xp_label)
        info_layout.addWidget(self.gold_label)
        info_layout.addWidget(self.cooldown_label)

        move_btn = QPushButton('Move')
        move_btn.setFont(self.my_font)
        move_btn.pressed.connect(lambda btn=move_btn: self.get_info(btn=btn))
        self.x_box = QSpinBox()
        self.x_box.setMinimum(-5)
        self.x_box.setFont(self.my_font)
        self.y_box = QSpinBox()
        self.y_box.setMinimum(-5)
        self.y_box.setFont(self.my_font)
        get_map = QPushButton('Map')
        get_map.pressed.connect(lambda btn=get_map: self.get_info(btn=btn))
        get_map.setFont(self.my_font)
        move_layout = QHBoxLayout()
        move_layout.addWidget(move_btn)
        move_layout.addWidget(self.x_box)
        move_layout.addWidget(self.y_box)
        move_layout.addWidget(get_map)

        controls_layout = QHBoxLayout()
        btns_layout = QVBoxLayout()
        self.info_view = QTextEdit()
        self.info_view.setFont(self.my_font)
        controls_layout.addWidget(self.info_view)

        self.location_layout = QVBoxLayout()
        self.location_label = QLabel()
        self.location_label.setFont(self.my_font)
        self.location_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.location_layout.addWidget(self.location_label)
        
        buttons = [
            'Rest', 'Logs', 'Maps', 'Char info', 'Skills',
            'Stats', 'Clothes', 'Inventory', 'Bank',
        ]
        for button in buttons:
            btn = QPushButton(button)
            btn.setFont(self.my_font)
            btns_layout.addWidget(btn)
            btn.pressed.connect(lambda btn=btn: self.get_info(btn=btn))
        
        controls_layout.addLayout(self.location_layout)
        controls_layout.addLayout(btns_layout)

        control_label = QLabel('Ask/use info/item by code:')
        control_label.setFont(self.my_font)
        self.control_edit = QLineEdit()
        self.control_edit.setFont(self.my_font)
        self.number_edit = QSpinBox()
        self.number_edit.setValue(1)
        self.number_edit.setMinimum(0)
        self.number_edit.setMaximum(9999)
        self.number_edit.setFont(self.my_font)
        self.find_button = QPushButton('Find text')
        self.find_button.setFont(self.my_font)
        self.find_button.pressed.connect(self.find_text)
        control_layout_2 = QHBoxLayout()
        control_layout_2.addWidget(control_label)
        control_layout_2.addWidget(self.control_edit)
        control_layout_2.addWidget(self.number_edit)
        control_layout_2.addWidget(self.find_button)

        control_layout_3 = QHBoxLayout()
        buttons = [
            'Equip', 'Unequip', 'Crafted by skills', 'Item info',
            'Monster info', 'Use Item', 'Delete item'
        ]
        for button in buttons:
            btn = QPushButton(button)
            btn.setFont(self.my_font)
            control_layout_3.addWidget(btn)
            btn.pressed.connect(lambda btn=btn: self.get_info(btn=btn))

        script_label = QLabel('Write script:')
        script_label.setFont(self.my_font)
        self.script_edit = QLineEdit()
        self.script_edit.setFont(self.my_font)
        self.script_number = QSpinBox()
        self.script_number.setFont(self.my_font)
        self.script_number.setMaximum(999)
        self.script_btn_start = QPushButton('Start script')
        self.script_btn_start.setFont(self.my_font)
        self.script_btn_start.pressed.connect(self.script_start)
        self.script_btn_stop = QPushButton('Stop script')
        self.script_btn_stop.setFont(self.my_font)
        self.script_btn_stop.pressed.connect(self.script_stop)
        script_layout = QHBoxLayout()
        script_layout.addWidget(script_label)
        script_layout.addWidget(self.script_edit)
        script_layout.addWidget(self.script_number)
        script_layout.addWidget(self.script_btn_start)
        script_layout.addWidget(self.script_btn_stop)

        self.main_v_layout = QVBoxLayout()
        self.main_v_layout.addLayout(info_layout)
        self.main_v_layout.addLayout(move_layout)
        self.main_v_layout.addLayout(controls_layout)
        self.main_v_layout.addLayout(control_layout_2)
        self.main_v_layout.addLayout(control_layout_3)
        self.main_v_layout.addLayout(script_layout)

        widget = QWidget()
        widget.setLayout(self.main_v_layout)

        self.setCentralWidget(widget)
        self.setFixedSize(QSize(1100, 600))

        self.update_info()
        self.get_info(action='map')

    def get_info(self, btn=None, action=None):
        if btn:
            action = btn.text().lower()
        if action in ('move', 'map'):
            x = self.x_box.text()
            y = self.y_box.text()
            answer = getattr(self.char, action)(x, y)
            self.update_location(answer, x, y)
        elif action in ('char info', 'skills', 'stats','clothes', 'inventory', 'bank'):
            answer = self.char.view_info_about_char(action)
        elif action in ('equip', 'unequip'):
            item = self.control_edit.text().lower()
            quantity = self.number_edit.text()
            answer = getattr(self.char, 'equip_unequip')(action, item, quantity)
        elif action in ('crafted by skills', 'item info', 'monster info'):
            text = self.control_edit.text().lower()
            if action == 'crafted by skills':
                answer = self.char.get_crafted_items_by_skills(text)
            elif action == 'item info':
                answer = self.char.get_item_info(text)
            elif action == 'monster info':
                answer = self.char.get_monster_info(text)
        elif action in (
            'craft', 'use item', 'recycling', 'delete item', 'use',
            'deposit', 'withdraw', 'task trade'):
            action = action.split()[0]
            action = ''.join(action)
            item = self.control_edit.text().lower()
            quantity = self.number_edit.text()
            answer = getattr(self.char, action)(item, quantity)
        elif 'task' in action and action != 'task trade':
            action = action.replace('task', '').strip()
            answer = self.char.task_action(f"task/{action}")
        elif action == 'depo $':
            answer = self.char.deposit_gold(self.number_edit.text())
        elif action == 'withdraw $':
            answer = self.char.withdraw_gold(self.number_edit.text())
        else:
            answer = getattr(self.char, action)()
        self.show_info(answer)

    def show_info(self, answer):
        text = ''
        for a in answer['new_data']:
            text += a
            text += '\n'
        self.info_view.setText(text)
        if 'cooldown' in answer:
            cooldown = answer['cooldown']
            worker = Worker(cooldown)
            worker.signals.finished.connect(self.script_start)
            self.threadpool.start(worker)
        self.update_info()

    def update_location(self, answer, x, y):
        if len(self.btns_pointers) > 0:
            for btn in self.btns_pointers:
                btn.setParent(None)
                btn.deleteLater()
            self.btns_pointers.clear()
        if 'type' in answer:
            name = answer['name']
            type = answer['type']
            code = answer['code']
            self.location_label.setText(
                '\n'.join(['Location:', name, f"x: {x}, y: {y}", type, code]))
            
            for button in names_for_btns[type]:
                btn = QPushButton(button)
                btn.setFont(self.my_font)
                self.btns_pointers.append(btn)
                self.location_layout.addWidget(btn)
                btn.pressed.connect(lambda btn=btn: self.get_info(btn=btn))
            
        else:
            self.location_label.setText(
                '\n'.join(['Location:', answer['name'], f"x: {x}, y: {y}"]))

    
    def update_info(self):
        self.level_label.setText(f"lvl: {str(self.char.char_info['level'])}")
        self.x_box.setValue(self.char.char_info['x'])
        self.y_box.setValue(self.char.char_info['y'])
        self.hp_label.setText(
            f"HP: {self.char.char_info['hp']}/{self.char.char_info['max_hp']}")
        self.xp_label.setText(
            f"XP: {self.char.char_info['xp']}/{self.char.char_info['max_xp']}"
        )        
        self.gold_label.setText(f"G: {self.char.char_info['gold']}")

    def script_start(self):
        action = self.script_edit.text().split()
        number = int(self.script_number.text())
        if number > 0:
            current_action = action[0]
            self.get_info(action=current_action)
            number -= 1
            self.script_number.setValue(number)
            action = action[1:]
            action.append(current_action)
            self.script_edit.setText(' '.join(action))

    def script_stop(self):
        self.script_number.setValue(0)

    def find_text(self):
        format = QTextCharFormat()
        self.info_view.selectAll()
        self.info_view.textCursor().mergeCharFormat(format)
        format.setBackground(QColor(Qt.gray))
        self.info_view.moveCursor(QTextCursor.Start)
        word = self.control_edit.text()[0:-1]
        while self.info_view.find(word):
            text_cursor = self.info_view.textCursor()
            text_cursor.select(QTextCursor.WordUnderCursor)
            text_cursor.mergeCharFormat(format)
            self.info_view.setTextCursor(text_cursor)
        format.setBackground(QColor(Qt.white))

app = QApplication()
window = MainWindow()
window.show()
app.setStyle('Fusion')
app.exec()