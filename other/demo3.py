from time import sleep
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# 设置 Appium 的 capabilities
caps = {
    "bundleId": "com.alipay.iphoneclient",
    "automationName": "XCUITest",
    "platformVersion": "17.6.1",
    "udid": "00008130-001660DC34DA001C",
    "platformName": "ios",
    "deviceName": "肖朝鹏的iPhone",
    "includeSafariInWebviews": True,
    "newCommandTimeout": 3600,
    "connectHardwareKeyboard": True
}

# 启动 Appium driver
driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", caps)

# 设置显式等待
wait = WebDriverWait(driver, 5, poll_frequency=0.2)  # 等待时间调整为5秒 参数设为 0.2 秒检查一次元素

def find_element_with_retry(by, value, retries=3):
    for _ in range(retries):
        try:
            element = wait.until(EC.element_to_be_clickable((by, value)))
            return element
        except (TimeoutException, StaleElementReferenceException):
            pass
    raise Exception("重试后没有找到元素")

def click_element(by, value):
    while True:
        try:
            element = find_element_with_retry(by, value)
            element.click()
            break
        except StaleElementReferenceException:
            continue

def send_keys_to_element(by, value, keys):
    element = find_element_with_retry(by, value)
    element.send_keys(keys)

# 进行操作
click_element(MobileBy.XPATH, "//XCUIElementTypeOther[@name='搜索框']")
click_element(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='我的小程序']")

# 增加对“我的小程序”元素的特殊处理
def wait_for_myapp_field():
    try:
        element = wait.until(EC.visibility_of_element_located((MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='我的小程序']")))
        element.click()
    except TimeoutException:
        print("The '我的小程序' element was not found or clickable within the timeout period.")

wait_for_myapp_field()

click_element(MobileBy.XPATH, "//XCUIElementTypeCell[@name='租租鸭']")
click_element(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='iPhone 14 Pro Max']")
click_element(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='免押租赁']")
click_element(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='确定']")
click_element(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='免押租赁']")
click_element(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='我已知晓并同意']")
click_element(MobileBy.XPATH, "//XCUIElementTypeButton[@name='同意协议并开通']")

# 请输入支付密码（第一次使用循环点击）
def input_password(password):
    buttons = [find_element_with_retry(MobileBy.XPATH, f"//XCUIElementTypeButton[@name='{num}']") for num in password]
    for button in buttons:
        button.click()

password = ['1', '3', '4', '0', '1', '2']
input_password(password)

click_element(MobileBy.XPATH, "//XCUIElementTypeButton[@name='完成']")
click_element(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='同意协议 免押下单']")
click_element(MobileBy.XPATH, "//XCUIElementTypeButton[@name='同意协议并授权,确认付款，租赁（预授权），付款金额7.00元人民币']")

# 请输入支付密码（第二次使用 send_keys）
send_keys_to_element(MobileBy.ACCESSIBILITY_ID, "密码共6位，已输入0位", '134012')

sleep(5)  # 确保操作完成
# 关闭驱动
driver.quit()
