import pytest
import allure
from common.log_utils import logger
from common.web_base import WebBase

@pytest.mark.usefixtures("web_driver")
class TestZzy:
    @pytest.mark.parametrize("test_data", WebBase().get_test_data('zzy'))
    @allure.story("百度搜索测试")
    @allure.title("使用关键词 {test_data} 搜索")
    def test_zzy(self, web_driver, test_data):
        """
        参数化测试 Web 应用示例
        """
        with allure.step("打开网页"):
            web_driver.open_url()  # 每次测试前重新加载页面

        web_driver.url = web_driver.get_url('url1')  # 在这里指定使用 url2
        with allure.step(f"开始执行测试用例，测试数据: {test_data}"):
            logger.info(f"开始执行测试用例，测试数据: {test_data}")



        with allure.step("执行测试步骤"):
            web_driver.execute_test_steps('zzy', test_data)
            web_driver.take_screenshot(f"search_result_{test_data}.png")
            result = web_driver.execute_test_steps('zzy', test_data)
            assert result, "执行测试步骤失败"

