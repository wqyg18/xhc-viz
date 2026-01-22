# 从算法日志文件生成可视化HTML文件

1. 将算法日志文件放入 `mylog_input/` 目录

2. 执行日志匹配器(输入特定日志文件名)
```bash
make run_log_matcher LOG_FILE=app_2026-01-21.log
```
3. 生成所有的HTML文件(输入特定日志文件名)
```bash
make log_viz_origin_in_out LOG_FILE=app_2026-01-21.log
```
该步骤会生成所有的HTML文件, 保存在 `mylog_output/visualization/original/{log_name}/` 目录下, 其中 `{log_name}` 是日志文件名(不带后缀)

3. 启动http server查看可视化结果
```bash
make run_http_server
```
执行后, 浏览器打开 `http://0.0.0.0:8000/`, 选择`mylog_output/`目录下对应的日志文件名子目录, 再选择想要查看的vehicle_id子目录, 即可查看可视化结果

# 一键完成所有步骤
或者直接运行一键完成所有步骤
```bash
make log_viz_all LOG_FILE=app_2026-01-21.log
```
