import os
import sys
from common.log_utils import logger
from common.config_utils import load_settings
from common.web_base import WebBase
from common.app_base import AppBase

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def execute_test(test_type, test_case, base_instance):
    try:
        logger.info(f"执行{test_type}测试: {test_case}")
        module = __import__(f"case.{test_type}_demo.test_{test_case}", fromlist=['*'])
        
        # 尝试多种可能的类名
        class_names = [
            f"Test{test_case.capitalize()}",
            f"Test{''.join(word.capitalize() for word in test_case.split('_'))}",
            "Test" + ''.join(word.capitalize() for word in test_case.split('_')),
            f"Test{test_case.upper()}"
        ]
        
        test_class = None
        for class_name in class_names:
            if hasattr(module, class_name):
                test_class = getattr(module, class_name)
                break
        
        if test_class is None:
            raise AttributeError(f"无���在模块 'case.{test_type}_demo.test_{test_case}' 中找到合适的测试类")
        
        test_instance = test_class()
        
        # 尝试多种可能的方法名
        method_names = [
            f"test_{test_case}",
            "test_zzy",
            f"test_{test_case.split('_')[-1]}"
        ]
        
        test_method = None
        for method_name in method_names:
            if hasattr(test_instance, method_name):
                test_method = getattr(test_instance, method_name)
                break
        
        if test_method is None:
            raise AttributeError(f"无法在类 '{test_class.__name__}' 中找到合适的测试方法")

        # 获取测试数据
        if test_type == 'web':
            test_data_list = base_instance.get_test_data(test_case)
        else:
            test_data_list = base_instance.get_test_data('app')

        # 对每个测试数据执行测试
        for data in test_data_list:
            test_method(base_instance, data)
    except Exception as e:
        logger.error(f"执行{test_type}测试时出错: {e}")
        raise


def run_single_test(test_type, test_case):
    settings = load_settings()
    logger.info(f"开始执行单个测试用例: 类型={test_type}, 用例={test_case}")

    if test_type == 'web':
        base_instance = WebBase()
    elif test_type == 'app':
        base_instance = AppBase('ios')  # 根据需要修改
    else:
        logger.error(f"未知的测试类型: {test_type}")
        return

    try:
        base_instance.start_driver()
        execute_test(test_type, test_case, base_instance)
    finally:
        base_instance.quit_driver()


def run_multiple_tests(test_cases):
    logger.info("开始执行多个测试用例")
    for test_case in test_cases:
        test_type = test_case['type']
        test_case_name = test_case['case']
        logger.info(f"准备执行测试用例: 类型={test_type}, 用例={test_case_name}")
        try:
            run_single_test(test_type, test_case_name)
            logger.info(f"成功执行测试用例: 类型={test_type}, 用例={test_case_name}")
        except Exception as e:
            logger.error(f"执行测试用例失败: 类型={test_type}, 用例={test_case_name}, 错误={e}")


if __name__ == "__main__":
    # 定义要运行的测试用例
    TEST_CASES = [
        {'type': 'app', 'case': 'ios_zzy'},
        {'type': 'web', 'case': 'zzy_web'}
    ]

    # 运行所有指定的测试用例
    run_multiple_tests(TEST_CASES)
    logger.info("所有测试用例执行完成")