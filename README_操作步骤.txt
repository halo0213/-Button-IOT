村长私库：GitHub Pages + Cloudflare Tunnel 安全联机版

所有文件在同一层；BGM已经内嵌 index.html。

1. 本地双击 START_WINDOWS.bat，输入两个不同的口令：玩家专用、GM专用。不要将口令提交到GitHub，也不要发给玩家GM口令。
2. 保持服务器运行；打开新的PowerShell执行：
   cd C:\cloudflared
   .\cloudflared.exe tunnel --url http://localhost:8765
   复制显示的 https://xxxx.trycloudflare.com 网址。
3. 把 index.html、gm.html、bridge.py、START_WINDOWS.bat 更新到仓库。GitHub Pages网址仍为：
   https://halo0213.github.io/-Button-IOT/
   https://halo0213.github.io/-Button-IOT/gm.html
4. 两个页面首次打开时分别填写同一个Tunnel网址、各自专用口令；浏览器仅保留在当前标签页会话中。
5. 需要换Tunnel或口令：F12控制台执行 sessionStorage.clear()，刷新网页重新输入。
6. ESP32接COM7，关闭Arduino串口监视器；服务器、Tunnel、玩家网页必须保持运行。

注意：Quick Tunnel为临时测试，每次重启网址会变。正式活动请配置Cloudflare正式Tunnel并进行联机压力测试。
警告：玩家口令仅用于防止未授权角色接入，任何得到玩家口令的人仍可冒充玩家；不要公开口令。
