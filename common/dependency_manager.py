class DependencyManager:
    """
    依赖管理器
    这个类用于管理测试用例之间的依赖关系。在复杂的测试场景中，某些测试用例可能依赖于其他测试用例的结果。
    DependencyManager 可以：
    存储测试用例的输出结果
    检查依赖关系是否满足
    在测试用例之间传递数据
    """
    def __init__(self):
        self.data_store = {}

    def set_data(self, key, value):
        self.data_store[key] = value

    def get_data(self, key):
        return self.data_store.get(key)

    def check_dependency(self, dependency):
        return dependency in self.data_store