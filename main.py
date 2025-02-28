#  create by ourongxing
#  detail url: https://github.com/ourongxing/maimemo-export

import argparse
import codecs
import csv
import os
import sqlite3
import sys

class Generate(object):
    def __init__(self, path):
        self.path = path
        # 连接数据库
        self.maimemo = sqlite3.connect("maimemo.db")
        self.stardict = sqlite3.connect("stardict.db")
        self.stardict_cursor = self.stardict.cursor()

    def exportAll(self, type):
        with open("./墨墨背单词词库名.txt", "r", encoding='utf-8') as f:
            list = f.readlines()
        for i, j in enumerate(list):
            list[i] = list[i].strip('\n')
        self.export(list, type)

    # 导出词库
    def export(self, list, type):
        maimemo = self.maimemo
        cursor = maimemo.cursor()
        for num, book in enumerate(list):
            sql = """
            SELECT vc_vocabulary
            FROM VOC_TB
            INNER JOIN (
            SELECT title,voc_id,chapter_id,`order`
            FROM BK_VOC_TB V
            INNER JOIN BK_CHAPTER_TB C ON V.chapter_id= C.id AND V.book_id IN (
                SELECT original_id FROM BK_TB WHERE name = '%s' ) ) AS tmp ON VOC_TB.original_id = tmp.voc_id
            ORDER BY `order`
            """ % book
            cursor.execute(sql)
            result = cursor.fetchall()
            self.generate(num, book, result, type)
        cursor.close()
        maimemo.close()
        self.stardict_cursor.close()
        self.stardict.close()

    # 获取中文含义
    def get_exp(self, word):
        cursor = self.stardict_cursor
        newword = word.replace("sth.", "").replace("sb.", "")
        # 去除单词中非字母的字符
        newword = (''.join([n for n in newword if n.isalnum()])).lower()
        sql = """
        SELECT translation
        FROM stardict
        WHERE sw = '%s'
        """ % newword
        cursor.execute(sql)
        result = cursor.fetchall()
        # 未找到
        if result == []:
            return "无"
        else:
            return result[0][0]

    def gen_csv(self, book, result):
        if not os.path.exists(self.path + "/csv/"):
            os.makedirs(self.path + "/csv/")
        with codecs.open(self.path + "/csv/" + book + ".csv", "w",
                         "utf_8_sig") as csvfile:
            writer = csv.writer(csvfile)
            for word in result:
                writer.writerows([[word[0], self.get_exp(word[0])]])

    def gen_txt(self, book, result):
        if not os.path.exists(self.path + "/txt/"):
            os.makedirs(self.path + "/txt/")
        with codecs.open(self.path + "/txt/" + book + ".txt", "w",
                         "utf_8_sig") as txtfile:
            for word in result:
                txtfile.write(word[0] + "\n")

    # 创建文件
    def generate(self, num, book, result, _type):
        if (result == []):
            print(str(num + 1) + " 未找到：" + book)
            return
        else:
            print(str(num + 1) + " 生成成功：" + book)

        if _type == "csv":
            self.gen_csv(book, result)
        elif _type == "txt":
            self.gen_txt(book, result)
        else:
            self.gen_csv(book, result)
            self.gen_txt(book, result)


if __name__ == "__main__":
    if os.path.exists("maimemo.db") == False | os.path.exists("stardict.db") == False:
        print(
            "数据库不存在，请下载 release 中的 maimemo_db&stardict_db.zip 文件，解压后分别放入当前文件夹"
        )

    #获取命令行传入的参数
    parser = argparse.ArgumentParser(
        description='用于生成适用于 List 背单词，不背单词，欧陆词典等的自定义词库')
    parser.add_argument('-t',
                        '--type',
                        help='导出的文件类型',
                        default='both',
                        choices=['csv', 'txt', 'both'])
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--all', help='导出墨墨背单词所有词库', action="store_true")
    group.add_argument('-l',
                       '--list',
                       nargs='*',
                       help='词库名，可多个，与其他选项配合使用时，该选项必须放在最后')
    args = parser.parse_args()

    path = "./dict"
    g = Generate(path)
    if args.all:
        g.exportAll(args.type)
    elif args.list == None:
        print("必须输入一个词库名称，使用 -l 词库名")
    else:
        g.export(args.list, args.type)
