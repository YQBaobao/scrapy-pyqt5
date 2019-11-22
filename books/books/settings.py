# -*- coding: utf-8 -*-

BOT_NAME = 'books'

SPIDER_MODULES = ['books.spiders']
NEWSPIDER_MODULE = 'books.spiders'

LOG_LEVEL = 'INFO'
LOG_FILE = 'output.log'

ROBOTSTXT_OBEY = True

SAVE_CONTENT = 'books.jl'
ITEM_PIPELINES = {
    'books.pipelines.ChanelPipeline': 300,
}
