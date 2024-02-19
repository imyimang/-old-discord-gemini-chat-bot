# 介紹
這是一個根據[Echoshard的專案](https://github.com/Echoshard/Gemini_Discordbot)改造的gemini chat bot

## 指令(預設為黑名單模式)
**以下所有指令都不需要任何prefix或mention**

*注意:以下指令都沒有設定任何權限限制,任何人都能使用*

* blockchannel ➡️ 不再接收當前頻道的訊息(封鎖頻道)
* unblockchannel ➡️ 解除當前頻道的封鎖
* blockserver ➡️ 不再接收當前伺服器**所有頻道**的訊息
* reset ➡️ 清除該用戶的短期記憶
## 注意事項
*私訊(dm channel)和伺服器頻道的使用方法是一模一樣的*

*這個版本是***每則訊息都會回覆**, **不需要mention**。*所以一次太多訊息他會卡住*

*回覆時機器人和真人用戶都會回覆,所以如果你有其他機器人建議用私訊(dm)使用,不然機器人們可能會吵起來*

*blockchannel和unblockchannel指令需要等他處理完前面堆積的api請求才會執行*

**每個用戶的短期記憶是分開的**,*reset只會清空當前使用指令的用戶的短期記憶*

*短期記憶的上限包含機器人的回覆*

*短期記憶僅包含文字回應,不包含圖片回應*
## 前置作業
將需要的機器人設定填入config.json中

這樣就完成前置作業了
