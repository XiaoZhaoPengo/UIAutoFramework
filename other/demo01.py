from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# 设置 Appium 的 capabilities
caps = {
    "appium:bundleId": "com.alipay.iphoneclient",
    "appium:automationName": "XCUITest",
    "appium:platformVersion": "17.6.1",
    "appium:udid": "00008130-001660DC34DA001C",
    "platformName": "ios",
    "appium:deviceName": "肖朝鹏的iPhone",
    "appium:includeSafariInWebviews": True,
    "appium:newCommandTimeout": 3600,
    "appium:connectHardwareKeyboard": True
}

# 启动 Appium driver
driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", caps)

# 设置显式等待
wait = WebDriverWait(driver, 20)

def find_element_with_retry(by, value, retries=3):
    for _ in range(retries):
        try:
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except (TimeoutException, StaleElementReferenceException):
            pass
    raise Exception("Element not found after retries")


test_click = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeOther[@name='搜索框']")
test_click.click()


input_field = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeApplication[@name='支付宝']/XCUIElementTypeWindow[1]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther[2]/XCUIElementTypeImage")
input_field.clear()  # 清空输入框内容，如果需要的话
input_field.send_keys("租租鸭")


# 等待搜索按钮可点击并点击
search_click = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeButton[@name='搜索']")
search_click.click()

