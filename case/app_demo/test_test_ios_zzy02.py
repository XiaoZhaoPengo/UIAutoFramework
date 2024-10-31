
import pytest
import allure
from common.app_base import AppBase
from common.log_utils import logger
from appium.webdriver.common.mobileby import MobileBy

@pytest.mark.usefixtures("ios_driver")
class TestTest_ios_zzy:
    @pytest.mark.parametrize("test_data", AppBase('ios').get_test_data('zzy_app02'))
    @allure.story("支付宝租租鸭小程序测试")
    @allure.title("使用设备 {test_data} 进行支付宝租租鸭小程序测试")
    def test_test_ios_zzy(self, ios_driver, test_data):
        """
        # 参数化测试 支付宝租租鸭小程序测试
        """
        ios_driver.start_driver()  # 确保ios appium驱动已启动
        with allure.step(f"开始执行测试用例，测试数据: {test_data}"):
            logger.info(f"开始执行测试用例，测试数据: {test_data}")

        #with allure.step("启动应用"):
        #    ios_driver.launch_app()

        with allure.step("执行测试步骤"):
            ios_driver.execute_test_steps('zzy_app02', test_data)

        with allure.step("最终结果截图"):
            ios_driver.take_screenshot(f"test_zzy_web_result.png")    

        with allure.step("验证测试结果"):
            # 这里需要根据实际的 app 界面来定位和验证元素
            result_element = ios_driver.wait_for_element(MobileBy.XPATH, "//XCUIElementTypeStaticText[contains(@name, '测试成功')]")
            assert result_element, "测试操作未成功完成"