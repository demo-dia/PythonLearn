import logging

# # 获取logger实例，如果参数为空则返回root logger
# logger = logging.getLogger("AppName")
#
# # 指定logger输出格式
# formatter = logging.Formatter('%(asctime)s %(levelname)-6s: %(message)s')
#
# # 文件日志
# # file_handler = logging.FileHandler("test.log")
# # file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
#
# # 控制台日志
# console_handler = logging.StreamHandler(sys.stdout)
# console_handler.formatter = formatter  # 也可以直接给formatter赋值
#
# # 为logger添加的日志处理器
# # logger.addHandler(file_handler)
# logger.addHandler(console_handler)
#
# # 指定日志的最低输出级别，默认为WARN级别
# logger.setLevel(logging.DEBUG)

# 移除一些日志处理器
# logger.removeHandler(file_handler)

# logging.basicConfig(level=logging.DEBUG,
#                     # stream=sys.stdout,
#
#                     format='%(asctime)s %(levelname)s %(filename)s %(funcName)s@%(lineno)d | %(message)s',
#                     datefmt='%H:%M:%S')


# logging.basicConfig(level=logging.DEBUG,
#                     format='\033[1;0m%(asctime)s %(levelname)-5s %(filename)s %(funcName)s@%(lineno)d |\033[1;32m  %(message)s \033[1;0m',
#                     datefmt='%H:%M:%S')
#
# logging.addLevelName(logging.DEBUG, "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))
# logging.addLevelName(logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
# logging.addLevelName(logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
