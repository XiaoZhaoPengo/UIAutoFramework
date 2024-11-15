import pytest
import allure
from common.app_base import AppBase
from common.log_utils import logger
from appium.webdriver.common.appiumby import AppiumBy as MobileBy

@pytest.mark.usefixtures("ios_driver")
class TestIosZzy:
    @pytest.mark.parametrize("test_data", AppBase('ios').get_test_data('app'))
    @allure.story("iOS 支付宝租租鸭小程序测试")
    @allure.title("使用设备 {test_data} 进行租赁")
    def test_ios_zzy(self, ios_driver, test_data):
        """
        参数化测试 iOS 支付宝租租鸭小程序
        """
        ios_driver.start_driver()  # 确保驱动已启动
        with allure.step(f"开始执行测试用例，测试数据: {test_data}"):
            logger.info(f"开始执行测试用例，测试数据: {test_data}")

        # with allure.step("启动支付宝应用"):
        #     ios_driver.launch_app()

        with allure.step("执行测试步骤"):
            ios_driver.execute_test_steps('app', test_data)

        with allure.step("最终结果截图"):
            web_driver.take_screenshot(f"test_zzy_web_result.png")
    

        with allure.step("验证租赁结果"):
            # 这里需要根据实际的 app 界面来定位和验证元素
            result_element = ios_driver.wait_for_element(MobileBy.XPATH, "//XCUIElementTypeButton[@name='完成']")
            assert result_element, "租赁操作未成功完成"




