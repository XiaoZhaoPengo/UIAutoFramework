import os
from pathlib import Path
import yaml
from common.log_utils import logger
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any
from jinja2 import Template

# 配置
CONFIG = {
    'yaml_dir': 'yaml_case',
    'case_dir': 'case',
    'web_subdir': 'web_demo',
    'app_subdir': 'app_demo',
}

# 文件已存在时的处理方式
FILE_EXISTS_ACTION = 'skip'  # 可选值: 'skip', 'overwrite', 'rename'

# 在这里设置测试类型和YAML文件名
TEST_TYPE = 'app'  # 或 'web'
YAML_FILE = 'zzy_app02.yaml'  # 确保与实际文件名一致
PLATFORM = 'ios'  # 新增参数，可以是 'ios' 或 'android'，如果不填则默认为 'android'

# 设置是否处理所有YAML文件
PROCESS_ALL_YAML = False  # 如果为True，将忽略TEST_TYPE和YAML_FILE，处理所有YAML文件

@dataclass
class TestCase:
    casename: str
    title: str
    testdata: List[Any]
    locators: List[Dict[str, Any]]

class TestCaseGenerator(ABC):
    def __init__(self, yaml_file: Path):
        self.yaml_file = yaml_file
        self.yaml_data = self.load_yaml()
        self.test_case = self.parse_yaml()

    def load_yaml(self) -> Dict[str, Any]:
        if not self.yaml_file.exists():
            raise FileNotFoundError(f"YAML file '{self.yaml_file}' does not exist")

        encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']

        for encoding in encodings:
            try:
                with self.yaml_file.open('r', encoding=encoding) as file:
                    return yaml.safe_load(file)
            except UnicodeDecodeError:
                continue

        raise ValueError(
            f"Unable to decode the YAML file '{self.yaml_file}' with any of the attempted encodings: {encodings}"
        )

    def parse_yaml(self) -> TestCase:
        try:
            return TestCase(**self.yaml_data)
        except TypeError as e:
            raise ValueError(f"Invalid YAML structure in {self.yaml_file}: {e}")

    @abstractmethod
    def get_subdir(self) -> str:
        pass

    @abstractmethod
    def get_template(self) -> str:
        pass

    def generate(self):
        try:
            template = Template(self.get_template())
            content = template.render(
                class_name=self.test_case.casename.capitalize(),
                function_name=self.test_case.casename.lower(),
                yaml_name=self.yaml_file.stem,
                title=self.test_case.title,
                locators=self.test_case.locators  # 直接传递 locators
            )

            case_dir = Path(CONFIG['case_dir']) / self.get_subdir()
            case_dir.mkdir(parents=True, exist_ok=True)
            case_file = case_dir / f"test_{self.test_case.casename.lower()}.py"

            if case_file.exists():
                if FILE_EXISTS_ACTION == 'skip':
                    logger.warning(f"测试用例文件 '{case_file}' 已存在。跳过生成。")
                    return
                elif FILE_EXISTS_ACTION == 'overwrite':
                    logger.warning(f"测试用例文件 '{case_file}' 已存在。正在覆盖。")
                elif FILE_EXISTS_ACTION == 'rename':
                    i = 1
                    while case_file.exists():
                        case_file = case_dir / f"test_{self.test_case.casename.lower()}_{i}.py"
                        i += 1
                    logger.warning(f"测试用例文件已存在。创建新文件：'{case_file}'")
                else:
                    raise ValueError(f"Invalid FILE_EXISTS_ACTION: {FILE_EXISTS_ACTION}")

            with case_file.open('w', encoding='utf-8') as file:
                file.write(content)

            logger.info(f"测试用例文件 '{case_file}' 已成功生成。")
            logger.debug(f"生成的内容:\n{content}")
        except Exception as e:
            logger.error(f"成测试用例文件时发生错: {e}")
            raise

class WebTestCaseGenerator(TestCaseGenerator):
    def get_subdir(self) -> str:
        return CONFIG['web_subdir']

    def get_template(self) -> str:
        return """
import pytest
import allure
from common.log_utils import logger
from common.web_base import WebBase
import time

@pytest.mark.usefixtures("web_driver")
class Test{{ class_name }}:
    @pytest.mark.parametrize("test_data", WebBase().get_test_data('{{ yaml_name }}'))
    @allure.story("{{ title }}")
    @allure.title("{{ title }} - {test_data}")
    def test_{{ function_name }}(self, web_driver, test_data):
        '''
        {{ title }}
        '''
        web_driver.url = web_driver.get_url('url2')  # 在这里指定使用 url1或url2

        with allure.step(f"开始执行测试用例，测试数据: {test_data}"):
            logger.info(f"开始执行测试用例，测试数据: {test_data}")

        with allure.step("打开网页"):
            web_driver.open_url()
            time.sleep(2)
                    
        with allure.step("执行测试步骤"):
            web_driver.execute_test_steps('{{ yaml_name }}', test_data)
 

        with allure.step("最终结果截图"):
            web_driver.take_screenshot(f"test_zzy_web_result.png") 
"""

