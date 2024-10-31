class ParameterManager:
    """
    参数管理器
    这个类负责管理测试参数。它可以：
    加载测试参数（从配置文件、数据库或其他来源）
    提供参数化测试的数据
    处理不同环境的参数变化
    """
    def __init__(self, parameters):
        self.parameters = parameters

    def get_parameter(self, key):
        return self.parameters.get(key)

    def set_parameter(self, key, value):
        self.parameters[key] = value

    def get_all_parameters(self):
        return self.parameters