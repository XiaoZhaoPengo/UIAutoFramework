from time import sleep

import pytest
import allure
from common.log_utils import logger
from common.web_base import WebBase
import time

@pytest.mark.usefixtures("web_driver")
class TestZzyWeb:
    @pytest.mark.parametrize("test_data", WebBase().get_test_data('zzy_web'))
    @allure.story("管理员登录和审核流程测试")
    @allure.title("使用用户名 {test_data} 进行审核")
    def test_zzy_web(self, web_driver, test_data):
        """
        管理员登录和审核流程测试
        """

        web_driver.url = web_driver.get_url('url2')  # 在这里指定使用 url2

        with allure.step(f"开始执行测试用例，测试数据: {test_data}"):
            logger.info(f"开始执行测试用例，测试数据: {test_data}")

        with allure.step("打开网页"):
            web_driver.open_url()
            time.sleep(1)

        with allure.step("执行测试步骤"):
            web_driver.execute_test_steps('zzy_web', test_data)

        with allure.step("最终结果截图"):
        web_driver.take_screenshot(f"test_zzy_web_result.png")

