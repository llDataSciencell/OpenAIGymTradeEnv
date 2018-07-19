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
