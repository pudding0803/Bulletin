# Bulletin
> 網路與資料庫設計的 project：一個留言板

## 環境與資料庫

* 使用技術
  * `PyQt5` + `Qt Designer`
  * `SQLite3` + `DB Brouser for SQLite`

* 資料庫設計
> 可以直接拿我用過的 `Bulletin.db` 🤧

![](https://i.imgur.com/8GqbXej.png)

## 主要頁面與功能

* 個人資料
  * 進行註冊、登入、登出
  * 編輯個人資料
  * 查看貼文、表情符號統計資料

![](https://i.imgur.com/RRLSkyE.png)

* 撰寫貼文
  * 撰寫並發布一則貼文
  * 支援 HTML 語法
  * 登入才能撰寫貼文

![](https://i.imgur.com/4M7DQ18.png)

* 貼文清單
  * 動態顯示所有貼文（含發文者、發文時間）
  * 可照「最近時間」、「最遠時間」、「熱門程度」排序
  * 若沒有名字會顯示 [anonymity]
  * 點擊「Read」可查看貼文詳細內容

![](https://i.imgur.com/lKRH5Pz.png)

* 查看貼文
  * 「發布貼文」或「查看貼文詳細內容」時使用的頁面
  * 可查看貼文相關的詳細資料
  * 支援 HTML 內容顯示
  * 可對貼文留下一種表情符號，可隨時更換或取消

![](https://i.imgur.com/ozvEfMe.png)

## 廢話區

* 全部都寫在 `WindowController.py` 裡面，又髒又亂QQ
* 好久沒在程式碼裡面寫 GUI 的東西了（貼文清單），網頁簡單多了🥺
* 這次跟 SQL 語法更熟了（`JOIN`、`GROUP BY`、Subquery 之類的）
* 設計資料庫和 UI/UX 滿好玩的，但實作前端不好玩🫠
