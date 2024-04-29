import json
import math
import random
import re
import time
import queue

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget
import pygame
import sys
import os

_hiragana = [
    'あ', 'い', 'う', 'え', 'お',
    'か', 'き', 'く', 'け', 'こ',
    'さ', 'し', 'す', 'せ', 'そ',
    'た', 'ち', 'つ', 'て', 'と',
    'な', 'に', 'ぬ', 'ね', 'の',
    'は', 'ひ', 'ふ', 'へ', 'ほ',
    'ま', 'み', 'む', 'め', 'も',
    'や', 'ゆ', 'よ',
    'ら', 'り', 'る', 'れ', 'ろ',
    'わ', 'を',
    'ん',
]
_katakana = [
    'ア', 'イ', 'ウ', 'エ', 'オ',
    'カ', 'キ', 'ク', 'ケ', 'コ',
    'サ', 'シ', 'ス', 'セ', 'ソ',
    'タ', 'チ', 'ツ', 'テ', 'ト',
    'ナ', 'ニ', 'ヌ', 'ネ', 'ノ',
    'ハ', 'ヒ', 'フ', 'ヘ', 'ホ',
    'マ', 'ミ', 'ム', 'メ', 'モ',
    'ヤ', 'ユ', 'ヨ',
    'ラ', 'リ', 'ル', 'レ', 'ロ',
    'ワ', 'ヲ',
    'ン',
]
_romanji = [
    'a', 'i', 'u', 'e', 'o',
    'ka', 'ki', 'ku', 'ke', 'ko',
    'sa', 'shi', 'su', 'se', 'so',
    'ta', 'chi', 'tsu', 'te', 'to',
    'na', 'ni', 'nu', 'ne', 'no',
    'ha', 'hi', 'fu', 'he', 'ho',
    'ma', 'mi', 'mu', 'me', 'mo',
    'ya', 'yu', 'yo',
    'ra', 'ri', 'ru', 're', 'ro',
    'wa', 'wo',
    'n',
]

# 通过字典的方式将平假名、片假名、罗马字对应起来
hiragana_dict = dict(zip(_romanji, _hiragana))
katakana_dict = dict(zip(_romanji, _katakana))


# 获取随机的罗马音
def get_random_romanji():
    return random.choice(_romanji)


# 通过罗马音获取平假名
def get_hiragana_by_romanji(romanji):
    return hiragana_dict.get(romanji)


# 通过罗马音获取片假名
def get_katakana_by_romanji(romanji):
    return katakana_dict.get(romanji)


# 通过平假名获取罗马音
def get_romanji_by_hiragana(hiragana):
    return _romanji[_hiragana.index(hiragana)]


# 通过片假名获取罗马音
def get_romanji_by_katakana(katakana):
    return _romanji[_katakana.index(katakana)]


# 检查是否为平假名
def is_hiragana(char):
    return char in _hiragana


# 检查是否为片假名
def is_katakana(char):
    return char in _katakana


# 检查是否为罗马音
def is_romanji(char):
    return char in _romanji


# 播放本地音频文件
def play_audio(romanji):
    # 尝试播放音频文件，如果没有对应的音频文件则返回-1
    audio_file = os.path.join('C:\\Users\\PinkYuDeer\\Desktop\\workSpace\\JapaneseLearning\\audio', romanji + '.mp3')
    if not os.path.exists(audio_file):
        return -1
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    return 0


