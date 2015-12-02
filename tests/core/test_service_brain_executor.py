# -*- coding: utf-8 -*-
import unittest
import kanaria.core.service.brain.executor as executor


class TestServiceBrainExecutor(unittest.TestCase):

    def test_separator_pattern(self):
        separator = executor.BlockSeparator()

        def confirm(vs, ms):
            i = 0
            for m in ms:
                s = m.group()
                self.assertEqual(vs[i], s)
                # print(s)
                i += 1
            self.assertEqual(i, len(vs))

        # mail address
        mails = ["www.xxxx@example.jp", "www-090-xxxx.xx@gmail.com", "090-9999-9999@exweb.xx.jp"]
        matched = separator.pattern_mail.finditer("私のメールアドレスは{0}です。彼のは{1}、彼女のは{2}です。".format(*mails))
        confirm(mails, matched)

        # date
        dates = ["11/21", "1/1", "2015/01/10"]
        matched = separator.pattern_date.finditer("今日は{0}、お正月は{1}、会議の日付は{2}です。".format(*dates))
        confirm(dates, matched)

        # phone number
        phones = ["09099999999", "090-9999-9999", "03-1111-1111", "0311111111"]
        matched = separator.pattern_phone.finditer("私の携帯は{0}か{1}、会社の連絡先は{2}か{3}です。".format(*phones))
        confirm(phones, matched)

    def test_split_by_blank_line(self):
        separator = executor.BlockSeparator()

        text = """
        今日はとてもいい天気でした。

        報告事項は特にありません。

        2015/11/2
        """

        fields = separator.split_by_blank_line(text)
        self.assertEqual(3, len(fields))
        self.assertEqual(executor.DataType.DATE, fields[2].data_type)

    def test_split_by_data_type(self):
        separator = executor.BlockSeparator()

        text = """
        11/1
        お客様より連絡あり。
        okyakusama001@test-company.com
        090-1111-1234
        折り返し連絡してほしいとのことです。
        """

        fields = separator.split_by_data_type(text)
        self.assertEqual(4, len(fields))
        self.assertEqual(executor.DataType.DATE, fields[0].data_type)

    def test_map_letter_to_field(self):
        from kanaria.core.model.letter import Letter
        import pykintone.application_settings.form_field as ff
        body = """
        本日のお仕事

        11/21
        今日もひたすらPythonのコードを書いた。やれやれだぜ。
        もし障害が起きたら以下に連絡をください。
        hoge@gmail.com

        09012221312
        """

        letter = Letter("", body)
        fields = [
            ff.BaseFormField.create("SINGLE_LINE_TEXT", "title", "タイトル"),
            ff.BaseFormField.create("MULTI_LINE_TEXT", "description", "報告内容"),
            ff.BaseFormField.create("DATE", "reported_date", "報告日時"),
            ff.BaseFormField.create("SINGLE_LINE_TEXT", "mail_address", "メールアドレス"),
            ff.BaseFormField.create("SINGLE_LINE_TEXT", "telephone", "電話番号"),
            ff.BaseFormField.create("MULTI_LINE_TEXT", "comment", "コメント")
        ]

        data = executor.map_letter_to_field(letter, fields)
        print(data)
        for n in [f.code for f in fields if f.code != "comment"]:
            self.assertTrue(n in data)
            self.assertTrue(data[n])

