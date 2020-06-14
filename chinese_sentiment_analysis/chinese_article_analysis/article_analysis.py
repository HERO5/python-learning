#!/usr/bin/python
# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import sys
sys.path.append("../chinese_participation")
sys.path.append("../dut_lib/")
sys.path.append("../algorithms/")
from jieba_participator import JiebaParticipator
from dut_extractor import DutExtractor
from dut_extractor_factory import DutExtractorFactory
from bsa_algorithm import BsaAlgorithm

################################################################
# 注释：
# 程序的入口是：string_semantic_analysis和file_semantic_analysis方法
# 返回结果为json串，格式如下：
# {
#     'score' : 1;
#     'score_comment' : '正：正向情感；负：负向情感。情感值越大，情感越强。';
#     'details' : [
#                  {'meaning' : '赞美', 'strength' : 5},
#                  {'meaning' : '佩服', 'strength' : 3}
#                  ]
# }
#
# score字段，是整体的情感得分；
# score_comment字段，是对score含义的注释，正：正向情感；负：负向情感。情感值越大，情感越强。
# details字段，详细的介绍了文本体现出的每个子情感分类的情感度,meaning字段表示子分类，strength表示这个子分类的情感度。
################################################################

COMMENT = "正：正向情感；负：负向情感。情感值越大，情感越强。"

class ArticleAnalysis(object):
    setence_separator_set = set(["。", "？", "！"])
    @staticmethod
    def get_segment_list_from_input_file(file_path):
        input_file = file(file_path, "r")
        segment_list = list()
        segment_partition_list = list()
        line = input_file.readline()
        while line:
            segment_list.append(line.strip())
            line = input_file.readline()
        input_file.close()
        return segment_list

    @staticmethod
    def get_segment_list(input_string):
        segment_list = input_string.split("\n")
        return segment_list

    @staticmethod
    def partition(segment_list):
        segment_partition_list = list()
        for seg in segment_list:
             partition_list = JiebaParticipator.participate(seg)
             segment_partition_list.append(partition_list)
        return segment_partition_list

    @staticmethod
    def semantic_analysis(segment_partition_list, library, algorithm):
        segment_semantic_result = list()
        article_semantic_value = 0
        if library == "dut":
            article_semantic_result = ArticleAnalysis.dut_semantic_analysis(segment_partition_list)
        if algorithm == "bsa_algorithm":
            article_semantic_value = ArticleAnalysis.bsa_algorithm_cal(article_semantic_result)
        result = ArticleAnalysis.combine_result(article_semantic_result, article_semantic_value)

        return result

    @staticmethod
    def combine_result(article_semantic_result, article_semantic_value):
        result_map = dict()
        result_map['score'] = article_semantic_value
        result_map['score_comment'] = COMMENT

        # Get the detail semantics
        meaning_map = dict()
        for segment_result in article_semantic_result:
            for sentence_result in segment_result:
                for word_result in sentence_result:
                    if word_result.has_key('meaning') is False:
                        continue
                    tmp_meaing = meaning_map.get(word_result['meaning'], dict())
                    strength = tmp_meaing.get('strength', 0)
                    strength += int(word_result.get('semantic_strength', 0))
                    tmp_meaing['strength'] = strength
                    meaning_map[word_result['meaning']] = tmp_meaing
        meaning_list = list()
        for item in meaning_map:
            tmp = meaning_map[item]
            tmp['meaning'] = item
            meaning_list.append(tmp)
        result_map['details'] = meaning_list
        return result_map

    @staticmethod
    def dut_semantic_analysis(segment_partition_list):
        dut_extractor = DutExtractorFactory.get_dut_extractor("../dut_lib/dut_sentiment_words.csv")
        total_semantic_value = 0
        article_semantic_result = list()
        for segment in segment_partition_list:
            input_setence_list = list()
            setence = list()
            for word in segment:
                word = word.encode("UTF-8").strip()
                setence.append(word)
                if word in ArticleAnalysis.setence_separator_set:
                    input_setence_list.append(setence)
                    setence = list()
            if len(setence) != 0:
                input_setence_list.append(setence)
            segment_semantic_result = list()
            for setence in input_setence_list:
                result = dut_extractor.get_word_semantic(setence)
                segment_semantic_result.append(result)
            article_semantic_result.append(segment_semantic_result)
        return article_semantic_result

    @staticmethod
    def bsa_algorithm_cal(article_semantic_result):
        bsa_algorithm = BsaAlgorithm("../common_lib/negative_words.txt")
        article_semantic_result = bsa_algorithm.cal_semantic_value(article_semantic_result)
        return article_semantic_result

    # 程序入口2，如果想对一个文本进行情感分析，可以调用file_semantic_analysis这个方法
    @staticmethod
    def file_semantic_analysis(file_path, library, algorithm):
        segment_list = ArticleAnalysis.get_segment_list_from_input_file(file_path)
        segment_partition_list = ArticleAnalysis.partition(segment_list)
        article_result = ArticleAnalysis.semantic_analysis(segment_partition_list, library, algorithm)
        return article_result

    # 程序入口1，如果对一段话进行情感分析，可以调用string_semantic_analysis这个方法
    @staticmethod
    def string_semantic_analysis(input_string, library, algorithm):
        segment_list = ArticleAnalysis.get_segment_list(input_string)
        segment_partition_list = ArticleAnalysis.partition(segment_list)
        article_result = ArticleAnalysis.semantic_analysis(segment_partition_list, library, algorithm)
        return article_result

if __name__ == '__main__':
    article_analysis = ArticleAnalysis()
    result = ArticleAnalysis.string_semantic_analysis("烛花这个电影不很恶心，让人讨厌\n我不讨厌这个电影\n不血腥，不恶心，吃不下饭去\n我不喜欢那种浪漫的电影\n", "dut", "bsa_algorithm")
    print result['score']
    print result['score_comment']
    detail = result['details']
    for item in detail:
        print item['meaning'], item['strength']