# 本地文件record.json，用于存储用户的答题记录
class Record:
    def __init__(self):
        self.records = {}
        # 记录每个问题的权重，用于根据用户的答题情况调整每个问题的出现概率
        self.weight = {}
        self.summary = {}
        self.load()
        self.avg_time = 0
        self.statistics()
        self.calculate_weight()

    # 从record.json文件中加载数据
    def load(self):
        try:
            with open('record.json', 'r', encoding='utf-8') as f:
                self.records = json.load(f)
        except FileNotFoundError:
            self.records = {}

    # 保存数据到record.json文件中
    def save(self):
        with open('record.json', 'w', encoding='utf-8') as f:
            json.dump(self.records, f, indent=4, ensure_ascii=False)

    # 统计用户的答题情况
    def statistics(self):
        # 遍历record，统计每个罗马音的四种问题的答题情况，包括答对次数、混淆次数、忘记次数、答题总次数、答题正确率、答题速度
        # 初始化所有统计为0
        for romanji in _romanji:
            self.summary[romanji + '1'] = {
                '答对次数': 0,
                '混淆次数': 0,
                '忘记次数': 0,
                '答题总次数': 0,
                '答题正确率': 0,
                '答题速度': 0,
            }
            self.summary[romanji + '2'] = {
                '答对次数': 0,
                '混淆次数': 0,
                '忘记次数': 0,
                '答题总次数': 0,
                '答题正确率': 0,
                '答题速度': 0,
            }
            self.summary[romanji + '3'] = {
                '答对次数': 0,
                '混淆次数': 0,
                '忘记次数': 0,
                '答题总次数': 0,
                '答题正确率': 0,
                '答题速度': 0,
            }
            self.summary[romanji + '4'] = {
                '答对次数': 0,
                '混淆次数': 0,
                '忘记次数': 0,
                '答题总次数': 0,
                '答题正确率': 0,
                '答题速度': 0,
            }
            self.summary[romanji] = {
                '答对次数': 0,
                '混淆次数': 0,
                '忘记次数': 0,
                '答题总次数': 0,
                '答题正确率': 0,
                '答题速度': 0,
            }

        if len(self.records) == 0:
            return
        # 遍历record，统计每个罗马音的四种问题的答对次数、混淆次数、忘记次数、答题总次数、答题总时间
        total_time = 0
        total_count = 0
        total_correct = 0
        total_forget = 0
        total_confuse = 0
        for key, value in self.records.items():
            p_romaji = value['question']
            if value['question_type'] == 2:
                p_romaji = get_romanji_by_katakana(p_romaji)
            elif value['question_type'] == 3:
                p_romaji = get_romanji_by_hiragana(p_romaji)
            self.summary[p_romaji + str(value['question_type'])]['答题总次数'] += 1
            self.summary[p_romaji]['答题总次数'] += 1
            total_count += 1
            if value['type'] == 0:
                self.summary[p_romaji + str(value['question_type'])]['答对次数'] += 1
                self.summary[p_romaji]['答对次数'] += 1
                self.summary[p_romaji + str(value['question_type'])]['答题速度'] += value['used_time']
                self.summary[p_romaji]['答题速度'] += value['used_time']
                total_time += value['used_time']
                total_correct += 1
            elif value['type'] == 1:
                self.summary[p_romaji + str(value['question_type'])]['忘记次数'] += 1
                self.summary[p_romaji]['忘记次数'] += 1
                total_forget += 1
            else:
                self.summary[p_romaji + str(value['question_type'])]['混淆次数'] += 1
                self.summary[p_romaji]['混淆次数'] += 1
                total_confuse += 1
        # 计算答题正确率、答题速度
        for romanji in _romanji:
            for i in range(1, 5):
                if self.summary[romanji + str(i)]['答题总次数'] != 0:
                    self.summary[romanji + str(i)]['答题正确率'] = str(self.summary[romanji + str(i)]['答对次数'] / self.summary[romanji + str(i)]['答题总次数'] * 100) + "%"
                    if self.summary[romanji + str(i)]['答对次数'] != 0:
                        self.summary[romanji + str(i)]['答题速度'] = self.summary[romanji + str(i)]['答题速度'] / self.summary[romanji + str(i)]['答对次数']
            if self.summary[romanji]['答题总次数'] != 0:
                self.summary[romanji]['答题正确率'] = str(self.summary[romanji]['答对次数'] / self.summary[romanji]['答题总次数'] * 100) + "%"
                if self.summary[romanji]['答对次数'] != 0:
                    self.summary[romanji]['答题速度'] = self.summary[romanji]['答题速度'] / self.summary[romanji]['答对次数']
        # 计算所有问题答对次数、混淆次数、忘记次数、答题总次数、答题正确率、答题速度
        self.summary['all'] = {}
        if total_correct != 0:
            self.summary['all']['答题速度'] = total_time / total_correct
        else:
            self.summary['all']['答题速度'] = -1
        self.summary['all']['答题总次数'] = total_count
        self.summary['all']['答对次数'] = total_correct
        self.summary['all']['忘记次数'] = total_forget
        self.summary['all']['混淆次数'] = total_confuse
        if total_count != 0:
            self.summary['all']['答题正确率'] = total_correct / total_count
        else:
            self.summary['all']['答题正确率'] = -1
        # 保存summary
        with open('summary.json', 'w', encoding='utf-8') as f:
            json.dump(self.summary, f, indent=4, ensure_ascii=False)

    # 计算权重，权重越高，问题出现的概率越高
    def calculate_weight(self):
        # 每个罗马音的四种问题类型的权重独立计算
        # 问题类型：1：听音写平片假名、罗马音 2：看片假写平假、罗马音 3：看平假写片假、罗马音 4：看罗马音写平片假
        # 权重应该考虑用户的答题情况，正确率越高，权重越低
        # 还应该考虑用户的答题速度，答题速度越快，做对时权重越低，做错时权重越高
        # 还应该考虑时间，时间越久远，权重越高

        # 初始化所有权重为0
        for romanji in _romanji:
            self.weight[romanji + '1'] = 0
            self.weight[romanji + '2'] = 0
            self.weight[romanji + '3'] = 0
            self.weight[romanji + '4'] = 0

        if len(self.records) == 0:
            return

        # 计算平均用时
        avg_time = 0
        for key, value in self.records.items():
            avg_time += value['used_time']
        avg_time /= len(self.records)
        self.avg_time = avg_time
        # 从第一个记录考试计算，遇到做对时，此罗马音的此类型权重减少400*(根号(平均用时/此次用时))
        # 遇到做错时，此罗马音的此类型权重增加100*((平均用时/此次用时)平方)
        # 遇到做对时，此罗马音的其他类型权重增加10*((平均用时/此次用时)平方)
        # 遇到做错时，此罗马音的其他类型权重增加20*((平均用时/此次用时)平方)
        # 每遍历一次记录，除了这次记录外的所有记录的权重增加1
        # TODO：将weight保存为3维数组，第一维是罗马音，第二维是问题类型，第三维是权重，减少遍历次数
        mistake_recall = queue.Queue(10)
        for key, value in self.records.items():
            if mistake_recall.full():
                mistake_recall.get()
            mistake_recall.put(value)
            # value['question']可能是平假名，也可能是片假名、罗马音，所以需要加上value['question_type']来区分，将其转化为罗马音
            _question = value['question']

            if value['question_type'] == 2:
                _question = get_romanji_by_katakana(_question)
            elif value['question_type'] == 3:
                _question = get_romanji_by_hiragana(_question)
            if value['type'] == 0:
                _p = math.sqrt(avg_time / value['used_time']) / 3
                if _p < 1:
                    _p = 1
                self.weight[_question + str(value['question_type'])] -= 200 * _p
                for k, v in self.weight.items():
                    if k[:-1] == _question and k[-1] != str(value['question_type']):
                        self.weight[k] -= 20 * _p
            else:
                _p = avg_time / value['used_time'] / 5
                if _p < 1:
                    _p = 1
                self.weight[_question + str(value['question_type'])] += 100 * math.pow(_p, 2)
                for k, v in self.weight.items():
                    if k[:-1] == _question and k[-1] != str(value['question_type']):
                        self.weight[k] += 20 * math.pow(_p, 2)

            if _question == 'shi':
                pass
            for k, v in self.weight.items():
                if k[:-1] != _question:
                    self.weight[k] += 1
        # 将记录中的答错记录倒数5-10的记录的权重增加200
        # 如果少于5个记录，则跳过
        if mistake_recall.qsize() >= 5:
            for i in range(mistake_recall.qsize() - 5):
                _record = mistake_recall.get()
                if _record['type'] == 0:
                    continue
                _question = _record['question']
                if _record['question_type'] == 2:
                    _question = get_romanji_by_katakana(_question)
                elif _record['question_type'] == 3:
                    _question = get_romanji_by_hiragana(_question)
                for k, v in self.weight.items():
                    if k[:-1] == _question:
                        if k[-1] == str(_record['question_type']):
                            self.weight[k] += 400
                        else:
                            self.weight[k] += 200

        # 将权重压缩到0-1000之间
        max_weight = max(self.weight.values())
        min_weight = min(self.weight.values())
        for k, v in self.weight.items():
            self.weight[k] = (v - min_weight) / (max_weight - min_weight) * 100
        # 保存权重
        with open('weight.json', 'w', encoding='utf-8') as f:
            json.dump(self.weight, f, indent=4, ensure_ascii=False)

    # 添加一条记录
    # 记录包括：问题类型、问题、答案、错误类型、错误原因、时间
    # 问题类型：1：听音写平片假名、罗马音 2：看片假写平假、罗马音 3：看平假写片假、罗马音 4：看罗马音写平片假
    # 错误类型：0：正确 1:忘记 2:混淆
    def add(self, question_type, question, answer, _type, reason, used_time):
        _time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.records[_time] = {
            'question_type': question_type,
            'question': question,
            'answer': answer,
            'type': _type,
            'reason': reason,
            'used_time': used_time,
        }
        self.save()
        self.calculate_weight()
        self.statistics()
        # TODO: 将每次添加单独计算权重、总结，减少计算次数

    # 根据权重获取问题
    # TODO: 五次内不重复、增加问题出现次数的权重，出现次数越多，权重越低
    def get_question_by_weight(self):
        # 首先，计算问题类型的权重，根据权重加权选择一种问题
        question_type_weight = {}
        for k, v in self.weight.items():
            if k[-1] not in question_type_weight:
                question_type_weight[k[-1]] = 0
            question_type_weight[k[-1]] += v
        max_weight = max(question_type_weight.values())
        min_weight = min(question_type_weight.values())
        if max_weight == min_weight:
            return get_random_romanji(), random.choice([1, 2, 3, 4])
        for k, v in question_type_weight.items():
            question_type_weight[k] = (v - min_weight) / (max_weight - min_weight)
        question_type = random.choices(list(question_type_weight.keys()), list(question_type_weight.values()))[0]

        # 然后，根据选择的问题类型，计算该问题类型的问题的权重，根据权重加权选择一个问题
        question_weight = {}
        for k, v in self.weight.items():
            if k[-1] == question_type:
                question_weight[k[:-1]] = v
        max_weight = max(question_weight.values())
        min_weight = min(question_weight.values())
        for k, v in question_weight.items():
            question_weight[k] = (v - min_weight) / (max_weight - min_weight)
        question = random.choices(list(question_weight.keys()), list(question_weight.values()))[0]
        return question, int(question_type)

    # 根据问题获取所有该记录
    def get(self, question):
        return [record for record in self.records.values() if record['question'] == question]

    # 根据问题获取总次数
    def get_total(self, question):
        return len(self.get(question))

    # 根据问题获取正确次数
    def get_correct(self, question):
        return len([record for record in self.get(question) if record['type'] == 0])

    # 根据问题获取忘记次数
    def get_forget(self, question):
        return len([record for record in self.get(question) if record['type'] == 1])

    # 根据问题获取混淆次数
    def get_confuse(self, question):
        return len([record for record in self.get(question) if record['type'] == 2])

    # 根据问题获取正确率（忘记和混淆都算错误）
    def get_accuracy(self, question):
        total = self.get_total(question)
        correct = self.get_correct(question)
        return correct / total if total != 0 else 0

    # 根据问题获取忘记率
    def get_forget_rate(self, question):
        total = self.get_total(question)
        forget = self.get_forget(question)
        return forget / total if total != 0 else 0

    # 根据问题获取混淆率
    def get_confuse_rate(self, question):
        total = self.get_total(question)
        confuse = self.get_confuse(question)
        return confuse / total if total != 0 else 0

    # 获取所有记录
    def get_all(self):
        return self.records.values()

    # 获取所有记录的总次数
    def get_all_total(self):
        return len(self.records)

    # 获取所有记录的正确次数
    def get_all_correct(self):
        return len([record for record in self.get_all() if record['type'] == 0])

    # 获取所有记录的忘记次数
    def get_all_forget(self):
        return len([record for record in self.get_all() if record['type'] == 1])

    # 获取所有记录的混淆次数
    def get_all_confuse(self):
        return len([record for record in self.get_all() if record['type'] == 2])

    # 获取所有记录的正确率（忘记和混淆都算错误）
    def get_all_accuracy(self):
        total = self.get_all_total()
        correct = self.get_all_correct()
        return correct / total if total != 0 else 0

    # 获取所有记录的忘记率
    def get_all_forget_rate(self):
        total = self.get_all_total()
        forget = self.get_all_forget()
        return forget / total if total != 0 else 0

    # 获取所有记录的混淆率
    def get_all_confuse_rate(self):
        total = self.get_all_total()
        confuse = self.get_all_confuse()
        return confuse / total if total != 0 else 0

    # 获取所有记录的平均正确率
    def get_average_accuracy(self):
        total = self.get_all_total()
        correct = self.get_all_correct()
        return correct / total if total != 0 else 0

    # 获取所有记录的平均忘记率
    def get_average_forget_rate(self):
        total = self.get_all_total()
        forget = self.get_all_forget()
        return forget / total if total != 0 else 0

    # 获取所有记录的平均混淆率
    def get_average_confuse_rate(self):
        total = self.get_all_total()
        confuse = self.get_all_confuse()
        return confuse / total if total != 0 else 0

    # 在控制台输出所有问题的统计信息，首先按照问题类型排序，然后按照问题排序
    def print_all(self):
        for record in sorted(self.records.values(), key=lambda x: (x['question_type'], x['question'])):
            print(record)


