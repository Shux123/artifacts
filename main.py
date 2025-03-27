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
    'bank': ['Deposit', 'Withdraw', 'Depo $', 'Withdraw $',
        'Buy expansion'],
    'tasks_master': ['New task', 'Task trade', 'Complete task',
        'Cancel task', 'Task exchange'],
    'grand_exchange': ['Buy item', 'Create sell order',
        'Cancel sell order', 'Get sell orders',
        'Sell item hystory'],
    'santa_claus': [],
    'npc': ['Buy item', 'Sell item', 'Items in shop'],
    'right_btns_panel': ['Rest', 'Logs', 'Maps', 'Char info', 'Skills',
        'Stats', 'Clothes', 'Inventory', 'Bank',],
    'bottom_btns_panel': ['Equip', 'Unequip', 'Crafted by skills',
        'Item info', 'Monster info', 'Use Item', 'Delete item', 
        'Events']
}
btns_names_to_action = {
    'Move': 'move',
    'Gathering': 'gathering',
    'Fight': 'fight',
    'Craft': 'craft',
    'Recycling': 'recycling',
    'Deposit': 'deposit',
    'Withdraw': 'withdraw',
    'Depo $': 'deposit_gold',
    'Withdraw $': 'withdraw_gold',
    'Buy expansion': 'buy_bank_expansion',
    'New task': 'task_action',
    'Task trade': 'task_trade',
    'Complete task': 'task_action',
    'Cancel task': 'task_action',
    'Task exchange': 'task_action',
    'Rest': 'rest',
    'Logs': 'logs',
    'Maps': 'maps',
    'Map': 'map',
    'Char info': 'view_info_about_char',
    'Skills': 'view_info_about_char',
    'Stats': 'view_info_about_char',
    'Clothes': 'view_info_about_char',
    'Inventory': 'view_info_about_char',
    'Bank': 'view_info_about_char',
    'Equip': 'equip_unequip',
    'Unequip': 'equip_unequip',
    'Crafted by skills': 'get_crafted_items_by_skills',
    'Item info': 'get_item_info',
    'Monster info': 'get_monster_info',
    'Use Item': 'use_item',
    'Delete item': 'delete_item',
    'Events': 'get_active_events',
    'Buy item': 'npc_buy_sell_item',
    'Sell item': 'npc_buy_sell_item',
    'Items in shop': 'get_npc_items',
    'Buy item': 'ge_buy_item',
    'Create sell order': 'ge_create_sell_order',
    'Cancel sell order': 'ge_cancel_sell_order',
    'Get sell orders': 'ge_get_sell_orders',
    'Sell item hystory': 'ge_get_hystory'
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
        
        for button in names_for_btns['right_btns_panel']:
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

        for button in names_for_btns['bottom_btns_panel']:
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
        info = {}
        if btn:
            button_name = btn.text()
            info['button_name'] = button_name.lower()
        if not action:
            action = btns_names_to_action[button_name]
        info['x'] = self.x_box.text()
        info['y'] = self.y_box.text()
        info['text'] = self.control_edit.text().lower()
        info['quantity'] = self.number_edit.text()
        answer = getattr(self.char, action)(info)
                
        if action in ('move', 'map'):
            self.update_location(answer, info['x'], info['y'])

        self.show_info(answer)

    def show_info(self, answer):
        text = ''
        for a in answer['data']:
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
        if 'error' in answer:
            return
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
            
        elif 'name' in answer:
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
        actions = self.script_edit.text().split()
        number = int(self.script_number.text())
        if number > 0:
            current_action = actions[0]
            self.get_info(action=current_action)
            number -= 1
            self.script_number.setValue(number)
            actions = actions[1:]
            actions.append(current_action)
            self.script_edit.setText(' '.join(actions))

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