import pytest
from run_tests import run_multiple_tests

# 配置要运行的测试
MULTIPLE_TESTS = [
    {'type': 'app', 'case': 'ios_zzy'},  # 先执行 app 测试
    {'type': 'web', 'case': 'zzy_web'}   # 然后执行 web 测试
]

def test_run_multiple():
    run_multiple_tests(MULTIPLE_TESTS)


if __name__ == "__main__":
    pytest.main([__file__, '-v'])