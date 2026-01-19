軟體工程課程: 版本控制 (Version Control)

海大資工 馬尚彬

# 單元大綱

- 版本控制概念
- GIT基本指令
- GIT分支作法
- 使用遠端儲存庫GitHub
- GitHub Pull Request
- Git/GitHub開發流程

#### 軟體開發步驟、文件與工具

![](_page_2_Figure_2.jpeg)

## 建構管理

- 建構管理(Software Configuration Management, SCM)的主要目標是確 保軟體開發和維護過程中的一致性、可追溯性和可重複性,包含:
  - 版本控制:管理原始程式碼和相關文件的版本,跟蹤變更歷史,以便能夠 準確地回溯到先前的狀態。(Git/GitHub, SVN)
  - 組態控制:確保軟體系統的各個元件和組件按照規定的標準進行配置和管 理。(Chef, Puppet, Ansible)
  - 建構自動化:建立自動化流程來執行建構、測試和部署軟體,以確保產品 的品質。(Jenkins, GitHub Actions, Travis CI)
  - 發布管理:管理軟體產品的發布流程,包括版本號管理、發布策略、更新 管理等。

## 為什麼需要版本控制?

當你撰寫報告時,如果你想備份,你會怎麼做?

![](_page_4_Figure_3.jpeg)

#### 會發生什麼事?

很多版本檔案

![](_page_5_Picture_3.jpeg)

#### 會發生什麼事?

#### 跟別人合作時……

![](_page_6_Figure_3.jpeg)

資料來源:自由軟體鑄造場王家薰,如何使用OpenSource的工具-協助軟體的開發及快速架站

#### 為什麼要版本控制

- 「凡走過必留下痕跡」
  - 追蹤歷程
  - 改了東西,不會改不回來
- 「三個臭皮匠勝過一個諸葛亮」
  - 大家一起改,不會互相干擾
  - 大家一起改,還能清楚知道對方改了什麼

#### 什麼是「版本」?

![](_page_8_Figure_2.jpeg)

# 甚麼是GIT?

- Git 是一種分散式版本的版本控制(Version Control)系統
- 甚麼是版本?
  - 你的(軟體)專案,不管是新增或刪除檔案,亦或是修改檔案內容,都稱之為 一個「版本」
  - 「版本控制系統」,會記錄這些所有的狀態變化,並且可以像搭乘時光機 一樣,隨時切換到過去某個「版本」時候的狀態。

## Git的優點

- 1. 免費、開源
  - Git 是由 Linux 核心的作者 Linus Torvalds 在 2005 年為了管理 Linux 核心程式 碼,僅花了 10 天所開發出來的
- 2. 速度快、檔案體積小
  - Git 特別的設計,在於它並不是記錄版本的差異,而是記錄檔案內容的「快 照」(snapshot)。
- 3. 分散式系統
  - Git 是一款分散式的版控系統(Distributed Version Control)。
  - 大多的 Git 操作也都是在自己電腦本機就可以完成。

# Git系統安裝

- 請到官方網站下載合適的Git版本:
  - <https://git-scm.com/download/win>
  - 安裝過程中可以更換預設編輯器為Notepad++或其他你熟悉的編輯器

![](_page_11_Picture_5.jpeg)

#### Git Bash

- 安裝完成之後,請啟動「Git Bash」
  - Windows系統版本模擬了一個在Linux 世界的Bash

可以右鍵選[Options]->[Text] 改字型(Font)大小

可以試打指令看看: git version

#### 常用終端機命令列指令

| 指令    | 說明        |
|-------|-----------|
| cd    | 切換目錄      |
| pwd   | 取得目前所在的位置 |
| ls    | 列出目前的檔案列表 |
| mkdir | 建立新的目錄    |
| touch | 建立檔案      |
| cp    | 複製檔案      |
| mv    | 移動檔案      |
| rm    | 刪除檔案      |
| clear | 清除畫面上的內容  |

## 設定Git

要開始使用 Git,首先要設定使用者的 Email 信箱以及使用者名稱:

```
user@DESKTOP MINGW64 /e/myprj
$ git config --global user.name "Albert Ma"
user@DESKTOP MINGW64 /e/myprj
$ git config --global user.email "albert@ntou.edu.tw"
```

可以看看Git的目前設定

```
user@DESKTOP MINGW64 /e/myprj
$ git config --list
```

*(*移除設定: *\$ git config --global --unset XX.YY)* 

(user@DESKTOP是老師的帳號與機器名稱)

#### Git Commits

- Git記錄專案在不同時間的狀態,構成一個專案開發的歷程
- 專案中每個記錄版本稱為一個提交(commit)
- 每一次commit可視為專案在一個給定的時間點上的快照(snapshot)

![](_page_15_Picture_5.jpeg)