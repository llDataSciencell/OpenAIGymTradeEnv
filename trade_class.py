#coding: utf-8
'''
default:2239.65016075
after:2436.87876149

##0.4 40%
635.385700015
711.099316173
'''

import numpy as np
import poloniex
import datetime
import time
import json
import os
import numpy as np
import matplotlib.pyplot as plt


class TradeClass(object):


    def __init__(self):
        self.trade_history=[]
        self.price_history=[]


    def read_cripto_watch_json(self):
        f = open('../DATA/Min-2017-6-1.json', 'r')
        jsonData = json.load(f)
        return jsonData["60"]

    def read_bitflyer_json(self):
        import csv
        history_data=[]
        import csv
        with open(os.environ['HOME']+'/bitcoin/bitflyerJPY_convert.csv', 'r') as f:
            reader=csv.reader(f,delimiter=',')
            header = next(reader)  # ヘッダーを読み飛ばしたい時
            for row in reader:
                history_data.append(float(row[1]))
                #print(float(row[1]))
            return history_data

    def getDataPoloniex(self):
        polo = poloniex.Poloniex()
        polo.timeout = 10
        chartUSDT_BTC = polo.returnChartData('USDT_ETH', period=300, start=time.time() - 1440*60 * 500, end=time.time())#1440(min)*60(sec)=DAY
        tmpDate = [chartUSDT_BTC[i]['date'] for i in range(len(chartUSDT_BTC))]
        date = [datetime.datetime.fromtimestamp(tmpDate[i]) for i in range(len(tmpDate))]
        data = [float(chartUSDT_BTC[i]['open']) for i in range(len(chartUSDT_BTC))]
        return date ,data

    def PercentageLabel(self,Xtrain,yTrain):
        X=[]
        Y=[]
        for i in range(0,len(yTrain)):
            original=Xtrain[i][-1]
            X.append([float(val/original) for val in Xtrain[i]])
            Y.append(float(float(yTrain[i]/Xtrain[i][-1])-1)*100*100)#%*100
        return X,Y

    def TestPercentageLabel(self,Xtrain):
        X=[]
        for i in range(0,len(Xtrain)):
            original = Xtrain[-1]
            X.append([float(val/original) for val in Xtrain])
        return X

    #+30ドル
    def buy(self,pred,money, ethereum, total_money, current_price):
        first_money,first_ethereum,first_total_money = money,ethereum,total_money
        if abs(pred) < 0.0:
            return first_money, first_ethereum, first_total_money
        spend = abs(money * 0.05)
        money -= spend * 1.0000#1.0015
        if money < 0:
            return first_money,first_ethereum,first_total_money
        ethereum += float(spend / current_price)
        total_money = money + ethereum * current_price

        return money, ethereum, total_money

    def sell(self,pred,money, ethereum, total_money, current_price):
        first_money, first_ethereum, first_total_money = money, ethereum, total_money

        if abs(pred) <0.0:
            return first_money, first_ethereum, first_total_money
        spend = abs(ethereum * 0.05)
        ethereum -= spend * 1.0000#1.0015

        if ethereum < 0.0:
            return first_money,first_ethereum,first_total_money
        money += float(spend * current_price)
        total_money = money + float(ethereum * current_price)

        return money, ethereum, total_money
    #abs(pred)にすること！
    def buy_simple(self,pred,money, ethereum, total_money, current_price):
        first_money, first_ethereum, first_total_money = money, ethereum, total_money
        spend = money * 0.5 * (abs(pred)*0.1)
        money -= spend * 1.0000
        if money < 0.0 or abs(pred) < 0.5:
            return first_money,first_ethereum,first_total_money

        ethereum += float(spend / current_price)
        total_money = money + ethereum * current_price

        return money, ethereum, total_money

    def sell_simple(self,pred,money, ethereum, total_money, current_price):
        first_money, first_ethereum, first_total_money = money, ethereum, total_money
        spend = ethereum * 0.5 * (abs(pred)*0.1)
        ethereum -= spend * 1.0000
        if ethereum < 0.0 or abs(pred) < 0.2:
            return first_money,first_ethereum,first_total_money

        money += float(spend * current_price)
        total_money = money + float(ethereum * current_price)

        return money, ethereum, total_money


    # 配列の長さバグかも
    #0.0001だけだと＋30
    #0.001*predで+200ドル
    def simulate_trade(self,price, X_test, model):
        money = 300
        ethereum = 0.01
        total_money = money + np.float64(price[0] * ethereum)
        first_total_money = total_money

        for i in range(0, len(price)):
            print(i)
            current_price = price[i]
            prediction = model.predict(X_test[i])
            pred = prediction[0]
            if pred > 0:
                print("buy")
                money, ethereum, total_money = self.buy_simple(pred,money, ethereum, total_money, current_price)
                print("money"+str(money))
            elif pred <= 0:
                print("sell")
                money, ethereum, total_money = self.sell_simple(pred,money, ethereum, total_money, current_price)
                print("money"+str(money))
        print("FIRST"+str(first_total_money))
        print("FINAL" + str(total_money))
        return total_money

    def update_trading_view(self, current_price, action):
        self.price_history.append(current_price)
        self.trade_history.append(action)


    def draw_trading_view(self):
        data, date = np.array(self.price_history), np.array([idx for idx in range(0, len(self.price_history))])
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(date, data)#,marker='o'
        ax.plot()

        for num in range(0,len(self.price_history)):
            if self.trade_history[num] == 0:
                plt.scatter(date[num], data[num], marker="^", color="green")
            elif self.trade_history[num] == 1:
                plt.scatter(date[num],data[num], marker="v", color="red")

        ax.set_title("Cripto Price")
        ax.set_xlabel("Day")
        ax.set_ylabel("Price[$]")
        plt.grid(fig)
        plt.show(fig)