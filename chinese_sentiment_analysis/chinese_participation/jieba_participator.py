#!/usr/bin/python
# encoding=utf8
import sys
from importlib import reload

reload(sys)
#Python3字符串默认编码unicode, 所以sys.setdefaultencoding也不存在了
# sys.setdefaultencoding('utf8')
import jieba

class JiebaParticipator(object):
    @staticmethod
    def participate(setence):
        seg_list = jieba.cut(setence, cut_all = False)
        return seg_list

if __name__ == '__main__':
    seg_list = JiebaParticipator.participate("今天的电影很不好看,看的非常不开心。你呢？怎么样？")
    for item in seg_list:
        print(item)
