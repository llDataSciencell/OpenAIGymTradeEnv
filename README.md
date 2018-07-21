# OpenAIGymのトレード用環境

## 使用方法
- FxEnvというディレクトリを作成して、その中にpythonのファイルを展開する。
- FxEnvの一つ上の階層に、以下の内容を追記する。
```python
# FxEnv
register(
    id='FxEnv-v0',
    entry_point='gym.envs.FxEnv:FxEnv',
    max_episode_steps=7200,
)
```

FxEnvのディレクトリの中身の__init__.pyと一つ上の__init__.pyは書く内容が異なるので注意

## TODO
- 行動の選択肢を増やす。信用取引用に変更する。現在のままだと、PASSしか選択肢なくなる傾向がある。

## Memo
- (7200 + 28800)=35000
'''
7200
Reward:0.0
 28800/50000: episode: 4, duration: 806.672s, episode steps: 7200, steps per second: 9, episode reward: -24.050, mean reward: -0.003 [-2.005, 54.071], mean action: 0.999 [0.000, 2.000], mean observation: 265625.230 [0.000, 289719.000], loss: 7220.513672, mean_absolute_error: 2046.584106, mean_q: 3072.209717
<class 'numpy.int64'>
buy
buy_sell9520回　action==0
29159.247087959495
1
'''
