# bilibili-appcache-extract

Project has been moved to and become part of https://github.com/mo-han/mo-han-toolbox.
项目移动并入 https://github.com/mo-han/mo-han-toolbox.

New implementation use PhantomJS to get some of the infomation from online website.
新的实现依赖 PhantomJS 从网站上获取某些信息。

---

Extract videos from offline cache directories of bilibili mobile client app, with names including the videos' title, av IDs and the uploaders' names. 

从B站的手机APP离线缓存目录中提取视频合并为.mp4文件，并在文件名中标注标题、AV号及UP主昵称。

Feed the executable with arguments of directories inside bilibili app's 
cache folder, which could be done either in command-line, or simply 
dragging those directories onto the executable file.

把B站客户端应用的离线下载目录下的文件夹作为参数直接向程序传递即可，既可以在命令行下完成此操作，也可以直接将那些文件夹拖到该程序EXE文件上。

*依赖ffmpeg*
