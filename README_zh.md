# apyllo

apyllo 是 携程开源的配置中心 apollo 的 python 客户端, https://github.com/ctripcorp/apollo

## 功能

- [x] 客户端灰度发布
- [x] 多namespace订阅支持
- [x] 长轮询配置变更和本地同步
- [x] 服务端不可用时可以选择降级到使用本地缓存配置

## 待实现

- [ ] 监听配置变化并可以自由订阅事件

## 安装

### 源码

```
# git clone git@github.com:Colstuwjx/apyllo.git
# python setup.py install
```

### Pypi

Add one line to your requirements.txt:

```
git+http://github.com:Colstuwjx/apyllo.git#egg=apyllo
```

## 用例

具体使用方法见： [examples](https://github.com/Colstuwjx/apyllo/blob/master/examples)
