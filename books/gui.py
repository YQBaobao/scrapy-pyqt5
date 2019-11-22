# -*- coding: utf-8 -*-
"""
@name:XXX
@Date: 2019/11/9 14:58
@Version: v.0.0
"""

import sys
import icons
from multiprocessing import Process, Manager, freeze_support
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, \
    QPushButton, QTextBrowser, QComboBox, QHBoxLayout, QVBoxLayout

from scrapy.crawler import CrawlerProcess
from books.spiders.book import BookSpider
from scrapy.utils.project import get_project_settings

# import logging
# from twisted.internet import reactor
# from scrapy.crawler import CrawlerRunner
# from scrapy.utils.log import configure_logging

import urllib.robotparser

import scrapy.spiderloader
import scrapy.statscollectors
import scrapy.logformatter
import scrapy.dupefilters
import scrapy.squeues

import scrapy.extensions.spiderstate
import scrapy.extensions.corestats
import scrapy.extensions.telnet
import scrapy.extensions.logstats
import scrapy.extensions.memusage
import scrapy.extensions.memdebug
import scrapy.extensions.feedexport
import scrapy.extensions.closespider
import scrapy.extensions.debug
import scrapy.extensions.httpcache
import scrapy.extensions.statsmailer
import scrapy.extensions.throttle

import scrapy.core.scheduler
import scrapy.core.engine
import scrapy.core.scraper
import scrapy.core.spidermw
import scrapy.core.downloader

import scrapy.downloadermiddlewares.stats
import scrapy.downloadermiddlewares.httpcache
import scrapy.downloadermiddlewares.cookies
import scrapy.downloadermiddlewares.useragent
import scrapy.downloadermiddlewares.httpproxy
import scrapy.downloadermiddlewares.ajaxcrawl
# import scrapy.downloadermiddlewares.chunked
import scrapy.downloadermiddlewares.decompression
import scrapy.downloadermiddlewares.defaultheaders
import scrapy.downloadermiddlewares.downloadtimeout
import scrapy.downloadermiddlewares.httpauth
import scrapy.downloadermiddlewares.httpcompression
import scrapy.downloadermiddlewares.redirect
import scrapy.downloadermiddlewares.retry
import scrapy.downloadermiddlewares.robotstxt

import scrapy.spidermiddlewares.depth
import scrapy.spidermiddlewares.httperror
import scrapy.spidermiddlewares.offsite
import scrapy.spidermiddlewares.referer
import scrapy.spidermiddlewares.urllength

import scrapy.pipelines

import scrapy.core.downloader.handlers.http
import scrapy.core.downloader.handlers.datauri
import scrapy.core.downloader.handlers.file
import scrapy.core.downloader.handlers.s3
import scrapy.core.downloader.handlers.ftp
import scrapy.core.downloader.contextfactory


class CrawlWindows(QWidget):
    def __init__(self):
        super(CrawlWindows, self).__init__()
        self.resize(600, 300)
        self.setWindowIcon(QIcon(':icons/favicon.ico'))
        self.setWindowTitle('Books to scrape (http://books.toscrape.com)')

        self.ua_line = QLineEdit(self)
        self.obey_combo = QComboBox(self)
        self.obey_combo.addItems(['Yes', 'No'])
        # self.save_location = QLineEdit(self)
        self.log_browser = QTextBrowser(self)
        self.crawl_button = QPushButton('Start crawl', self)
        self.crawl_button.clicked.connect(lambda: self.crawl_slot(self.crawl_button))

        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()
        self.h_layout.addWidget(QLabel('Input User-Agent:'))
        self.h_layout.addWidget(self.ua_line)
        # self.h_layout.addWidget(QLabel('Save path'))
        # self.h_layout.addWidget(self.save_location)
        self.h_layout.addWidget(QLabel('Robot protocol:'))
        self.h_layout.addWidget(self.obey_combo)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(QLabel('Output log box:'))
        self.v_layout.addWidget(self.log_browser)
        self.v_layout.addWidget(self.crawl_button)
        self.setLayout(self.v_layout)

        self.p = None
        self.Q = Manager().Queue()
        self.log_thread = LogThread(self)

    def crawl_slot(self, button):
        if button.text() == 'Start crawl':
            self.log_browser.clear()
            self.crawl_button.setText('Stop crawl')
            ua = self.ua_line.text().strip()
            is_obey = True if self.obey_combo.currentText() == 'Yes' else False
            # save_location = self.save_location.text().strip()
            self.p = Process(target=crawl_run, args=(self.Q, ua, is_obey))
            self.log_browser.setText('The collection process is starting...')
            self.p.start()

            self.log_thread.start()
        else:
            self.crawl_button.setText('Start crawl')
            self.p.terminate()

            self.log_thread.terminate()


class LogThread(QThread):
    def __init__(self, gui):
        super(LogThread, self).__init__()
        self.gui = gui

    def run(self) -> None:
        while True:
            if not self.gui.Q.empty():
                self.gui.log_browser.append(self.gui.Q.get())

                # 确保滑动条到底
                cursor = self.gui.log_browser.textCursor()
                pos = len(self.gui.log_browser.toPlainText())
                cursor.setPosition(pos)
                self.gui.log_browser.setTextCursor(cursor)

                if '采集结束' in self.gui.log_browser.toPlainText():
                    self.gui.crawl_button.setText('Start crawl')
                    break

                # 睡眠20ms
                self.msleep(20)


def crawl_run(Q, ua, is_obey):
    # CrawlerProcess
    settings = get_project_settings()
    settings['USER_AGENT'] = ua
    settings['ROBOTSTXT_OBEY'] = is_obey

    process = CrawlerProcess(settings=settings)
    process.crawl(BookSpider, Q=Q)
    process.start()

    """
    # CrawlerRunner
    configure_logging(install_root_handler=False)
    logging.basicConfig(filename='output.log', format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)
    runner = CrawlerRunner(settings={
        'USER_AGENT': ua,
        'ROBOTSTXT_OBEY': is_obey,
        'SAVE_CONTENT': 'books.jl',
        'ITEM_PIPELINES': {
            'books.pipelines.ChanelPipeline': 300,
        },
    })
    d = runner.crawl(BookSpider, Q=Q)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    """


if __name__ == '__main__':
    freeze_support()
    app = QApplication(sys.argv)
    books = CrawlWindows()
    books.show()
    sys.exit(app.exec_())