# 用于去除html标签，并用空格将多个html标签之间的内容分隔开
def remove_html_tag(html):
    html = re.sub(r'<[^>]+>', ' ', html)
    html = re.sub(r'\s+', ' ', html)
    return html.strip()


class MainWindow(QWidget):
    def __init__(self):

        super().__init__()
        self.play_button1 = None
        self.play_button2 = None
        self.play_button3 = None
        self.question_label1 = None
        self.question_label2 = None
        self.question_label3 = None
        self.question_main_label1 = None
        self.question_main_label2 = None
        self.question_main_label3 = None
        self.record = Record()
        self.answer_label = None
        self.qMessageBox = None
        self.confuse_reason = None
        self.start_button = None
        self.answer = None
        self.question = None
        self.mode = None
        self.romanji = None
        self.questionStr = None
        self.used_time = None
        self.setWindowTitle('日语学习')
        self.setGeometry(100, 100, 300, 300)

        self.stacked_widget = QStackedWidget(self)

        self.start_page = QWidget()
        self.init_start_page()

        self.question_page = QWidget()
        self.init_question_page()

        self.answer_page = QWidget()
        self.init_answer_page()

        self.confuse_page = QWidget()
        self.init_confuse_page()

        self.stacked_widget.addWidget(self.start_page)
        self.stacked_widget.addWidget(self.question_page)
        self.stacked_widget.addWidget(self.answer_page)
        self.stacked_widget.addWidget(self.confuse_page)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def init_start_page(self):
        layout = QHBoxLayout()
        start_button = QPushButton('开始学习', self)
        # noinspection PyUnresolvedReferences
        start_button.clicked.connect(self.next_question_clicked)
        layout.addStretch(1)
        layout.addWidget(start_button)
        layout.addStretch(1)
        self.start_page.setLayout(layout)

    # 显示题目，第一行包含题目类型 + 题目，模式为1时，包含一个播放音频的按钮，模式为其他时直接显示题目
    def init_question_page(self):
        layout = QGridLayout()
        self.question_label1 = QLabel(self.questionStr)
        layout.addWidget(self.question_label1, 0, 0, 1, 2)
        self.play_button1 = QPushButton('播放音频', self)
        # noinspection PyUnresolvedReferences
        self.play_button1.clicked.connect(self.play_audio)
        layout.addWidget(self.play_button1, 0, 3)
        self.question_main_label1 = QLabel(self.question)
        layout.addWidget(self.question_main_label1, 1, 0, 1, 3)
        if self.mode == 1:
            self.question_main_label1.hide()
        else:
            self.play_button1.hide()
        answer_button = QPushButton('显示答案', self)
        # noinspection PyUnresolvedReferences
        answer_button.clicked.connect(self.show_answer_clicked)
        layout.addWidget(answer_button, 2, 0, 1, 3)
        self.question_page.setLayout(layout)

    def init_answer_page(self):
        layout = QGridLayout()
        self.question_label2 = QLabel(self.questionStr)
        layout.addWidget(self.question_label2, 0, 0, 1, 2)
        self.play_button2 = QPushButton('播放音频', self)
        # noinspection PyUnresolvedReferences
        self.play_button2.clicked.connect(self.play_audio)
        layout.addWidget(self.play_button2, 0, 3)
        self.question_main_label2 = QLabel(self.question)
        layout.addWidget(self.question_main_label2, 1, 0, 1, 3)
        if self.mode == 1:
            self.question_main_label2.hide()
        else:
            self.play_button2.hide()
        self.answer_label = QLabel(self.answer)
        layout.addWidget(self.answer_label, 2, 0, 1, 3)
        wrong_button = QPushButton('混淆', self)
        # noinspection PyUnresolvedReferences
        wrong_button.clicked.connect(self.confuse)
        layout.addWidget(wrong_button, 3, 0)
        forget_button = QPushButton('忘记了', self)
        # noinspection PyUnresolvedReferences
        forget_button.clicked.connect(self.forget)
        layout.addWidget(forget_button, 3, 1)
        correct_button = QPushButton('下一题', self)
        # noinspection PyUnresolvedReferences
        correct_button.clicked.connect(self.correct)
        correct_button.setStyleSheet("background-color: green")
        layout.addWidget(correct_button, 3, 3)
        self.answer_page.setLayout(layout)

    def init_confuse_page(self):
        layout = QGridLayout()
        self.question_label3 = QLabel(self.questionStr)
        layout.addWidget(self.question_label3, 0, 0, 1, 2)
        self.play_button3 = QPushButton('播放音频', self)
        # noinspection PyUnresolvedReferences
        self.play_button3.clicked.connect(self.play_audio)
        layout.addWidget(self.play_button3, 0, 3)
        self.question_main_label3 = QLabel(self.question)
        layout.addWidget(self.question_main_label3, 1, 0, 1, 3)
        if self.mode == 1:
            self.question_main_label3.hide()
        else:
            self.play_button3.hide()
        confuse_label = QLabel('请输入混淆原因')
        layout.addWidget(confuse_label, 2, 0)
        self.confuse_reason = QLineEdit()
        layout.addWidget(self.confuse_reason, 2, 1)
        confuse_button = QPushButton('确定', self)
        # noinspection PyUnresolvedReferences
        confuse_button.clicked.connect(self.confuse_check)
        layout.addWidget(confuse_button, 2, 2)
        # 返回
        back_button = QPushButton('返回', self)
        # noinspection PyUnresolvedReferences
        back_button.clicked.connect(self.show_answer_clicked)
        layout.addWidget(back_button, 3, 0, 1, 3)
        # QMessage
        self.qMessageBox = QMessageBox()
        self.qMessageBox.setText('wait')
        layout.addWidget(self.qMessageBox, 4, 0, 1, 3)
        self.qMessageBox.hide()
        self.confuse_page.setLayout(layout)

    def show_answer_clicked(self):
        self.answer_label.setText(self.answer)
        self.play_audio()
        print(remove_html_tag(self.answer))
        self.used_time = time.time() - self.used_time
        print("用时：", self.used_time)
        self.stacked_widget.setCurrentIndex(2)

    def next_question_clicked(self):
        self.init_question()
        self.question_label1.setText(self.questionStr)
        self.question_label2.setText(self.questionStr)
        self.question_label3.setText(self.questionStr)
        self.question_label1.setFont(QFont('微软雅黑', 20))
        self.question_label2.setFont(QFont('微软雅黑', 20))
        self.question_label3.setFont(QFont('微软雅黑', 20))
        if self.mode == 1:
            self.play_audio()
            self.play_button1.show()
            self.play_button2.show()
            self.play_button3.show()
            self.question_main_label1.hide()
            self.question_main_label2.hide()
            self.question_main_label3.hide()
        else:
            self.play_button1.hide()
            self.play_button2.hide()
            self.play_button3.hide()
            self.question_main_label1.setText(self.question)
            self.question_main_label2.setText(self.question)
            self.question_main_label3.setText(self.question)
            self.question_main_label1.show()
            self.question_main_label2.show()
            self.question_main_label3.show()
        print(remove_html_tag(self.questionStr), remove_html_tag(self.question))
        self.stacked_widget.setCurrentIndex(1)
        self.used_time = time.time()

    def confuse(self):
        self.stacked_widget.setCurrentIndex(3)

    def confuse_check(self):
        reason = self.confuse_reason.text()
        if reason == '':
            QMessageBox.warning(self.qMessageBox, '错误', '请输入混淆原因')
            self.qMessageBox.show()
        # 检查输入是否为空或者是否是片假名、平假名、罗马音
        elif not is_hiragana(reason) and not is_katakana(reason) and not is_romanji(reason):
            QMessageBox.warning(self.qMessageBox, '错误', '输入有误，混淆原因只能是片假名、平假名、罗马音')
            self.qMessageBox.show()
        else:
            self.record.add(self.mode, remove_html_tag(self.question), remove_html_tag(self.answer), 2, reason, self.used_time)
            # 清空输入框和提示
            self.confuse_reason.setText('')
            self.qMessageBox.setText('')
            self.qMessageBox.hide()
            self.next_question_clicked()

    def forget(self):
        self.record.add(self.mode, remove_html_tag(self.question), remove_html_tag(self.answer), 1, "", self.used_time)
        self.next_question_clicked()

    def correct(self):
        self.record.add(self.mode, remove_html_tag(self.question), remove_html_tag(self.answer), 0, "", self.used_time)
        self.next_question_clicked()

    # 初始化题目以及答案，
    # mode：模式 1：听音写平片假名、罗马音 2：看片假写平假、罗马音 3：看平假写片假、罗马音 4：看罗马音写平片假
    def init_question(self):
        # 随机抽取一个罗马音
        romanji, self.mode = self.record.get_question_by_weight()
        self.romanji = romanji
        # 根据模式初始化题目以及答案
        if self.mode == 1:
            # 听音写平片假名、罗马音
            self.questionStr = '请听音，写出平片假名、罗马音'
            self.question = ("<span style='font-family:微软雅黑; font-size:80pt'>" + romanji + "</span>")
            self.answer = (
                        "<span style='font-family:AiharaHudemojiKaisho; font-size:120pt'>"
                        + get_hiragana_by_romanji(romanji) + ' ' + get_katakana_by_romanji(romanji)
                        + "</span><span style='font-family:微软雅黑; font-size:40pt'>    " + romanji + "</span>")
        elif self.mode == 2:
            # 看片假写平假、罗马音
            self.questionStr = '请看片假名，写出平假名、罗马音'
            self.question = ("<span style='font-family:AiharaHudemojiKaisho; font-size:120pt'>" + get_katakana_by_romanji(romanji) + "</span>")
            self.answer = ("<span style='font-family:AiharaHudemojiKaisho; font-size:120pt'>" + get_hiragana_by_romanji(romanji)
                           + "</span><span style='font-family:微软雅黑; font-size:40pt'>    " + romanji + "</span>")
        elif self.mode == 3:
            # 看平假写片假、罗马音
            self.questionStr = '请看平假名，写出片假名、罗马音'
            self.question = ("<span style='font-family:微软雅黑; font-size:120pt'>" + get_hiragana_by_romanji(romanji) + "</span>")
            self.answer = ("<span style='font-family:AiharaHudemojiKaisho; font-size:120pt'>" + get_katakana_by_romanji(romanji)
                           + "</span><span style='font-family:微软雅黑; font-size:80pt'>    " + romanji + "</span>")
        elif self.mode == 4:
            # 看罗马音写平片假
            self.questionStr = '请看罗马音，写出平片假名'
            self.question = ("<span style='font-family:微软雅黑; font-size:80pt'>" + romanji + "</span>")
            self.answer = (
                        "<span style='font-family:AiharaHudemojiKaisho; font-size:120pt'>"
                        + get_hiragana_by_romanji(romanji) + ' ' + get_katakana_by_romanji(romanji) + "</span>")

    # 播放音频
    def play_audio(self):
        if play_audio(self.romanji) != 0:
            print("播放音频失败")


def showdata():
    pass


# 程序入口
if __name__ == '__main__':
    showdata()
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
