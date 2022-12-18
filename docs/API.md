# "你说我猜"接口文档

版本：v0.1-alpha4

[TOC]

## 游戏规则

### 角色

- 服务器
- 玩家 A
- 玩家群体 B（1-9 人）

### 玩法

- 【服务器】从【词库】里【随机】选择一个【词语】，发送给【玩家 A】。

- 【玩家 A】根据【词语】写一段【描述】，【描述】尽可能体现【词语】的含义，但不可以使用【词语】中的任何一个【字】或谐音。
- 【玩家 A】将【描述】发送给【服务器】，【服务器】根据【描述】生成一张【图片】。
- 【服务器】将【图片】发送给【玩家群体 B】，【玩家群体 B】观察图片并输入自己猜测的【词语】。
- 若【玩家群体 B】中有一人的【词语】正确，【玩家 A】与【玩家群体 B】中【得出正确词语】的【这个玩家】大量得分，【玩家群体 B】中其他玩家少量减分。
- 若所有人的【词语】均不正确，【玩家 A】减分，【玩家群体 B】均少量得分。
- 【猜测】行为限时，【玩家群体 B】人数越多，限时越短。

## 账号

`/api/account`

### 获取用户名

`/api/account/username`

获取当前用户名，用于 navigator 获取当前登录状态

- 发送
  - 不发送
- 回执
  - `code`: int
  - `message`: string
  - `username`: string

### 登录

`/api/account/login`

- 发送
  - `username`: string
  - `password`: string

- 回执
  - `code`: int
  - `message`: str

### 登出

`/api/account/logout`

登出后当前 SESSION 失效

- 发送
  - 不发送
- 回执
  - `code`: int
  - `message`: str

### 注册

`/api/account/create`

- 发送
  - `username`: string
  - `password`: string
- 回执
  - `code`: int
  - `message`: str

注册后直接登录

### 检查是否已注册，不着急做

`/api/account/check`

### 修改信息，不着急做

`/api/account/update`

### 登出，不着急做

`/api/account/logout`

使 Cookies 中的 SESSION 失效

## 游戏

`/api/game`

### 自定义模式（测试用）

`/api/game/test`

#### 创建游戏

`/api/game/test/create`

创建一个会话，获得一对 Game ID: `host_id`, `guest_id`

- 回执
  - `code`: int
  - `message`: str
  - ~~`host_id`: str~~
  - `guest_id`: str

#### 加入游戏

`/api/game/test/join`

通过 `guest_id` 加入其他人创建的游戏

- 发送
  - `guest_id`
- 回执
  - `code`: int
  - `message`: str

### 匹配模式

`/api/game/match`

#### 开始匹配

`/api/game/match/start`

开始匹配，并获取一个匹配 ID: `match_id`

- 回执
  - `code`: int
  - `message`: str
  - ~~`match_id`: str~~

#### 获取状态（每秒发送一次）

`/api/game/match/status`

通过 `match_id` 获取匹配状态，成功则返回一个角色信息 (`role`) 及角色 ID (`id`)

- 回执
  - `code`: int
  - `message`: str
  - `role`: str
  - ~~`id`: str~~

### 核心功能

#### 获取词语

`/api/game/core/getword`

通过 `host_id` 获取词语，`host_id` 与词语绑定

- 回执
  - `code`: int
  - `message`: str
  - `word`: str

#### 获取图片

`/api/game/core/image`

通过 `host_id` 获取图片 URL

- 回执
  - `code`: int
  - `message`: str
  - `url`: str

#### 提交描述

`/api/game/core/submit`

通过 `host_id` 提交一个描述，若描述符合规则即可开始游戏

- 发送
  - `description`: str
- 回执：
  - `code`: int
  - `message`: str

#### 是否可开始（每秒发送一次）

`/api/game/core/available`

通过 `guest_id` 查询是否可以开始游戏，成功则返回描述及应该开始游戏的时间戳

- 回执
  - `code`: int
  - `message`: str

#### 获取图片及描述

`/api/game/core/description`

通过 `guest_id` 获取图片 URL 及 host 方提交的描述

- 回执
  - `code`: int
  - `message`: str
  - `url`: str
  - `description`: str

#### 提交猜测

`/api/game/core/guess`

通过 `guest_id` 提交词语，服务器返回是否猜测正确

- 发送
  - `guess`: str
- 回执
  - `code`: int
  - `message`: str

#### 获取提示

`/api/game/core/hint`

通过 `guest_id` 获取提示

- 回执
  - `code`: int
  - `message`: str
  - `hint`: str

#### 获取游戏状态

`/api/game/core/status_host`

通过角色 (`role`) 及角色 ID (`id`) 检查游戏是否已完成，若完成则返回一个分数变化，每秒检查一次

- 回执
  - `code`: int
  - `message`: str
  - `status`: int
  - `score_diff`: int

### 排位

`/api/utils`

#### 获取分数

`/api/utils/score`

- 回执
  - `code`: int
  - `message`: str
  - `score`: int

#### 排行榜

`/api/utils/rank`

- 回执
  - `code`: int
  - `message`: str
  -

## API 细节

### 参数类型及格式

- 通用
  - `username`: str, `[A-Za-z0-9_\-\.]{4,16}`
  - `password`: str, `[a-f0-9]{32}`
  - `id`, `host_id`, `guest_id`, `word_id`, `match_id`: str, `[a-f0-9]{32}`
  - `exist`: bool
  - `role`: str, `host` or `guest`
  - `word`: str, 长度不超过 8 个字
  - `description`: str, 长度不超过 16 个字
- 回执
  - `code`: int, 见下方状态码
  - `message`: str，长度不超过 16 个字

### 消息状态码

- 0：成功
- 1xx：服务器错误
  - 100：服务器异常

- 2xx：账号错误
  - 200：账号或密码错误
  - 201：账号已存在
  - 202：未登录

- 3xx：游戏错误
  - 30x：测试功能错误
  - 31x：匹配功能错误
    - 310：匹配中

  - 32x：游戏功能错误

- 4xx：排位信息错误
  - 401：获取分数失败
  - 402：获取排行榜失败

### 游戏状态码

- 0：完成
- 1：未完成
- 2：游戏异常
