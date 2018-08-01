import copy
import sys
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from trade_class import TradeClass
import gym
import numpy as np
from functions import *

class FxEnv(gym.Env):
    def __init__(self):
        self.price_idx=0
        self.trade = TradeClass()
        training_set = self.trade.read_bitflyer_json()
        print("price_data idx 0-10" + str(training_set[0:10]))
        print("price_data idx last 10" + str(training_set[-1]))
        self.length_data=len(training_set)

        self.input_len = 400
        self.n_actions = 3
        self.asset_info_len=2
        self.buy_sell_count_len=4
        #TODO
        self.observe_size = self.input_len+self.buy_sell_count_len#+self.asset_info_len  #env.observation_space.shape[0]
        
        self.data = []
        self.y_train = []
        for i in range(self.input_len, self.length_data - 1001):
            # data.append(np.flipud(training_set_scaled[i-60:i]))
            self.data.append(training_set[i - self.input_len:i])
            self.y_train.append(training_set[i])

        self.price = self.y_train
        self.money = 500
        self.before_money = copy.deepcopy(self.money)
        self.cripto = 0.00001
        self.total_money = self.money + np.float64(self.price[0] * self.cripto)
        self.first_total_money = self.total_money
        self.pass_count = 0
        self.buy_sell_count = 0  # buy+ sell -
        self.pass_renzoku_count = 0
        self.buy_sell_fee=0.00001
        self.current_asset = [self.cripto, self.money]
        self.action_space = gym.spaces.Discrete(3)  # 東西南北
        self.MAP=np.array([0 for idx in range(0,self.observe_size)])
        self.inventory=[]
        self.observation_space = gym.spaces.Box(
            low=0,
            high=3,
            shape=self.MAP.shape
        )
        self.begin_total_money=self.money+self.cripto*self.price[0]
        print("LENGTH OF LOOP NUM:"+str(len(self.data)))
        self.buy_inventory=[]
        self.sell_inventory=[]
        self.total_profit=0

    def _reset(self):
        self.price_idx=0
        return self.data[self.price_idx]+[0,0,0,0]#TODO: +self.current_asset
    def _seed(self,seed=None):
        return self.length_data

    def return_lenghth_steps(self):
        return self.length_data

    def _render(self, mode='', close=False):
        #画面への表示　主にGUI
        pass

    def buy_simple(self,money, cripto, total_money, current_price):
            first_money, first_cripto, first_total_money = money, cripto, total_money
            spend = money * 0.1
            money -= spend * (1+self.buy_sell_fee)
            if money <= 0.0:
                return first_money,first_cripto,first_total_money

            cripto += float(spend / current_price)
            total_money = money + cripto * current_price

            return money, cripto, total_money

    def sell_simple(self,money, cripto, total_money, current_price):
        first_money, first_cripto, first_total_money = money, cripto, total_money
        spend = cripto * 0.1
        cripto -= spend * (1+self.buy_sell_fee)
        if cripto <= 0.0:
            return first_money,first_cripto,first_total_money

        money += float(spend * current_price)
        total_money = money + float(cripto * current_price)

        return money, cripto, total_money


    def pass_simple(self,money,cripto,total_money,current_price):
        total_money = money + float(cripto * current_price)
        return money,cripto,total_money

    def buy_lot(self, money, cripto, total_money, current_price):
        first_money, first_cripto, first_total_money = money, cripto, total_money
        spend = current_price * 0.001
        money -= spend * (1 + self.buy_sell_fee)
        EMPTY_MONEY_FLAG=False
        if money <= 0.0:
            EMPTY_MONEY_FLAG=True
            return first_money, first_cripto, first_total_money,EMPTY_MONEY_FLAG

        cripto += float(spend / current_price)
        total_money = money + cripto * current_price

        return money, cripto, total_money, EMPTY_MONEY_FLAG

    def sell_lot(self, money, cripto, total_money, current_price):
        first_money, first_cripto, first_total_money = money, cripto, total_money
        spend = cripto * 0.001
        cripto -= spend * (1 + self.buy_sell_fee)
        EMPTY_MONEY_FLAG=False
        if cripto <= 0.0:
            EMPTY_MONEY_FLAG = True
            return first_money, first_cripto, first_total_money,EMPTY_MONEY_FLAG

        money += float(spend * current_price)
        total_money = money + float(cripto * current_price)

        return money, cripto, total_money,EMPTY_MONEY_FLAG

    def _step(self, action):

        if type(action) is list or type(action) is np.ndarray:
            action=action.tolist()
            action = action.index(max(action))
        else:
            pass
        self.price_idx+=1

        current_price = self.data[self.price_idx][-1]

        self.trade.update_trading_view(current_price, action)

        len_buy=len(self.buy_inventory)
        len_sell=len(self.sell_inventory)
        if len_buy > 40:
            buy_flag = 1
            sell_flag= 0
        elif len_sell > 40:
            buy_flag = 0
            sell_flag= 1
        else:
            buy_flag=0
            sell_flag=0

        buy_sell_array=[len_buy,len_sell,buy_flag,sell_flag]

        #TODO idx + 1じゃなくて良いか？　バグの可能性あり。=>修正済み
        #next_state = getStateFromCsvData(self.data, self.price_idx+1, window_size)
        reward = 0
        if action == 1 and len(self.sell_inventory) > 0 and len(self.buy_inventory) < 50:  # sell
                sold_price = self.sell_inventory.pop(0)
                profit=sold_price - current_price
                reward = profit#max(profit, 0)
                self.total_profit += profit
                print("Buy(空売りの決済): " + str(current_price) + " | Profit: " + str(profit))
        elif action == 1 and len(self.buy_inventory) < 50:  # buy
                self.buy_inventory.append(current_price)
                print("Buy: " + str(current_price))
        elif action == 2 and len(self.buy_inventory) > 0 and len(self.sell_inventory) < 50:  # sell
                bought_price = self.buy_inventory.pop(0)
                profit = current_price - bought_price
                reward = profit  # max(profit, 0)
                self.total_profit += profit
                print("Sell: " + str(current_price) + " | Profit: " + formatPrice(profit))
        elif action == 2 and len(self.sell_inventory) < 50:
                self.sell_inventory.append(current_price)
                print("Sell(空売り): " + formatPrice(current_price))

        print("Reward: "+str(reward))
        print("inventory(sell) : "+str(len(self.sell_inventory)))
        print("inventory(buy)  : "+str(len(self.buy_inventory)))
        if False:#self.price_idx % 50000 == 1000:
            print("last action:" + str(action))
            print("TOTAL MONEY" + str(self.total_money))
            print("100回中passは" + str(self.pass_count) + "回")
            # print("100回中buy_sell_countは" + str(self.buy_sell_count) + "回")
            self.pass_count = 0
            try:
                self.trade.draw_trading_view()
            except:
                pass
        done = True if self.price_idx == self.length_data - 1 else False

        # obs, reward, done, infoを返す
        return self.data[self.price_idx]+buy_sell_array,reward,done,{}

