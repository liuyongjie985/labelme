# -*- encoding:utf-8 -*-
import re
import os
from skimage import io as sio
from UIView.main_window import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QCompleter
from random import choice
from urllib.parse import urlencode
import requests
from PIL import Image
from datetime import datetime
from PyQt5.QtCore import Qt


class fun_main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.dic_label = {}
        # self.setWindowIcon(QIcon("D:/pig.ico")) 设置图标
        self.setWindowTitle('标注工具')
        self.total_num = 0
        self.namespace = []
        self.index = 0
        self.all_pic_num = 0
        self.begin_time = datetime.now()
        self.s = requests.session()
        self.dire = None
        self.headers = [
            {
                'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'},
            {
                'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'},
            {'User-Agent': r"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0"},
            {
                'User-Agent': r"Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko"},
            {'User-Agent': r"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"},
            {'User-Agent': r"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)"},
            {
                'User-Agent': r"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"},
            {
                'User-Agent': r"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"},
            {'User-Agent': r"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0"},
            {'User-Agent': r"Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50"},
            {
                'User-Agent': r"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)"},
            {'User-Agent': r"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)"}
        ]
        # 读取文件
        self.actionopen.triggered.connect(self.open)
        self.pushButtonPre.clicked.connect(self.pushButtonPre_click)
        self.pushButton_2.clicked.connect(self.pushButton_2_click)
        self.pushButton_3.clicked.connect(self.pushButton_3_click)
        self.pushButton_ok.clicked.connect(self.pushButton_ok_click)
        # self.init_lineedit()

    def open(self):
        if self.dire:
            with open(os.path.join(self.dire, 'relabel.txt'), 'w', encoding='utf8') as w:
                for line in self.dic_label.keys():
                    w.writelines('{} {}\n'.format(line, self.dic_label[line]))
        self.dire = None
        self.total_num = 0
        self.namespace = []
        self.dic_label = {}
        self.dic_chinese = {}
        self.index = 0
        directory1 = QFileDialog.getExistingDirectory(self,
                                                      "选取文件夹",
                                                      "./")  # 起始路径
        if not directory1:
            return
        self.dire = directory1
        self.statusBar().showMessage(directory1)  # 设置状态栏显示的消息
        if os.path.exists(os.path.join(directory1, 'relabel.txt')):
            tmp_dic = os.path.join(directory1, 'relabel.txt')
        else:
            tmp_dic = os.path.join(directory1, 'res.txt')
        with open(tmp_dic, 'r', encoding='utf8') as f:
            for line in f.readlines():
                line = line.strip()
                index = line.find(' ')
                self.dic_label[line[:index]] = line[index + 1:]
                self.namespace.append(line[:index])
                self.total_num += 1
        chinese_dic = os.path.join(directory1, 'chinese.txt')
        with open(chinese_dic, 'r', encoding='utf8') as f:
            for line in f.readlines():
                line = line.strip()
                index = line.find(' ')
                self.dic_chinese[line[:index]] = line[index + 1:]

        self.total.setText('of %d' % (self.total_num))
        self.all_pic_num += self.total_num
        begin = datetime.now()
        self.show_in_label()
        end = datetime.now()
        print(end - begin)

    def img2pixmap(self, image):
        # Y, X = image.shape[:2]
        # self._bgra = np.zeros((Y, X, 4), dtype=np.uint8, order='C')
        # self._bgra[..., 0] = image[..., 2]
        # self._bgra[..., 1] = image[..., 1]
        # self._bgra[..., 2] = image[..., 0]
        # qimage = QtGui.QImage(self._bgra.data, X, Y, QtGui.QImage.Format_RGB32)
        # pixmap = QtGui.QPixmap.fromImage(qimage)

        img_pil = Image.fromarray(image)
        pixmap = img_pil.toqpixmap()  # QPixmap
        return pixmap

    def preprocess_img(self, image, max_h=64, max_w=1120):
        maxHeight = int(max_h)
        maxWidth = int(max_w)
        height = image.shape[0]
        width = image.shape[1]
        new_height = maxHeight
        new_width = round(width * new_height / height)
        new_width = new_width if new_width < maxWidth else maxWidth
        return new_height, new_width

    def show_img_label1(self):
        ori_img = sio.imread(os.path.join(self.dire, os.path.basename(self.namespace[self.index])))
        # print(os.path.join(self.dire,os.path.basename(self.namespace[self.index])))
        pix_img = self.img2pixmap(ori_img)
        h, w = self.preprocess_img(ori_img)
        print(h, w)
        self.label_img1.setPixmap(pix_img)
        # if w<=1120:
        self.label_img1.move(130 + (1120 - w) // 2, 40)
        self.label_img1.setFixedSize(w, h)
        self.label_img1.setScaledContents(True)

    def show_edit_label(self):
        self.textEdit.setPlainText(self.dic_label[self.namespace[self.index]])

    def show_chinese_label(self):
        self.textChinese.setPlainText(self.dic_chinese[self.namespace[self.index]])

    def show_img_label2(self):
        begin = datetime.now()
        render_img = self.render(self.dic_label[self.namespace[self.index]])
        end = datetime.now()
        print('render time {}'.format(end - begin))
        if isinstance(render_img, str):
            self.label_img2.setText(render_img)
            self.label_img2.move(130 + 200 // 2, 180)
        else:
            pix_img = self.img2pixmap(render_img)
            h, w = self.preprocess_img(render_img)
            print(h, w)
            self.label_img2.setPixmap(pix_img)
            # if w <= 1120:
            self.label_img2.move(130 + (1120 - w) // 2, 180)
            self.label_img2.setFixedSize(w, h)
            self.label_img2.setScaledContents(True)

    def show_in_label(self):
        self.textEdit_2.setPlainText(str(self.index + 1))
        self.textEdit_4.setPlainText(os.path.basename(self.namespace[self.index])[:-4])
        self.show_img_label1()
        self.show_edit_label()
        self.show_chinese_label()
        self.show_img_label2()

    def init_lineedit(self):
        # 增加自动补全
        items_list = [r'\Leftrightarrow', r'\Delta', r'\Longleftrightarrow', r'\Longrightarrow', r'\Pi', r'\Rightarrow',
                      r'\Theta', r'\_', r'\alpha', r'\angle', r'\approx', r'\ast', r'\backslash', r'\beta', r'\bigcirc',
                      r'\bullet', r'\circ', r'\delta', r'\div', r'\downarrow',
                      r'\equiv', r'\frac', r'\gamma', r'\ge', r'\in', r'\lambda', r'\le', r'\leftarrow',
                      r'\leftharpoondown', r'\leftharpoonup', r'\leftrightarrow', r'\leftrightharpoons',
                      r'\longleftarrow', r'\longrightarrow', r'\omega', r'\ominus', r'\oplus', r'\pi', r'\prod',
                      r'\quad', r'\rho', r'\rightarrow', r'\rightharpoondown', r'\rightharpoonup', r'\rightleftarrows',
                      r'\rightleftharpoons', r'\romannumeral', r'\sigma', r'\sim', r'\sqrt', r'\swarrow',
                      r'\textcircled', r'\times', r'\uparrow', r'\upsilon ', r'\varphi', r'\xleftarrow',
                      r'\xlongequal', r'\xrightarrow', r'\xrightleftarrows', r'\xrightleftharpoons', ]
        self.completer = QCompleter(items_list)
        # 设置匹配模式  有三种： Qt.MatchStartsWith 开头匹配（默认）  Qt.MatchContains 内容匹配  Qt.MatchEndsWith 结尾匹配
        self.completer.setFilterMode(Qt.MatchStartsWith)
        # 设置补全模式  有三种： QCompleter.PopupCompletion（默认）  QCompleter.InlineCompletion   QCompleter.UnfilteredPopupCompletion
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        # 给lineedit设置补全器
        self.textEdit.setCompleter(self.completer)

    def pushButtonPre_click(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.total_num - 1
        self.show_in_label()

    def pushButton_2_click(self):
        self.index += 1
        if self.index == self.total_num:
            self.index = 0
        self.show_in_label()

    def pushButton_3_click(self):
        if int(self.textEdit_2.toPlainText()) < 1 or int(self.textEdit_2.toPlainText()) > self.total_num:
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '没有这张图')
            msg_box.exec_()
        else:
            self.index = int(self.textEdit_2.toPlainText()) - 1
            if self.index == self.total_num:
                self.index = 0
            self.show_in_label()

    def pushButton_ok_click(self):
        begin = datetime.now()
        self.dic_label[self.namespace[self.index]] = self.textEdit.toPlainText()
        self.show_img_label2()
        end = datetime.now()
        print(end - begin)

    def render(self, txt):
        begin = datetime.now()
        new = r''
        txt = txt.replace(r'、', r'\,_{、}')
        txt = txt.replace(r'。', r'\,_{。}')
        for i in txt:
            if '\u4e00' <= i <= '\u9fa5' or '\u3400' <= i <= '\u4dbf' or i in [r'＂', r'》', r'《', r'，', r'。', r'！', r'？',
                                                                               r'（', r'）', r'【', r'】', r'：', r'、', r'“',
                                                                               r'‘', r'’', r'”', r'；', r'…']:
                new = new + '\mbox{' + i + '}'
            else:
                new = new + i
        new = re.sub(r'\\xlongequal\s*\[(\s*\\,\s*)*\]\s*\{(\s*\\,\s*)*\}', r'\\xlongequal[\\quad\\quad\\quad]{\\,}',
                     new)
        new = re.sub(r'\\longrightarrow', r'\\xrightarrow[\\quad\\quad\\quad]{\\,}', new)
        new = re.sub(r'\\longleftarrow', r'\\xleftarrow[\\quad\\quad\\quad]{\\,}', new)
        new = re.sub(r'\\rightleftharpoons', r'\\xrightleftharpoons[\\quad\\quad\\quad]{\\,}', new)
        new = new.replace(r'\uppercase \expandafter { \romannumeral', r'\uppercase\expandafter{\romannumeral')
        txt = new
        end = datetime.now()
        print('make latex time {}'.format(end - begin))
        headers = choice(self.headers)
        headers['Content-Type'] = 'application/json; charset=utf-8'
        Para = {'formula': r'\begin{CJK}{UTF8}{gbsn}\rm {%s}\end{CJK}' % txt,
                'remhost': 'quicklatex.com', r'fsize': '40px', 'errors': '1',
                'mode': '0', 'out': '8', 'fcolor': r'000000',
                'preamble': r'''
                        \usepackage{CJK}
                        \usepackage{amsmath}
                        \usepackage{amsfonts}
                        \usepackage{amssymb}
                        \usepackage{extarrows}
                        \usepackage{geometry}
                        \geometry{a2paper,scale=0.8}
                        \usepackage{chemarr}'''}
        # img = self.renderlatex(r'$\begin{CJK}{UTF8}{gbsn}\rm {%s}\end{CJK}$'%txt)

        data = urlencode(Para)
        data = data.replace("+", '%20').encode('utf-8')
        begin = datetime.now()
        start_html = self.time_out(r'https://www.quicklatex.com/latex3.f', headers, data)
        end = datetime.now()
        print('post_time', end - begin)
        if not start_html:
            return '连接超时'
        if start_html.text.split()[0] != '0':
            print(start_html.text.split('\n')[2])
            return '语法错误:{}'.format(start_html.text.split('\n')[2])
        print(start_html.text)
        print(start_html)
        begin = datetime.now()
        print(start_html.text.split()[1])
        img = start_html.text.split()[1]
        # img = sio.imread(start_html.text.split()[1])
        try:
            res = self.s.get(img, timeout=4)
        except:
            return '连接超时'
        end = datetime.now()
        print('read_img_time', end - begin)
        with open('baidu_tieba.jpg', 'wb') as f:
            f.write(res.content)
        img = sio.imread('baidu_tieba.jpg')

        return img

    #
    # def renderlatex(self,formula, fontsize=20, dpi=200, format_='jpg'):
    #     rcParams['text.latex.preamble'] = r'''\usepackage{CJK}
    #                     \usepackage{amsmath}
    #                     \usepackage{amsfonts}
    #                     \usepackage{amssymb}
    #                     \usepackage{extarrows}
    #                     \usepackage{chemarr}'''
    #     #matplotlib.rcParams['text.usetex'] = True
    #     #matplotlib.rcParams['text.latex.unicode'] = True
    #     fig = plt.figure()
    #     fig.text(0, 0, u'{}'.format(formula), fontsize=fontsize,usetex=True)
    #     begin = datetime.now()
    #     f = open("test_image.jpg", "wb")
    #     fig.savefig(f, dpi=dpi,  format=format_, bbox_inches='tight')
    #     img = sio.imread("test_image.jpg")
    #     end = datetime.now()
    #     print('fig_time', end - begin)
    #     return img

    def time_out(self, all_url, headers, data):
        try:
            response = self.s.post(all_url, headers=headers, data=data, timeout=4)
            if response.status_code == 200:
                return response
        except:
            return False

    def closeEvent(self, event):
        if self.dire:
            with open(os.path.join(self.dire, 'relabel.txt'), 'w', encoding='utf8') as w:
                for line in self.dic_label.keys():
                    w.writelines('{} {}\n'.format(line, self.dic_label[line]))
            end_time = datetime.now()
            spend_time = end_time - self.begin_time
            spend_time = str(spend_time).split('.')[0].split(':')
            print(spend_time)
            QMessageBox.about(self, '完成', '本次标注{}小时{}分钟{}秒，共标注{}张。'.format(spend_time[0], spend_time[1], spend_time[2],
                                                                           self.all_pic_num))
            event.accept()
