# 你画我猜 - StableDiffusion AI 画图版

## 使用方法

运行 `main.py` 启动服务器

```bash
python3 main.py
```

然后在浏览器中打开 `localhost:80` 即可

## TODO

- [x] 首页
  - [x] 前端：完成页面框架
  - [x] 前端：填充首页内容
- [ ] 实现注册、登录功能
  - [x] 前端：完成登录页面
  - [x] 后端：完成登录 API
  - [x] 前端：完成注册页面
  - [x] 后端：完成注册 API
  - [x] 后端：完成 SESSION 机制
  - [ ] 后端：完成设置 Cookie 及检查 Cookie 功能
- [x] 实现游戏核心功能
  - [x] 设计游戏主页面
    - [x] 前端：完成游戏主页面
  - [x] 创建自定义模式游戏（测试用）
    - [x] 前端：完成创建游戏页面
    - [x] 后端：完成创建游戏 API
  - [x] 实时更新游戏状态，完成系统通知及猜图功能
    - [x] 文档：完善 API 文档，设计通知等功能实现方式
    - [x] 前端：完成实时更新界面功能
    - [x] 后端：完成通知相关 API
  - [ ] 排行榜、段位
    - [ ] 前端：完成排行榜页面
    - [x] 后端：设计段位变化算法
    - [ ] 后端：完成排行榜及获取段位 API
- [x] 完成匹配模式
  - [x] 创建匹配模式游戏
    - [x] 前端：完善创建游戏页面
    - [x] 后端：完成匹配机制
    - [x] 后端：完成匹配 API
- [x] StableDiffusion 对接
  - [x] 后端：将游戏 API 与 StableDiffusion 对接
- [x] 完成词库功能
  - [x] 前端：完成选词及提交描述功能
  - [x] 后端：完成选词、提交描述 API
  - [x] 后端：检查描述是否符合规则
