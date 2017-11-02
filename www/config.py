'''
编写最新配置文件
'''
import config_default

class Dict(dict):
    '''
    简单的dict,但是支持访问X,Y格式
    '''
    def __init__(self,name=(),values=(),**kw):
        super(Dict,self).__init__(**kw)
        for k,v in zip(name,values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

#创建一个以覆盖配置文件为准,从而更新默认配置并返回的函数
def merge(defaults,override):
    r = {}
    for k,v in defaults.items():
        if k in override:
            if isinstance(v,dict):
                r[k] = merge(v,override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r

def toDict(d):
    D = Dict()
    for k,v in d.items():
        D[k] = toDict(v) if isinstance(v,dict) else v
    return D

configs = config_default.configs
try:
    import config_override
    configs = merge(configs,config_override.configs)
except ImportError:
    pass

configs=toDict(configs)