class AppTestCaseGenerator(TestCaseGenerator):
    def __init__(self, yaml_file: Path, platform: str = None):
        super().__init__(yaml_file)
        self.platform = platform or PLATFORM or 'android'

    def get_subdir(self) -> str:
        return CONFIG['app_subdir']

    def get_template(self) -> str:
        return '''
import pytest
import allure
from common.app_base import AppBase
from common.log_utils import logger
from appium.webdriver.common.mobileby import MobileBy

@pytest.mark.usefixtures("{{ platform }}_driver")
class Test{{ class_name }}:
    @pytest.mark.parametrize("test_data", AppBase('{{ platform }}').get_test_data('{{ yaml_name }}'))
    @allure.story("{{ title }}")
    @allure.title("使用设备 {test_data} 进行{{ title }}")
    def test_{{ function_name }}(self, {{ platform }}_driver, test_data):
        """
        # 参数化测试 {{ title }}
        """
        ios_driver.start_driver()  # 确保ios appium驱动已启动
        with allure.step(f"开始执行测试用例，测试数据: {test_data}"):
            logger.info(f"开始执行测试用例，测试数据: {test_data}")

        #with allure.step("启动应用"):
        #    {{ platform }}_driver.launch_app()

        with allure.step("执行测试步骤"):
            {{ platform }}_driver.execute_test_steps('{{ yaml_name }}', test_data)

        with allure.step("最终结果截图"):
            ios_driver.take_screenshot(f"test_zzy_web_result.png")    

        with allure.step("验证测试结果"):
            # 这里需要根据实际的 app 界面来定位和验证元素
            result_element = {{ platform }}_driver.wait_for_element(MobileBy.XPATH, "//XCUIElementTypeStaticText[contains(@name, '测试成功')]")
            assert result_element, "测试操作未成功完成"
'''
    def generate(self):
        try:
            template = Template(self.get_template())
            content = template.render(
                class_name=self.test_case.casename.capitalize(),
                function_name=self.test_case.casename.lower(),
                yaml_name=self.yaml_file.stem,
                title=self.test_case.title,
                platform=self.platform
            )

            subdir = self.get_subdir()
            case_dir = Path(CONFIG['case_dir']) / subdir
            case_dir.mkdir(parents=True, exist_ok=True)
            
            file_name = f"test_{self.test_case.casename.lower()}.py"
            file_path = case_dir / file_name

            # 添加文件写入逻辑
            if file_path.exists():
                if FILE_EXISTS_ACTION == 'skip':
                    logger.warning(f"测试用例文件 '{file_path}' 已存在。跳过生成。")
                    return
                elif FILE_EXISTS_ACTION == 'overwrite':
                    logger.warning(f"测试用例文件 '{file_path}' 已存在。正在覆盖。")
                elif FILE_EXISTS_ACTION == 'rename':
                    i = 1
                    while file_path.exists():
                        file_path = case_dir / f"test_{self.test_case.casename.lower()}_{i}.py"
                        i += 1
                    logger.warning(f"测试用例文件已存在。创建新文件：'{file_path}'")
                else:
                    raise ValueError(f"Invalid FILE_EXISTS_ACTION: {FILE_EXISTS_ACTION}")

            with file_path.open('w', encoding='utf-8') as file:
                file.write(content)

            logger.info(f"测试用例文件 '{file_path}' 已成功生成。")
            logger.debug(f"生成的内容:\n{content}")

        except Exception as e:
            logger.error(f"生成测试用例文件时发生错误: {e}")
            raise

def generate_test_cases():
    yaml_dir = Path(CONFIG['yaml_dir'])

    if PROCESS_ALL_YAML:
        yaml_files = list(yaml_dir.glob('*.yaml'))
    else:
        yaml_files = [yaml_dir / YAML_FILE]

    for yaml_file in yaml_files:
        try:
            if not yaml_file.exists():
                logger.error(f"YAML 文件 '{yaml_file}' 不存在")
                continue

            encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
            yaml_content = None

            for encoding in encodings:
                try:
                    with yaml_file.open('r', encoding=encoding) as f:
                        yaml_content = yaml.safe_load(f)
                    break
                except UnicodeDecodeError:
                    continue

            if yaml_content is None:
                logger.error(
                    f"无法使用以下编码解码 YAML 文件 '{yaml_file}'：{encodings}")
                continue

            if PROCESS_ALL_YAML:
                if 'type' not in yaml_content:
                    logger.warning(f"YAML 文件 '{yaml_file}' 不包含 'type' 字段。跳过处理。")
                    continue
                test_type = yaml_content['type']
            else:
                test_type = TEST_TYPE

            if test_type not in ['web', 'app']:
                logger.warning(f"'{yaml_file}' 的测试类型 '{test_type}' 无效。跳过处理")
                continue

            generator_class = WebTestCaseGenerator if test_type == 'web' else AppTestCaseGenerator
            if test_type == 'app':
                generator = generator_class(yaml_file, PLATFORM)
            else:
                generator = generator_class(yaml_file)
            generator.generate()
        except Exception as e:
            logger.error(f"处理 YAML 文件 '{yaml_file}' 时发生错误：{e}")

if __name__ == "__main__":
    generate_test_cases()