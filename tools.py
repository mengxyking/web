import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding="UTF-8")
import execjs

# 读取js文件代码并执行
def read_jscode(file, function, parameter=None):  # parameter传的参数是一个元组 参数可能有多个
    with open(file=file, mode='r', encoding='utf-8') as f:
        js_code = f.read()
    JS = execjs.compile(js_code)  # compile后面传入的是js的代码
    if parameter == None:
        ret = JS.call(function)
    elif type(parameter) == tuple:
        ret = JS.call(function, *parameter)
    else:
        ret = JS.call(function, parameter)
    return ret