import numpy as np
import math
import os
import requests
import json, sys


# prints formatted price
def formatPrice(n):
    return ("-$" if n < 0 else "$") + "{0:.2f}".format(abs(n))


def read_bitflyer_json():
    import csv
    history_data = []
    import csv
    with open(os.environ['HOME'] + '/bitcoin/bitflyerJPY_convert.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        header = next(reader)  # ヘッダーを読み飛ばしたい時
        for row in reader:
            history_data.append(float(row[1]))
        # print(float(row[1]))
        return history_data


# returns the sigmoid
def sigmoid(gamma):
    if gamma < 0:
        return 1 - 1 / (1 + math.exp(gamma))
    return 1 / (1 + math.exp(-gamma))

'''
>>> ccc[:-100:-2]
[299, 297, 295, 293, 291, 289, 287, 285, 283, 281, 279, 277, 275, 273, 271, 269, 267, 265, 263, 261, 259, 257, 255, 253, 251, 249, 247, 245, 243, 241, 239, 237, 235, 233, 231, 229, 227, 225, 223, 221, 219, 217, 215, 213, 211, 209, 207, 205, 203, 201]
>>>

'''

# returns an an n-day state representation ending at time t
# 入力データを作る際も、価格ごとの差分をとってシグモイドに入れている。
def getState(data, idx, window_size):
    n=window_size+1
    t=idx+1
    #t(idx)に+1したのは、
    #aaa[100:200:10] =>[100, 110, 120, 130, 140, 150, 160, 170, 180, 190]で200番目の数字がこぼれてしまうから。
    #idxを+1しておくことで、内包表記が簡単になる。
    #>>> aaa[100:201:10] => [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
    d = t - n + 1
    block = data[d:t + 1] if d >= 0 else -d * [data[0]] + data[0:t + 1]  # pad with t0
    res = []
    for i in range(n - 1):
        res.append(sigmoid(int(block[i + 1] - block[i]) * 0.01))

    return np.array([res])
def getStateLiveMode(price_array):
    #入力->出力で１つ配列が短くなる。
    res=[]
    for i in range(0,len(price_array)-1):
        res.append(sigmoid(int(price_array[i + 1] - price_array[i]) * 0.01))

    return res
def calc_low(data,idx,window_size,one_tick_sec_term):
    if idx <= window_size * (one_tick_sec_term/60):
        #TODO modify
        return [0 for i in range(0,window_size)]
    low_price=[]
    low=float('inf')
    for i in range(idx,idx-(window_size+1)*int(one_tick_sec_term/60),-1):
        if data[i] < low:
            low=data[i]
        if len(low_price) >= window_size:
            #print("data:   ")
            #print(data[idx - (window_size + 1) * int(one_tick_sec_term / 60):idx + 1])
            low_price.reverse()
            #print("low_price array:")
            #print(low_price)
            return low_price
        if i % int(one_tick_sec_term/60) == 0:
            low_price.append(low)
            low = float('inf')


def calc_high(data,idx,window_size,one_tick_sec_term):

    if idx <= window_size * (one_tick_sec_term/60):
        #TODO modify
        return [0 for i in range(0,window_size)]
    high_price=[]
    high=-float('inf')
    for i in range(idx,idx-(window_size+1)*int(one_tick_sec_term/60),-1):
        if data[i] > high:
            high=data[i]
        if len(high_price) >= window_size:
            #print("data:   ")
            #print(data[idx - (window_size + 1) * int(one_tick_sec_term / 60):idx + 1])
            high_price.reverse()
            return high_price
        if i % int(one_tick_sec_term/60) == 0:
            high_price.append(high)
            high = -float('inf')

    high_price.reverse()
    return high_price

'''
data
[286380.0, 286488.0, 286520.0, 286600.0, 286619.0, 286878.0, 286856.0, 286538.0, 286489.0, 286300.0, 286440.0, 286139.0, 286139.0, 286133.0, 286133.0, 286092.0, 286345.0, 286445.0, 286402.0, 286446.0, 286170.0, 286100.0, 285992.0, 285990.0, 285720.0, 285400.0, 285500.0, 285600.0, 285562.0, 285797.0, 286060.0, 286214.0, 286499.0, 286640.0, 286671.0, 286670.0, 286540.0, 286800.0, 286651.0, 286900.0, 286940.0, 286955.0, 286600.0, 286600.0, 286773.0, 286773.0, 287023.0, 286860.0, 286836.0, 286400.0, 286381.0, 286494.0, 286668.0, 286919.0, 286778.0, 286899.0, 286791.0, 286690.0, 286650.0, 286650.0, 286691.0, 286620.0, 286701.0, 286700.0, 286721.0, 286730.0, 286982.0, 286884.0, 286788.0, 286500.0, 286404.0, 286040.0, 285630.0, 285500.0, 285695.0, 285798.0, 285868.0, 285619.0, 285590.0, 285250.0, 284778.0, 284750.0, 284395.0, 284350.0, 284383.0, 284440.0, 284465.0, 284573.0, 284293.0, 284160.0, 284040.0, 284200.0, 284101.0, 284199.0, 283691.0, 284000.0, 284035.0, 283811.0, 283850.0, 283660.0, 283753.0, 283273.0, 282208.0, 281715.0, 281500.0, 280736.0, 280514.0, 280736.0, 280607.0, 280433.0, 281002.0, 280687.0, 281091.0, 281234.0, 281297.0, 281716.0, 281382.0, 282028.0, 282166.0, 282028.0, 281564.0, 281564.0, 281100.0, 280670.0, 280670.0, 280602.0, 280505.0, 280305.0, 279453.0, 278400.0, 277943.0, 277500.0, 277139.0, 276750.0, 276500.0, 277054.0, 277775.0, 277900.0, 278184.0, 278134.0, 278601.0, 278276.0, 278000.0, 277460.0, 277097.0, 277777.0, 278207.0, 278607.0, 279082.0, 280109.0, 280050.0, 279807.0, 279703.0, 280000.0, 279700.0, 280419.0, 280100.0, 280203.0, 280320.0, 279720.0, 279270.0, 279108.0, 278327.0, 279490.0, 280200.0, 279614.0, 279390.0, 279500.0, 279499.0, 279454.0, 279822.0, 280000.0, 279660.0, 279601.0, 279100.0, 278670.0, 278051.0, 278050.0, 278436.0, 278693.0, 277945.0, 277450.0, 277010.0, 277000.0, 276858.0, 277220.0, 277513.0, 277514.0, 277621.0, 278135.0, 278344.0, 277690.0, 277827.0, 278137.0, 278000.0, 277329.0, 277015.0, 276858.0, 276810.0, 276500.0, 276612.0, 276000.0, 275853.0, 276612.0, 276000.0, 276155.0, 276874.0, 277900.0, 277237.0, 277377.0, 277840.0, 278932.0, 279148.0, 278573.0, 278486.0, 278471.0, 278091.0, 277462.0, 277999.0, 278500.0, 278501.0, 278501.0, 278332.0, 279248.0, 279363.0, 278870.0, 278853.0, 278614.0, 278965.0, 279468.0, 280700.0, 281322.0, 280656.0, 280346.0, 279890.0, 280400.0, 280215.0, 280020.0, 279740.0, 279646.0, 279985.0, 280160.0, 280470.0, 280774.0, 280963.0, 280667.0, 280881.0, 280700.0, 281100.0, 281172.0, 281169.0, 281170.0, 281502.0, 281901.0, 282269.0, 282428.0]
low_price
[286139.0, 286092.0, 285992.0, 285400.0, 285562.0, 286540.0, 286600.0, 286600.0, 286381.0, 286690.0, 286620.0, 286700.0, 285630.0, 285500.0, 284395.0, 284350.0, 284040.0, 283691.0, 282208.0, 280514.0, 280433.0, 281234.0, 281100.0, 280305.0, 277139.0, 276500.0, 278000.0, 277097.0, 279082.0, 279700.0, 278327.0, 279390.0, 279454.0, 278050.0, 277010.0, 276858.0, 277621.0, 276858.0, 275853.0, 276000.0, 277237.0, 277462.0, 277999.0, 278614.0, 278965.0, 279890.0, 279646.0, 280667.0, 281100.0, 281901.0]'''
def getStateFromCsvData(data,idx,window_size):
    t=idx+1
    #tはidxに+1したもの。添字の都合。
    #print("getStateFromCsvData"+str(calc_high(data,idx,window_size+1,300)))
    price300_sec_high=getStateLiveMode(calc_high(data,idx,window_size+1,300))
    price3600_sec_high=getStateLiveMode(calc_high(data,idx,window_size+1,3600))
    price86400_sec_high=getStateLiveMode(calc_high(data,idx,window_size+1,86400))
    price300_sec_low=getStateLiveMode(calc_low(data,idx,window_size+1,300))
    price3600_sec_low=getStateLiveMode(calc_low(data,idx,window_size+1,3600))
    price86400_sec_low=getStateLiveMode(calc_low(data,idx,window_size+1,86400))
    #print("price300:　　"+str(price300_sec_high))
    #print("data[] 300/60　　　"+str(data[int(t-window_size*300/60)-1:int(t):int(300/60)]))
    #print("data[] 3600/60    "+str(data[t - window_size * int(3600 / 60) - 1:t:int(3600 / 60)]))
    #print("data[idx]"+str(data[t-1]))
    #print("data[idx]" + str(data[t-50:t]))
    return [np.array(price300_sec_high),np.array(price3600_sec_high),np.array(price86400_sec_high),np.array(price300_sec_low), np.array(price3600_sec_low), np.array(price86400_sec_low)]

def make_input_data(window_size):
    # ローソク足の時間を指定
    # periods = ["60","300"]

    # ローソク足取得
    # １日:86400 1時間:3600　1分 60
    #res3600 = json.loads(requests.get("https://api.cryptowat.ch/markets/bitflyer/btcjpy/ohlc?periods=3600").text)
    res300 = json.loads(requests.get("https://api.cryptowat.ch/markets/bitflyer/btcjpy/ohlc?periods=300").text)
    #res86400 = json.loads(requests.get("https://api.cryptowat.ch/markets/bitflyer/btcjpy/ohlc?periods=86400").text)

    price300_sec_high = [res300["result"]["300"][-idx][2] for idx in range(1, window_size+2)]
    #price3600_sec_high=[res3600["result"]["3600"][-idx][2] for idx in range(1,window_size+2)]
    #price86400_sec_high = [res86400["result"]["86400"][-idx][2] for idx in range(1, window_size+2)]
    price300_sec_low = [res300["result"]["300"][-idx][3] for idx in range(1, window_size+2)]
    #price3600_sec_low=[res3600["result"]["3600"][-idx][3] for idx in range(1,window_size+2)]
    #price86400_sec_low = [res86400["result"]["86400"][-idx][3] for idx in range(1, window_size+2)]

    #print(price300_sec_high)
    #必ずreturnでは複数の配列を返すこと。でないとtestcaseでエラーが出る。
    return getStateLiveMode(price300_sec_high),getStateLiveMode(price300_sec_low)#\
    '''
        ,getStateLiveMode(price3600_sec_high),\
           getStateLiveMode(price86400_sec_low),\
           getStateLiveMode(price3600_sec_low),getStateLiveMode(price86400_sec_low)
    '''
import unittest
from functions import *
window_size = 50
data=read_bitflyer_json()

class TestStringMethods(unittest.TestCase):
    #calc_high,calc_lowはwindow_size+1の長さの配列を返却

    #Liveはwindow_sizeぴったり
    def test_make_input1(self):
        self.assertEqual(len(make_input_data(window_size)[0]), 50)

    def test_getStateCsv(self):
        idx=1000
        self.assertEqual(len(getStateFromCsvData(data, idx, window_size)[0]),50)

    def test_calc_high_low1(self):
        self.assertEqual(len(calc_low(data,1000,window_size,300)),window_size)
    def test_calc_high_low2(self):
        self.assertEqual(len(calc_low(data,1001,window_size,300)),window_size)
    def test_calc_high_low3(self):
        self.assertEqual(len(calc_low(data,1002,window_size,300)),window_size)
    def test_calc_high_low4(self):
        self.assertEqual(len(calc_low(data,1003,window_size,300)),window_size)
    def test_calc_high_low5(self):
        self.assertEqual(len(calc_low(data,1004,window_size,300)),window_size)
    def test_calc_high_low6(self):
        self.assertEqual(len(calc_low(data,1005,window_size,300)),window_size)
    def test_calc_high_low7(self):
        self.assertEqual(len(calc_low(data,1006,window_size,300)),window_size)
    def test_calc_high_low8(self):
        self.assertEqual(len(calc_low(data,1007,window_size,300)),window_size)
    def test_calc_high1(self):
        self.assertEqual(len(calc_high(data,1000,window_size,300)),window_size)
    def test_calc_high2(self):
        self.assertEqual(len(calc_high(data,1001,window_size,300)),window_size)
    def test_calc_high3(self):
        self.assertEqual(len(calc_high(data,1002,window_size,300)),window_size)
    def test_calc_high4(self):
        self.assertEqual(len(calc_high(data,1003,window_size,300)),window_size)
    def test_calc_high5(self):
        self.assertEqual(len(calc_high(data,1004,window_size,300)),window_size)
    def test_calc_high6(self):
        self.assertEqual(len(calc_high(data,1005,window_size,300)),window_size)
    def test_calc_high7(self):
        self.assertEqual(len(calc_high(data,1006,window_size,300)),window_size)
    def test_calc_high8(self):
        self.assertEqual(len(calc_high(data,1007,window_size,300)),window_size)

    def test_calc_high_low1(self):
        self.assertEqual(len(calc_low(data,1000,window_size,86400)),window_size)
    def test_calc_high_low2(self):
        self.assertEqual(len(calc_low(data,1001,window_size,86400)),window_size)
    def test_calc_high_low3(self):
        self.assertEqual(len(calc_low(data,1002,window_size,86400)),window_size)
    def test_calc_high_low4(self):
        self.assertEqual(len(calc_low(data,1003,window_size,86400)),window_size)
    def test_calc_high_low5(self):
        self.assertEqual(len(calc_low(data,1004,window_size,86400)),window_size)
    def test_calc_high_low6(self):
        self.assertEqual(len(calc_low(data,1005,window_size,300)),window_size)
    def test_calc_high_low7(self):
        self.assertEqual(len(calc_low(data,1006,window_size,300)),window_size)
    def test_calc_high_low8(self):
        self.assertEqual(len(calc_low(data,1007,window_size,300)),window_size)
    def test_calc_high1(self):
        self.assertEqual(len(calc_high(data,1000,window_size,300)),window_size)
    def test_calc_high2(self):
        self.assertEqual(len(calc_high(data,1001,window_size,300)),window_size)
    def test_calc_high3(self):
        self.assertEqual(len(calc_high(data,1002,window_size,300)),window_size)
    def test_calc_high4(self):
        self.assertEqual(len(calc_high(data,1003,window_size,300)),window_size)
    def test_calc_high5(self):
        self.assertEqual(len(calc_high(data,1004,window_size,300)),window_size)
    def test_calc_high6(self):
        self.assertEqual(len(calc_high(data,1005,window_size,300)),window_size)
    def test_calc_high7(self):
        self.assertEqual(len(calc_high(data,1006,window_size,300)),window_size)
    def test_calc_high8(self):
        self.assertEqual(len(calc_high(data,1007,window_size,300)),window_size)

    def test_calc_high1(self):
        self.assertEqual(len(calc_high(data, 1008, window_size, 300)), window_size)

    def test_calc_high2(self):
        self.assertEqual(len(calc_high(data, 1009, window_size, 300)), window_size)

    def test_calc_high3(self):
        self.assertEqual(len(calc_high(data, 1010, window_size, 300)), window_size)

    def test_calc_high4(self):
        self.assertEqual(len(calc_high(data, 1011, window_size, 300)), window_size)

    def test_calc_high5(self):
        self.assertEqual(len(calc_high(data, 1012, window_size, 300)), window_size)

    def test_calc_high6(self):
        self.assertEqual(len(calc_high(data, 1013, window_size, 300)), window_size)

    def test_calc_high7(self):
        self.assertEqual(len(calc_high(data, 1014, window_size, 300)), window_size)

    def test_calc_high8(self):
        self.assertEqual(len(calc_high(data, 1015, window_size, 300)), window_size)


    def test_calc_high8(self):
        self.assertEqual(len(calc_high(data, 0, window_size, 300)), window_size)
    def test_calc_high8(self):
        self.assertEqual(len(calc_high(data, 1, window_size, 300)), window_size)

    def test_high_price(self):
        self.assertEqual(calc_high([0 if idx % 3 == 0 else 100 for idx in range(0,3000)],1007,window_size,300)[10],100)

    def test_getState(self):
        self.assertEqual(len(getStateLiveMode(calc_high(data, 1000, window_size+1, 300))),window_size)

    def test_getState(self):
        self.assertEqual(len(getStateLiveMode(calc_high(data, 1, window_size+1, 300))),window_size)

    '''
    def test_make_input2(self):
        self.assertEqual(len(make_input_data(window_size)[1]), 50)
    def test_make_input3(self):
        self.assertEqual(len(make_input_data(window_size)[2]), 50)
    def test_make_input4(self):
        self.assertEqual(len(make_input_data(window_size)[3]), 50)
    def test_make_input5(self):
        self.assertEqual(len(make_input_data(window_size)[4]), 50)
    def test_make_input6(self):
        self.assertEqual(len(make_input_data(window_size)[5]), 50)
    def test_make_input6(self):
        self.assertEqual(len(make_input_data(window_size)), 6)
    def test_make_input6(self):
        print(data[1900:2000])
        self.assertEqual(len(getState_from_csvdata(data, 2000, window_size)),window_size)
    '''

    '''
    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
    '''
if __name__ == '__main__':
    unittest.main()