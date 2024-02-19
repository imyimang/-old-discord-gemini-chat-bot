# 介紹
這是一個根據[Echoshard的專案](https://github.com/Echoshard/Gemini_Discordbot)改造的gemini chat bot

## *此專案已停止更新/維修,新版程式請至[新專案](https://github.com/imyimang/discord-gemini-chat-bot)*
## 指令

### 以下指令都只能在dm channel使用
* 查詢人設 ➡️ 查詢當前設定的機器人人設
* 清空人設 ➡️ 清空當前用戶的人設
* 其他訊息全部都會被判定為設定人設
### 能在一般channel使用
* reset ➡️ 清除該用戶的短期記憶
## 注意事項



**每個用戶的短期記憶是分開的**,*reset只會清空當前使用指令的用戶的短期記憶*

*短期記憶的上限包含機器人的回覆*

*短期記憶僅包含文字回應,不包含圖片回應*
## 前置作業
導入requirements.txt

```
pip install -U -r requirements.txt
```

將需要的機器人設定填入.env中

這樣就完成前置作業了
