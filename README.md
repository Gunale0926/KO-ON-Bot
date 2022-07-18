# MusicBot
A Music Player for Kaiheila.cn

# bot_with_environment 安装说明

## **下载**
[下载地址](https://github.com/CarterGunale/MusicBot/releases) 
<<<点进去后点击下载bot_with_environment.zip

---
## **解压**
注意解压的文件夹<font color=red>不要包含</font>***空格***或者***中文***之类的奇怪东西

示例解压路径： D:\bot_with_environment

---
## **配置 config.json 文件**

### 1. 填写 token
> 获取 bot token [开发者平台直达](https://developer.kaiheila.cn/app/index)
>1. 点击上方的链接进入开发者平台
>2. 点击右上角 *新建应用* 创建一个 bot
>3. 点击刚创建的 bot 
>4. 点击左侧列表的 *机器人*
>5. 复制右侧页面中间的 *Token*


1. 打开 bot_with_environment 目录下的 config.json 文件
2. 将刚刚复制的 *token* 填写到 `token1` 处

### 2. 填写 q_id（可选）
1. 在 `q_id` 处填写QQ号

### 3. 填写 n_phone
1. 在 `n_phone` 处填写网易云音乐的登录账号

### 4. 填写 n_passwd
1. 在 `n_passwd` 处填写网易云音乐的登录密码

### 5. 填写 n_cookies（可选）
>获取网易云音乐cookies（示例使用 Chrome ）
>1. 登录 [网易云音乐](https://music.163.com/) 网页版
>2. 在空白区域 *右键* ，单击 *检查*， 或者按键盘上 *F12* ，打开 开发者工具
>>注：首开 Devtools 有一个切换到中文的提示，请注意切换语言。<br>
>>若点错或忘切换请百度切换方法
>3. 点击顶部菜单栏的 *网络*
>4. 按 *F5* 或 *Ctrl+R* 刷新页面
>5. 在中间列表上翻至顶，找到名为 *music.163.com* 的条目，然后单击 
>6. 单击右侧靠近中上部的 *标头* 选项卡，下翻找到一大串的 *cookie* 键，单击选中，右键点击复制值
1. 在 `n_cookies` 处填写刚刚获得的 cookie

### 6. 填写 q_cookie
1. 在 `q_cookie` 处填写QQ音乐的 cookie，获取方式和网易云基本无异，不多赘述
>选择不启用QQ音乐可不填写

### 7. 选择是否启用 qq_enable 
1. 值为 `0` 时不启用，值为 `1` 时启用

### <font color=yellow>**最后检查一下是否有误删的引号，多余的空格，记得保存文件**</font>

---
## **准备启动 bot**

>找到 `run.bat` 文件<br>
>如果没有选择启用qq音乐点歌可以把 `cd QQMusic` 下方的那一行 `start /MIN npm start` 删了，注意别删错<br>
>记得保存

---
## **启动 bot**
双击 run.bat ，弹出来的询问网络权限都给了就行了

---
到此结束惹
