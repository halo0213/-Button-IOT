村长私库 · 2026-10-28 修正版

1. BGM已直接嵌入index.html，不再需要bgm文件夹。三段音频：规则/五关/Bonus，按游戏状态循环。
2. 第三关 2:20，第四关 1:35，第五关 1:05，Bonus 2:20。
3. 前五关保留原本的0/10警示，达到10/10进入Bonus。
4. Bonus独立从0/8警示开始。按错、松手或超时 +1并重开Bonus；8/8才结束。
5. 成功或Bonus失败回到规则BGM。
6. GitHub网页上传单文件上限通常25MB；index.html约73MB，需使用Git命令行推送，GitHub仓库单文件硬上限100MB。
7. GitHub Pages不支持运行bridge.py；GM与实体ESP32仍需运行本地Python服务器，不能只靠GitHub Pages。
8. 服务器GM指令尚未验证身份，勿直接公网开放。
