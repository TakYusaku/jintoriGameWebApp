# -*- coding: utf-8 -*-

import datetime
import dateutil.parser
import pytz

###############################################################
# Date関連
def date_to_date(datetime_obj):
    """
    datetime型もしくはdate型をうけとり所定の日付文字列で返す関数
    """
    date_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    return  date_str

def date_to_str(datetime_obj):
    """
    datetime型もしくはdate型をうけとりDateのみの日付文字列で返す関数
    """
    date_str = datetime_obj.strftime('%Y-%m-%d')
    return  date_str

def date_calc(date_str, delta_date):
    """
    日付計算の便利関数
    :param date_str: 所定の日付形式
    :param delta_date: 計算したい日付　範囲は整数
    :return: 計算後の所定の日付形式
    """
    target_date = dateutil.parser.parse(date_str)
    date_temp = target_date + datetime.timedelta(days=delta_date)
    date_str_changed = date_to_str(date_temp)
    return date_str_changed

def get_japantime_now():
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    return now

def get_japantime_today():
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    today = now.strftime('%Y-%m-%d')
    return today