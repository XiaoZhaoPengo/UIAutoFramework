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
wait = WebDriverWait(driver, 5)

def find_element_with_retry(by, value, retries=3):
    for _ in range(retries):
        try:
            element = wait.until(EC.element_to_be_clickable((by, value)))
            return element
        except (TimeoutException, StaleElementReferenceException):
            pass
    raise Exception("Element not found after retries")

# 进行操作
search_click = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeOther[@name='搜索框']")
search_click.click()

myapp_field = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='我的小程序']")
myapp_field.click()

zzyapp_click = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeCell[@name='租租鸭']")
zzyapp_click.click()

iphone_click = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='iPhone 14 Pro Max']")
iphone_click.click()

mianya_click = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='免押租赁']")
mianya_click.click()

suerclick = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='确定']")
suerclick.click()

mianya2 = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='免押租赁']")
mianya2.click()

suer2click = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='我已知晓并同意']")
suer2click.click()

suer3click = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeButton[@name='同意协议并开通']")
suer3click.click()

# 请输入支付密码
password = ['1', '3', '4', '0', '1', '2']
for num in password:
    button = find_element_with_retry(MobileBy.XPATH, f"//XCUIElementTypeButton[@name='{num}']")
    button.click()



finish_click = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeButton[@name='完成']")
finish_click.click()

aggre_click = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeStaticText[@name='同意协议 免押下单']")
aggre_click.click()

aggre_click2 = find_element_with_retry(MobileBy.XPATH, "//XCUIElementTypeButton[@name='同意协议并授权,确认付款，租赁（预授权），付款金额7.00元人民币']")
aggre_click2.click()



aggre_click3 = find_element_with_retry(MobileBy.ACCESSIBILITY_ID, "密码共6位，已输入0位")
aggre_click3.send_keys('134012')



