import os
import yaml
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from appium.webdriver.common.mobileby import MobileBy
from common.log_utils import logger
import allure
import time

class Locator:
    def __init__(self, driver):
        self.driver = driver

    def find_element(self, by, value, timeout=3):
        """
        查找元素并返回
        """
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            logger.error(f"⏳ 超时：未能在 {timeout} 秒内找到元素 '{value}'")
            return None

    def find_element_to_be_clickable(self, by, value, timeout=3):
        """
        等待元素可点击并返回该元素
        """
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        except TimeoutException:
            logger.error(f"⏳ 超时：元素 '{value}' 在 {timeout} 秒内未变为可点击状态")
            return None

    def find_elements(self, by, value, timeout=3):
        """
        查找多个元素并返回列表
        """
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except TimeoutException:
            logger.error(f"⏳ 超时：未能在 {timeout} 秒内找到元素集 '{value}'")
            return []

class AppBase:
    def __init__(self, platform):
        self.platform = platform.lower()
        self.config = self.load_settings()
        self.caps = self.get_capabilities(self.platform)
        self.driver = None
        self.locator = None
        self.wait = None

    def start_driver(self):
        if not self.driver:
            appium_server_url = self.config.get('appui', {}).get('appium_server_url')
            if not appium_server_url:
                logger.error("❌ 未找到 Appium 服务器 URL 配置")
                raise ValueError("Appium 服务器 URL 未配置")
            
            logger.info(f"🚀 正在启动 Appium 驱动，URL: {appium_server_url}")
            self.driver = webdriver.Remote(appium_server_url, self.caps)
            self.locator = Locator(self.driver)
            self.wait = WebDriverWait(self.driver, 5)
        return self.driver

    def quit_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("👋 退出了驱动")

    def load_settings(self):
        """加载配置文件"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        settings_path = os.path.join(project_root, 'config', 'setting.yaml')
        
        try:
            with open(settings_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.error(f"❌ 配置文件未找到：{settings_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"❌ 解析YAML文件时出错：{e}")
            return {}

    def get_capabilities(self, platform):
        if platform not in self.config:
            logger.error(f"❌ 配置中未找到平台 '{platform}'")
            raise Exception(f"配置中未找到平台 '{platform}'")
        return self.config[platform]['capabilities']

    def wait_for_element(self, by, value, timeout=5):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"元素在 {timeout} 秒内未到: {value}")
            return None

    def click_element(self, by, locator):
        """
        点击元素
        """
        element = self.wait_for_element(by, locator)
        if element:
            element.click()
            logger.info(f"👆 点击了元素：{locator}")
        else:
            logger.error(f"❌ 未能点击元素：{locator}")

    def send_keys(self, by, locator, value):
        """
        向元素输入文字
        """
        element = self.wait_for_element(by, locator)
        if element:
            element.send_keys(value)
            logger.info(f"⌨️ 向元素 {locator} 输入了文字：{value}")
        else:
            logger.error(f"❌ 未能向元素 {locator} 输入文字")

    def swipe(self, start_x, start_y, end_x, end_y, duration=800):
        """
        滑动屏幕
        """
        self.driver.swipe(start_x, start_y, end_x, end_y, duration)
        logger.info(f"👆 执行了滑动操作：({start_x}, {start_y}) -> ({end_x}, {end_y})")

    def take_screenshot(self, filename, category='app'):
        """
        截图
        :param filename: 截图文件名
        :param category: 截图类别，默认为 'app'
        """
        base_dir = os.path.join('reports', 'screenshots', category)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        if not filename.endswith('.png'):
            filename += '.png'
        screenshot_path = os.path.join(base_dir, filename)
        try:
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"📸 屏幕截图已保存: {screenshot_path}")
        except Exception as e:
            logger.error(f"❌ 保存屏幕截图时发生错误: {e}")

    def close_app(self):
        """
        关闭应用
        """
        self.driver.close_app()
        logger.info("🚪 关闭了应用")

    def launch_app(self):
        """
        启动应用
        """
        self.driver.launch_app()
        logger.info("🚀 启动了应用")

    def scroll_to_element(self, by, locator, timeout=5):
        """
        滚动到指定元素
        """
        try:
            element = self.locator.find_element(by, locator, timeout)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            logger.info(f"🔍 滚动到了元素：{locator}")
        except (TimeoutException, NoSuchElementException):
            logger.error(f"❌ 未能在 {timeout} 秒内找到并滚动到元素：{locator}")

    def handle_alert(self, action='accept'):
        """
        处理弹窗
        """
        try:
            alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            if action == 'accept':
                alert.accept()
                logger.info("✅ 接受了弹窗")
            elif action == 'dismiss':
                alert.dismiss()
                logger.info("❌ 取消了弹窗")
        except TimeoutException:
            logger.warning("⚠️ 未在指定时间内找到弹窗")

    def check_network_status(self):
        """
        检查网络状态
        """
        network_status = self.driver.execute_script("return navigator.onLine;")
        status = "在线" if network_status else "离线"
        logger.info(f"🌐 网络状态：{status}")
        return network_status

    def interact_with_slider(self, by, locator, value):
        """
        操作滑块控件
        """
        slider = self.wait_for_element(by, locator)
        if slider:
            self.driver.execute_script("arguments[0].value = arguments[1];", slider, value)
            logger.info(f"👆 设置滑块 {locator} 的值为 {value}")
        else:
            logger.error(f"❌ 未能操作滑块：{locator}")

    def execute_javascript(self, script, *args):
        """
        执行 JavaScript 代码
        """
        result = self.driver.execute_script(script, *args)
        logger.info(f"🖥️ 执行了 JavaScript：{script[:50]}...")

        return result

    def wait_for_element_to_disappear(self, by, value, timeout=5):
        """
        等待元素消失
        """
        try:
            WebDriverWait(self.driver, timeout).until_not(
                EC.presence_of_element_located((by, value))
            )
            logger.info(f"🕳️ 元素已消失：{value}")
        except TimeoutException:
            logger.error(f"⏳ 超时：元素 '{value}' 在 {timeout} 秒内未消失")

    def get_element_text(self, by, value):
        """
        获取元素文本
        """
        element = self.wait_for_element(by, value)
        if element:
            text = element.text
            logger.info(f"📝 获取到元素 {value} 的文本：{text}")
            return text
        else:
            logger.error(f"❌ 未能获取元素 {value} 的文本")
            return None

    def is_element_present(self, by, value):
        """
        检查元素是否存在
        """
        try:
            self.driver.find_element(by, value)
            logger.info(f"✅ 元素存在：{value}")
            return True
        except NoSuchElementException:
            logger.info(f"❌ 元素不存在：{value}")
            return False

    def wait_and_tap(self, by, value, timeout=5):
        """
        等待并点击元素
        """
        element = self.wait_for_element(by, value, timeout)
        if element:
            element.click()
            logger.info(f"👆 等待并点击了元素：{value}")
        else:
            logger.error(f"❌ 未能等待到并点击元素：{value}")

    def get_page_source(self):
        """
        获取页面源代码
        """
        source = self.driver.page_source
        logger.info("📄 获取了页面源代码")
        return source

    def reset_app(self):
        """
        重置应用
        """
        self.driver.reset()
        logger.info("🔄 重置了应用")

    def set_network_connection(self, connection_type):
        """
        设置网络连接类型
        """
        self.driver.set_network_connection(connection_type)
        logger.info(f"🌐 设置了网络连接类型：{connection_type}")

    def get_device_time(self):
        """
        获取设备时间
        """
        device_time = self.driver.device_time
        logger.info(f"🕰️ 获取到设备时间：{device_time}")
        return device_time

    def hide_keyboard(self):
        """
        隐藏键盘
        """
        if self.driver.is_keyboard_shown():
            self.driver.hide_keyboard()
            logger.info("⌨️ 隐藏了键盘")
        else:
            logger.info("ℹ️ 键盘已经是隐藏状态")

    def ios_specific_method(self):
        """
        iOS 特有方法
        """
        if self.platform != "ios":
            logger.error("❌ 此方法仅适用于 iOS")
            raise Exception("此方法仅适用于 iOS")
        # 在此处添加 iOS 特有的操作
        logger.info("🍏 执行了 iOS 特有操作")

    def android_specific_method(self):
        """
        Android 特有方法
        """
        if self.platform != "android":
            logger.error("❌ 此方法仅适用于 Android")
            raise Exception("此方法仅适用于 Android")
        # 在此处添加 Android 特有的操作
        logger.info("🤖 执行了 Android 特有操作")

    def read_case_yaml(self, yaml_case):
        """
        读取 YAML 用例文件
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        yaml_case_path = os.path.join(project_root, 'yaml_case', f'{yaml_case}.yaml')
        
        logger.info(f"📂 尝试读取 YAML 文件：{yaml_case_path}")
        
        if not os.path.isfile(yaml_case_path):
            logger.error(f"❌ 未找到用例 '{yaml_case}' 的 YAML 文件")
            return None

        try:
            with open(yaml_case_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                logger.info(f"✅ 成功加载 YAML 数据：{yaml_case}")
                return data
        except yaml.YAMLError as e:
            logger.error(f"❌ 解析 YAML 文件时出错：{e}")
            return None

    def get_test_data(self, yaml_case):
        case_data = self.read_case_yaml(yaml_case)
        if not case_data:
            return []
        return case_data.get('testdata', [])

    def get_case_title(self, yaml_case):
        case_data = self.read_case_yaml(yaml_case)
        if not case_data:
            return None
        return case_data.get('title', '')

    def find_element_with_retry(self, by, value, retries=2, timeout=10):
        for attempt in range(retries + 1):
            try:
                if by == 'COORDINATES':
                    x, y = map(int, value.split(','))
                    self.driver.tap([(x, y)], 100)  # 使用 tap 方法，持续时间设为 100 毫秒
                    time.sleep(1)  # 点击后等待 1 秒
                    logger.info(f"✅ 成功点击坐标：{value}")
                    return True
                else:
                    by_type = getattr(MobileBy, by.upper())
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((by_type, value))
                    )
                    logger.info(f"✅ 成功找到元素：{value}")
                    return element
            except Exception as e:
                if attempt < retries:
                    logger.warning(f"⚠️ 第 {attempt + 1} 次尝试查找元素 {value} 失败，错误：{e}，正在重试...")
                    time.sleep(1)  # 重试前等待 1 秒
                else:
                    logger.error(f"❌ 在 {retries} 次重试后仍未找到元素：{value}，错误：{e}")
        return None

    def execute_step(self, step, test_data):
        """
        执行单个步骤
        """
        logger.debug(f"🔍 执行步骤: {step}")
        by = step.get('by')
        value = step.get('value')
        action = step.get('action')
        info = step.get('info', '')
        optional = step.get('optional', False)
        sleep_time = step.get('sleep')  # 获取 sleep 时间
        

        if not all([by, value, action]):
            logger.error(f"❌ 步骤缺少必要的信息: {step}")
            return False

        logger.info(f"🚀 执行操作: {info}, 定位方式: {by}, 定位值: {value}, 操作: {action}")

        try:
            # 处理 value 中的测试数据
            if isinstance(value, str) and '{test_data}' in value:
                value = value.format(**test_data)

            if by == 'COORDINATES':
                x, y = map(int, value.split(','))
                self.driver.tap([(x, y)], 100)
                logger.info(f"👆 点击了坐标：{value}")
            else:
                element = self.find_element_with_retry(by, value)

                if element is None:
                    if optional:
                        logger.warning(f"⚠️ 可选元素未找到: {value}")
                        return True
                    else:
                        logger.error(f"❌ 必选元素未找到: {value}")
                        return False

                if action == 'click':
                    element.click()
                    time.sleep(1)  # 点击后等待 1 秒
                    logger.info(f"👆 点击了元素：{value}")
                elif action == 'send_keys':
                    input_text = step.get('input', '')
                    if isinstance(input_text, str) and '{' in input_text and '}' in input_text:
                        input_text = input_text.format(**test_data)
                    element.send_keys(input_text)
                    logger.info(f"⌨️ 向元素 {value} 输入了文字")
                elif action == 'input_password':
                    self.input_password(self.driver, value)
                else:
                    logger.error(f"❌ 不支持的操作: {action}")
                    return False

            # 执行 sleep
            if sleep_time:
                time.sleep(float(sleep_time))
                logger.info(f"⏳ 等待 {sleep_time} 秒")

            return True
        except Exception as e:
            logger.error(f"❌ 执行步骤时出错: {e}")
            logger.error(f"错误发生时的变量状态: by={by}, value={value}, action={action}, test_data={test_data}")
            screenshot_path = f"screenshots/{step.get('step', 'screenshot')}.png"
            self.take_screenshot(screenshot_path, category='app')
            allure.attach.file(screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
            if not optional:
                raise
            logger.warning(f"⚠️ 可选步骤执行失败，继续执行下一步: {step}")
            return False

    def execute_test_steps(self, yaml_case, test_data):
        """
        执行测试用例的所有步骤
        """
        case_data = self.read_case_yaml(yaml_case)
        if not case_data:
            logger.error(f"❌ 无法读取测试用例数据: {yaml_case}")
            return False

        logger.debug(f"📂 加载的用例数据: {case_data}")

        locators = case_data.get('locators', [])
        for step_index, step in enumerate(locators, start=1):
            step_info = step.get('info', step.get('step', f'执行步骤-{step_index}'))
            max_retries = 3
            for retry in range(max_retries):
                try:
                    with allure.step(f"步骤 {step_index}: {step_info}"):
                        success = self.execute_step(step, {'test_data': test_data})
                        if success:
                            logger.info(f"✅ 步骤 {step_index} 执行成功: {step_info}")
                            break
                        elif retry == max_retries - 1:
                            raise AssertionError(f"❌ 步骤-{step_index} 执行失败: {step_info}")
                except Exception as e:
                    if retry < max_retries - 1:
                        logger.warning(f"⚠️ 步骤 {step_index} 执行失败，正在重试 ({retry + 1}/{max_retries})")
                        time.sleep(2)  # 重试前等待 2 秒
                    else:
                        error_msg = f"❌ 步骤 {step_index} '{step_info}' 异常，原因：{e}"
                        logger.error(error_msg)
                        allure.attach(str(step), f"失败的步骤 {step_index} 详情", allure.attachment_type.TEXT)
                        self.take_screenshot(f"step_{step_index}_exception.png", category='app')
                        raise AssertionError(error_msg)

        logger.info("✅ 所有测试步骤执行完成")
        return True


    def input_password(self, driver, password):
        for num in password:
            button = self.find_element_with_retry(MobileBy.XPATH, f"//XCUIElementTypeButton[@name='{num}']")
            button.click()
        logger.info("🔢 完成密码输入")

if __name__ == "__main__":
    app_base = AppBase(platform='android')
    try:
        data = app_base.get_test_data('example_case')
        logger.info(f"📊 获取到的测试数据：{data}")
    except Exception as e:
        logger.error(f"❌ 运行时出错：{e}")
