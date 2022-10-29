import sqlite3
from datetime import datetime

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox

from UI import Ui_MainWindow


def dictFactory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    col_names = [col[0] for col in cursor.description]
    return {key: value for key, value in zip(col_names, row)}


def showMessagebox(msg: str, is_warning: bool):
    msg_box = QMessageBox()
    msg_box.setWindowFlag(Qt.FramelessWindowHint)
    msg_box.setIcon(QMessageBox.Warning if is_warning else QMessageBox.Information)
    msg_box.setWindowTitle('Warning' if is_warning else 'Introduction')
    msg_box.setText(msg)
    color = 'red' if is_warning else 'black'
    msg_box.setStyleSheet(f'''
        QLabel {{
            min-height: 100px;
            color: {color};
            font-family: Comic Sans MS;
            font-size: 24px;
        }}
        QPushButton {{
            font-family: Comic Sans MS;
        }}
    ''')
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


class WindowController(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Bulletin')
        self.setWindowIcon(QtGui.QIcon('pudding.png'))
        self.setup_control()
        self.curr_id = None
        self.shots = [QPixmap(f'shots/{i}.png') for i in range(3)]
        self.conn = sqlite3.connect('./bulletin.db')
        with self.conn:
            self.cursor = self.conn.cursor()
            self.conn.row_factory = dictFactory
        self.listPosts()
        self.ui.r_widget.setVisible(False)
        self.ui.emoji_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.ui.emoji_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

    def setup_control(self):
        self.ui.sign_up_btn.clicked.connect(self.signUp)
        self.ui.sign_in_btn.clicked.connect(self.signIn)
        self.ui.sign_out_btn.clicked.connect(self.signOut)
        self.ui.update_btn.clicked.connect(self.updateProfile)
        self.ui.post_btn.clicked.connect(self.writePost)
        self.ui.order_box.currentIndexChanged.connect(self.listPosts)
        self.setSignIn(False)

    def signUp(self):
        acct = self.ui.acct.text()
        pwd = self.ui.pwd.text()
        if acct == '' or pwd == '':
            showMessagebox('Account and Password fields must be filled.', True)
        else:
            user = self.conn.execute(
                'SELECT * FROM `user` WHERE `account`=? LIMIT 1;', (acct,)
            ).fetchone()
            if user is None:
                self.cursor.execute(
                    'INSERT INTO `user` (`account`, `password`, `gender`) VALUES (?, ?, ?);', (acct, pwd, 0)
                )
                self.conn.commit()
                self.curr_id = self.cursor.lastrowid
                self.setSignIn(True)
            else:
                showMessagebox('The account had been registered.', True)

    def signIn(self):
        acct = self.ui.acct.text()
        pwd = self.ui.pwd.text()
        user = self.conn.execute(
            f"SELECT * FROM `user` WHERE `account`=? AND `password`=? LIMIT 1;", (acct, pwd,)
        ).fetchone()
        if user is None:
            showMessagebox('The account or the password was incorrect.', True)
        else:
            self.curr_id = user['id']
            self.setSignIn(True)

    def signOut(self):
        self.curr_id = None
        self.setSignIn(False)

    def setSignIn(self, sign_in: bool):
        self.ui.acct.setEnabled(not sign_in)
        self.ui.pwd.setEnabled(not sign_in)
        self.ui.sign_up_btn.setVisible(not sign_in)
        self.ui.sign_in_btn.setVisible(not sign_in)
        self.ui.sign_out_btn.setVisible(sign_in)
        self.ui.profile.setVisible(sign_in)
        self.ui.w_title.setEnabled(sign_in)
        self.ui.w_cont.setEnabled(sign_in)
        self.ui.post_btn.setEnabled(sign_in)
        self.ui.r_widget.setVisible(False)
        if sign_in:
            self.loadProfile()

    def loadProfile(self):
        user = self.conn.execute(
            f"SELECT * FROM `user` WHERE `id`=? LIMIT 1;", (self.curr_id,)
        ).fetchone()
        self.ui.profile.setVisible(True)
        self.ui.name.setText(user['name'])
        self.ui.intro.setText(user['introduction'])
        self.ui.birth.setDate(QtCore.QDate.fromString(user['birthday'], 'yyyy/MM/dd'))
        self.ui.new_pwd.setText(user['password'])
        self.ui.male.setChecked(user['gender'] == 1)
        self.ui.female.setChecked(user['gender'] == 2)
        self.ui.others.setChecked(user['gender'] == 0)
        post_num = self.conn.execute(
            'SELECT COUNT(*) AS `num` FROM `post` WHERE `user_id`=?;', (self.curr_id,)
        ).fetchone()['num']
        self.ui.ttl_post_lb.setText(f'Total Posts: {post_num}')
        give_emojis = self.conn.execute(
            'SELECT `emoji`.`user_id`, `emoji`.`emoji`, COUNT(*) AS `num`,`post`.`user_id` AS `post_user_id` '
            'FROM `emoji` JOIN `post` ON `emoji`.`post_id`=`post`.`id` '
            'WHERE `emoji`.`user_id`=? AND `post_user_id`<>? AND `emoji`.`emoji`<>-1 GROUP BY `emoji`;',
            (self.curr_id, self.curr_id,)
        ).fetchall()
        given_emojis = self.conn.execute(
            'SELECT `emoji`.`user_id`, `emoji`.`emoji`, COUNT(*) AS `num`,`post`.`user_id` AS `post_user_id` '
            'FROM `emoji` JOIN `post` ON `emoji`.`post_id`=`post`.`id` '
            'WHERE `emoji`.`user_id`<>? AND `post_user_id`=? AND `emoji`.`emoji`<>-1 GROUP BY `emoji`;',
            (self.curr_id, self.curr_id,)
        ).fetchall()
        give_nums, given_nums = [0 for _ in range(8)], [0 for _ in range(8)]
        for i in give_emojis:
            give_nums[i['emoji']] = i['num']
        for i in given_emojis:
            given_nums[i['emoji']] = i['num']
        for i in range(8):
            self.ui.emoji_table.item(0, i).setText(str(give_nums[i]))
            self.ui.emoji_table.item(1, i).setText(str(given_nums[i]))

    def updateProfile(self):
        name = self.ui.name.text()
        user = self.conn.execute(
            'SELECT * FROM `user` WHERE `name`=? AND `id`<>? LIMIT 1;', (name, self.curr_id)
        ).fetchone()
        if user is not None:
            showMessagebox('The name has been used.', True)
            return
        intro = self.ui.intro.toPlainText()
        birth = self.ui.birth.date().toString('yyyy/MM/dd')
        new_pwd = self.ui.new_pwd.text()
        gender = 1 if self.ui.male.isChecked() else 2 if self.ui.female.isChecked() else 0
        self.conn.execute(
            'UPDATE `user` SET `name`=?, `introduction`=?, `birthday`=?, `gender`=?, `password`=? WHERE `id`=?;',
            (name, intro, birth, gender, new_pwd, self.curr_id,)
        )
        self.conn.commit()
        self.loadProfile()

    def writePost(self):
        title = self.ui.w_title.text()
        cont = self.ui.w_cont.toPlainText()
        time = datetime.now()
        if title == '' or cont == '':
            showMessagebox('Title and Content fields must be filled.', True)
        else:
            self.cursor.execute(
                'INSERT INTO `post` (`user_id`, `title`, `content`, `time`) VALUES (?, ?, ?, ?);',
                (self.curr_id, title, cont, time,)
            )
            self.conn.commit()
            self.ui.w_title.clear()
            self.ui.w_cont.clear()
            self.listPosts()
            self.readPost(self.cursor.lastrowid)

    def listPosts(self):
        if self.ui.order_box.currentIndex() == 2:
            posts = self.conn.execute(
                'SELECT `post`.*, `user`.`name`, `user`.`gender`, '
                '(SELECT COUNT(*) FROM `emoji` '
                'WHERE `post`.`id`=`emoji`.`post_id` AND `post`.`user_id`<>`emoji`.`user_id` '
                'AND `emoji`.`emoji`<>-1) AS `pop` FROM `post` '
                'JOIN `user` ON `post`.`user_id`=`user`.`id` ORDER BY `pop` DESC;'
            ).fetchall()
        else:
            order = 'DESC' if self.ui.order_box.currentIndex() == 0 else 'ASC'
            posts = self.conn.execute(
                'SELECT `post`.*, `user`.`name`, `user`.`gender` FROM `post` '
                'JOIN `user` ON `post`.`user_id`=`user`.`id` '
                'ORDER BY `post`.`time` ' + order + ';',
            ).fetchall()
        post_count = len(self.ui.l_widget.children())
        for i in range(len(posts)):
            if i >= post_count:
                globals()[f'frame_{i}'] = QtWidgets.QFrame(self.ui.l_widget)
                globals()[f'frame_{i}'].setGeometry(QtCore.QRect(20, 30 + 80 * i, 1101, 41))
                globals()[f'frame_{i}'].setFrameShape(QtWidgets.QFrame.StyledPanel)
                globals()[f'frame_{i}'].setFrameShadow(QtWidgets.QFrame.Raised)
                globals()[f'frame_{i}'].setObjectName(f'frame_{i}')
                globals()[f'img_lb_{i}'] = QtWidgets.QLabel(globals()[f'frame_{i}'])
                globals()[f'img_lb_{i}'].setGeometry(QtCore.QRect(0, 0, 41, 41))
                globals()[f'img_lb_{i}'].setObjectName(f'img_lb_{i}')
                globals()[f'name_{i}'] = QtWidgets.QLabel(globals()[f'frame_{i}'])
                globals()[f'name_{i}'].setGeometry(QtCore.QRect(60, 0, 171, 41))
                globals()[f'name_{i}'].setObjectName(f'name_{i}')
                globals()[f'ttl_{i}'] = QtWidgets.QLabel(globals()[f'frame_{i}'])
                globals()[f'ttl_{i}'].setGeometry(QtCore.QRect(250, 0, 461, 41))
                globals()[f'ttl_{i}'].setObjectName(f'ttl_{i}')
                globals()[f'time_{i}'] = QtWidgets.QLabel(globals()[f'frame_{i}'])
                globals()[f'time_{i}'].setGeometry(QtCore.QRect(740, 0, 211, 41))
                globals()[f'time_{i}'].setObjectName(f'time_{i}')
                globals()[f'read_{i}'] = QtWidgets.QPushButton(globals()[f'frame_{i}'])
                globals()[f'read_{i}'].setGeometry(QtCore.QRect(970, 0, 81, 41))
                globals()[f'read_{i}'].setObjectName(f'read_{i}')
            self.ui.l_widget.setMinimumHeight(30 + 80 * len(self.ui.l_widget.children()))
            post = posts[i]
            globals()[f'img_lb_{i}'].setPixmap(self.shots[post['gender']].scaled(41, 41))
            globals()[f'name_{i}'].setText(post['name'] if post['name'] != '' else '[anonymity]')
            globals()[f'ttl_{i}'].setText(post['title'])
            globals()[f'time_{i}'].setText(post['time'][:-10])
            globals()[f'read_{i}'].setText('Read')
            globals()[f'read_{i}'].disconnect()
            globals()[f'read_{i}'].clicked.connect(lambda _, post_id=post['id']: self.readPost(post_id))

    def readPost(self, post_id: int):
        self.ui.r_widget.setVisible(True)
        self.ui.tabWidget.setCurrentIndex(3)
        post = self.conn.execute(
            'SELECT `post`.*, `user`.`name`, `user`.`introduction`, `user`.`gender` FROM `post` '
            'JOIN `user` ON `post`.`user_id`=`user`.`id` '
            'WHERE `post`.`id`=? LIMIT 1;',
            (post_id,)
        ).fetchone()
        self.ui.r_title.setText(post['title'])
        self.ui.r_cont.setText(post['content'])
        self.ui.r_time.setText(post['time'][:-10])
        self.ui.r_name.setText(post['name'] if post['name'] != '' else '[anonymity]')
        self.ui.r_img_lb.setPixmap(self.shots[post['gender']].scaled(81, 81))
        self.ui.r_intro_btn.disconnect()
        if post['name'] != '':
            self.ui.r_intro_btn.clicked.connect(lambda _: showMessagebox(post['introduction'], False))
        else:
            self.ui.r_intro_btn.clicked.connect(lambda _: showMessagebox('This account is anonymous.', True))
        for i in range(8):
            eval(f'self.ui.e{i}_btn').disconnect()
            if self.curr_id is None:
                eval(f'self.ui.e{i}_btn').clicked.connect(lambda _: showMessagebox('Please sign in first.', True))
            else:
                eval(f'self.ui.e{i}_btn').clicked.connect(lambda _, emoji=i: self.updateEmoji(post_id, emoji))
        self.showEmojiNum(post_id)

    def showEmojiNum(self, post_id: int):
        emojis = self.conn.execute(
            'SELECT `emoji`, COUNT(*) AS `num` FROM `emoji` WHERE `post_id`=? AND `emoji`<>-1 GROUP BY `emoji`;',
            (post_id,)
        ).fetchall()
        nums = [0 for _ in range(8)]
        for i in emojis:
            nums[i['emoji']] = i['num']
        rec = None
        if self.curr_id is not None:
            emoji_rec = self.conn.execute(
                'SELECT `emoji` FROM `emoji` WHERE `user_id`=? AND `post_id`=? AND `emoji`<>-1 LIMIT 1;',
                (self.curr_id, post_id,)
            ).fetchone()
            if emoji_rec is not None:
                rec = emoji_rec['emoji']
        for i in range(8):
            eval(f'self.ui.e{i}_lb').setText(str(nums[i]))
            bd_style = 'inset' if i == rec else 'outset'
            bg_color = '#90caf9' if i == rec else '#bbdefb'
            eval(f'self.ui.e{i}_btn').setStyleSheet(
                f'background-color: {bg_color}; border: 8px {bd_style} #64b5f6; border-radius: 30px;'
            )

    def updateEmoji(self, post_id: int, emoji: int):
        emoji_rec = self.conn.execute(
            'SELECT * FROM `emoji` WHERE `user_id`=? AND `post_id`=? LIMIT 1;', (self.curr_id, post_id,)
        ).fetchone()
        if emoji_rec is None:
            self.conn.execute(
                'INSERT INTO `emoji` (`user_id`, `post_id`, `emoji`) VALUES (?, ?, ?);',
                (self.curr_id, post_id, emoji)
            )
        elif emoji_rec['emoji'] == emoji:
            self.conn.execute(f'UPDATE `emoji` SET `emoji`=-1 WHERE `id`=?;', (emoji_rec['id'],))
        else:
            self.conn.execute(f'UPDATE `emoji` SET `emoji`=? WHERE `id`=?;', (emoji, emoji_rec['id']))
        self.conn.commit()
        self.showEmojiNum(post_id)
        self.loadProfile()
