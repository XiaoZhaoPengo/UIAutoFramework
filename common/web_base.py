# 标准库导入
import os
import json
import platform
import shutil
import subprocess
import time
import zipfile
from typing import Dict, Optional

# 第三方库导入
import allure
import requests
import yaml
from colorama import init, Fore
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions, Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    WebDriverException
)

# 本地导入
from common.log_utils import logger

# 初始化 colorama
init(autoreset=True)


# 定位方法封装
def id(value: str) -> tuple:
    return By.ID, value

def name(value: str) -> tuple:
    return By.NAME, value

def xpath(value: str) -> tuple:
    return By.XPATH, value

def css_selector(value: str) -> tuple:
    return By.CSS_SELECTOR, value

def class_name(value: str) -> tuple:
    return By.CLASS_NAME, value

def tag_name(value: str) -> tuple:
    return By.TAG_NAME, value

def link_text(value: str) -> tuple:
    return By.LINK_TEXT, value

def partial_link_text(value: str) -> tuple:
    return By.PARTIAL_LINK_TEXT, value


class BrowserManager:
    @staticmethod
    def get_chrome_driver_path():
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "darwin":
            platform_key = "mac"
        elif system == "windows":
            platform_key = "win"
        elif system == "linux":
            platform_key = "linux"
        else:
            raise Exception(f"❌ 不支持的操作系统: {system}")

        if machine == "arm64" and system == "darwin":
            platform_key += "-arm64"
        elif "64" in machine and system != "darwin":
            platform_key += "64"
        elif system == "windows":
            platform_key += "32"

        chromedriver_name = "chromedriver.exe" if system == "windows" else "chromedriver"
        driver_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'driver', platform_key,
                                   chromedriver_name)
        logger.info(f"🔧 ChromeDriver 路径: {driver_path}")
        return driver_path

    def get_chrome_version(self):
        try:
            if platform.system() == "Darwin":  # macOS
                process = subprocess.Popen(
                    ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                    stdout=subprocess.PIPE)
                version = process.communicate()[0].decode('UTF-8').replace('Google Chrome', '').strip()
                return version
            elif platform.system() == "Windows":
                process = subprocess.Popen(
                    ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output = process.communicate()[0]
                version = output.decode('utf-8').strip().split()[-1]
                return version
            elif platform.system() == "Linux":
                process = subprocess.Popen(['google-chrome', '--version'], stdout=subprocess.PIPE)
                version = process.communicate()[0].decode('UTF-8').replace('Google Chrome', '').strip()
                return version
            else:
                logger.error(f"❌ 不支持的操作系统: {platform.system()}")
                return None
        except Exception as e:
            logger.error(f"❌ 获取 Chrome 版本时出错: {e}")
            return None

    def get_matching_chromedriver_version(self, chrome_version):
        major_version = chrome_version.split('.')[0]
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
        else:
            logger.warning(f"⚠️ 无法获取 Chrome {major_version} 的匹配 ChromeDriver 版本，尝试获取最新版本")
            return self.get_latest_chromedriver_version()

    def get_latest_chromedriver_version(self):
        url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
        else:
            raise Exception("❌ 无法获取最新的 ChromeDriver 版本")

    def get_chromedriver_version(self, driver_path):
        try:
            output = subprocess.check_output([driver_path, '--version'])
            version = output.decode('utf-8').split()[1]
            return version
        except Exception as e:
            logger.error(f"❌ 获取 ChromeDriver 版本时出错: {e}")
            return None

    def is_chromedriver_compatible(self, driver_path, chrome_version):
        try:
            output = subprocess.check_output([driver_path, '--version']).decode('utf-8')
            driver_version = output.split()[1]
            return driver_version.split('.')[0] == chrome_version.split('.')[0]
        except:
            return False

    def download_latest_chromedriver(self):
        try:
            # 获取最新的 ChromeDriver 版本
            url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
            response = requests.get(url)
            data = json.loads(response.text)
            latest_version = data['channels']['Stable']['version']

            # 确定平台
            system = platform.system().lower()
            machine = platform.machine().lower()

            if system == "darwin":
                platform_key = "mac-x64" if machine != "arm64" else "mac-arm64"
            elif system == "windows":
                platform_key = "win64" if "64" in machine else "win32"
            elif system == "linux":
                platform_key = "linux64"
            else:
                raise Exception(f"❌ 不支持的操作系统: {system}")

            # 构建下载 URL
            download_url = next(item['url'] for item in data['channels']['Stable']['downloads']['chromedriver'] if
                                item['platform'] == platform_key)

            # 下载 ChromeDriver
            driver_dir = os.path.dirname(self.get_chrome_driver_path())
            zip_path = os.path.join(driver_dir, "chromedriver.zip")
            os.makedirs(driver_dir, exist_ok=True)

            logger.info(f"📥 正在从 {download_url} 下载 ChromeDriver...")
            response = requests.get(download_url)
            with open(zip_path, 'wb') as file:
                file.write(response.content)

            # 解压缩文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(driver_dir)

            # 移动 chromedriver 到正确的位置
            chromedriver_name = "chromedriver.exe" if system == "windows" else "chromedriver"
            chromedriver_path = os.path.join(driver_dir, f"chromedriver-{platform_key}", chromedriver_name)
            final_path = os.path.join(driver_dir, chromedriver_name)

            if os.path.exists(chromedriver_path):
                shutil.move(chromedriver_path, final_path)
            else:
                raise FileNotFoundError(f"❌ ChromeDriver 文件未在预期位置找到: {chromedriver_path}")

            # 删除临时文件
            os.remove(zip_path)
            shutil.rmtree(os.path.join(driver_dir, f"chromedriver-{platform_key}"))

            # 设置权限
            if system != "windows":
                os.chmod(final_path, 0o755)

            logger.info(f"✅ ChromeDriver {latest_version} 下载完成。路径: {final_path}")
            return final_path
        except Exception as e:
            logger.error(f"❌ 下载 ChromeDriver 时发生错误: {e}")
            raise        


    def start_firefox_driver(self):
        web_driver_path = os.getenv('FIREFOX_DRIVER_PATH', './driver/geckodriver')
        if not os.path.isfile(web_driver_path):
            logger.warning("⚠️ Firefox driver 未找到。尝试下载...")
            BrowserManager.download_firefox_driver()

        options = FirefoxOptions()
        firefox_options = self.caps.get('firefoxOptions', {})
        for arg in firefox_options.get('args', []):
            options.add_argument(arg)

        service = Service(web_driver_path)
        return webdriver.Firefox(service=service, options=options)

    def download_firefox_driver(self):
        # 实现 Firefox driver 下载逻辑
        pass

class WebBase:

    def __init__(self, config=None, url_key='url1', browser_type='chrome'):
        self.config = config if config is not None else self.load_config()
        self.caps = self.get_capabilities()
        self.browser_type = browser_type
        self.url = self.get_url(url_key) # 使用 url_key 参数
        self.max_timeout = self.get_wait_timeout('max_timeout')
        self.poll_frequency = self.get_wait_timeout('poll_frequency')
        self.driver = None
        self.original_window = None  # 初始化为 None

    def get_by_type(self, by):
        by_type = {
            'id': By.ID,
            'name': By.NAME,
            'class_name': By.CLASS_NAME,
            'tag_name': By.TAG_NAME,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT,
            'xpath': By.XPATH,
            'css_selector': By.CSS_SELECTOR
        }
        return by_type.get(by.lower(), By.ID)    

    def get_wait_timeout(self, timeout_type):
        return self.config.get('web', {}).get('wait', {}).get(timeout_type, 10)

    def load_config(self):
        settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'setting.yaml')
        if not os.path.isfile(settings_file):
            logger.warning(f"⚠️ 配置文件 '{settings_file}' 未找到。将使用默置。")
            return {}
        with open(settings_file, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def get_url(self, url_key='url1'):
        return self.config.get('web', {}).get('urls', {}).get(url_key, 'http://example.com')

    def get_capabilities(self):
        return self.config.get('web', {}).get('capabilities', {})

    def start_driver(self):
        if self.driver:
            return self.driver
        logger.info("🚀 开始初始化 WebDriver...")
        if self.browser_type == 'chrome':
            self.driver = self.start_chrome_driver()
        elif self.browser_type == 'firefox':
            self.driver = self.start_firefox_driver()
        else:
            raise ValueError(f"❌ 不支持的浏览器类型: {self.browser_type}")

        self.original_window = self.driver.current_window_handle
        logger.info(f"✅ WebDriver 初始化完成，原始窗口句柄: {self.original_window}")    
        logger.info("✅ WebDriver 初始化完成")
        return self.driver

    def open_url(self):
        """
        打开指定的 URL
        """
        if not self.driver:
            self.start_driver()
        
        logger.info(f"🌐 正在打开URL: {self.url}")
        self.driver.get(self.url)
        
        # 设置原始窗口句柄
        if self.original_window is None:
            self.original_window = self.driver.current_window_handle
            logger.info(f"🪟 设置原始窗口句柄: {self.original_window}")

        try:
            WebDriverWait(self.driver, self.max_timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            logger.info("✅ 页面加载完成")
        except TimeoutException:
            logger.error("❌ 页面加载超时")
            self.take_screenshot("page_load_timeout.png")
            raise

    def start_chrome_driver(self):
        chrome_driver_path = BrowserManager.get_chrome_driver_path()
        if not os.path.exists(chrome_driver_path):
            logger.warning("⚠️ ChromeDriver 未找到。尝试下载...")
            chrome_driver_path = BrowserManager.download_latest_chromedriver()

        options = Options()
        chrome_options = self.caps.get('chromeOptions', {})

        # 根据setting文件配置决定是否添加 --headless 选项
        if self.config.get('web', {}).get('headless', False):
            options.add_argument('--headless')

        for arg in chrome_options.get('args', []):
            options.add_argument(arg)

        service = Service(executable_path=chrome_driver_path)
        return webdriver.Chrome(service=service, options=options)


    def wait_for_element(self, by, value, timeout=None, poll_frequency=None):
        """
        等待元素出现，并处理可能的异常
        """
        wait_timeout = timeout or self.max_timeout
        wait_poll_frequency = poll_frequency or self.poll_frequency

        logger.info(f"🔍 等待元素：{value}出现 , 显示等待时间: {wait_timeout}秒, 元素每秒检索频率: {wait_poll_frequency}秒")

        try:
            wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=wait_poll_frequency)
            element = wait.until(EC.presence_of_element_located((by, value)))
            logger.info(f"✅ 元素'{value}'已找到😋 ")
            return element
        except TimeoutException:
            logger.error(f"⏳ 等待元素{value}出现超时啦！😭 ")
            self.take_screenshot(f"timeout_{value}.png")
            raise TimeoutException(f"等待元素 {(by, value)} 出现超时啦！😭 等待时间：{wait_timeout}秒🕙")
        except NoSuchElementException:
            logger.error(f"❌ 未找到{value}元素💦")
            self.take_screenshot(f"not_found_{value}.png")
            raise NoSuchElementException(f"未找到{value}元素💦")
        except StaleElementReferenceException:
            logger.error(f"🔄 元素{value}已过时")
            self.take_screenshot(f"stale_{value}.png")
            raise StaleElementReferenceException(f"元素已过时: {(by, value)}，页面可能已刷新")
        except WebDriverException as e:
            logger.error(f"❌ WebDriver异常: {e}")
            self.take_screenshot(f"webdriver_exception_{value}.png")
            raise
        except Exception as e:
            logger.error(f"❌ 等待元素出现时发生未知错误: {e}")
            self.take_screenshot(f"unknown_error_{value}.png")
            raise


    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def quit_driver(self):
        """
        关闭 WebDriver
        """
        if hasattr(self, 'driver') and self.driver:
            logger.info("🛑 正在关闭 WebDriver...")
            try:
                self.driver.quit()
                time.sleep(0.1)  # 添加一个小延迟
                logger.info("✅ WebDriver 已关闭")
            except Exception as e:
                logger.error(f"❌ 关闭 WebDriver 时发生错误: {e}")
        else:
            logger.warning("⚠️ WebDriver 已经关闭或未初始化")

    def maximize_window(self):
        """
        最大化浏览器窗口
        """
        self.driver.maximize_window()

    def minimize_window(self):
        """
        最小化浏览器窗口
        """
        self.driver.execute_script("window.minimize();")

    def switch_window(self, target):
        """
        切换到指定的窗口。
        
        :param target: 'new' 表示切换到最新的窗口，整数表示窗口的索引（0为原始窗口）
        :return: bool，切换是否成功
        """
        try:
            all_handles = self.driver.window_handles
            current_handle = self.driver.current_window_handle
            logger.info(f"当前窗口句柄: {current_handle}")
            logger.info(f"所有窗口句柄: {all_handles}")

            if isinstance(target, int):
                if 0 <= target < len(all_handles):
                    self.driver.switch_to.window(all_handles[target])
                    logger.info(f"🪟 切换到窗口索引 {target}: {all_handles[target]}")
                else:
                    logger.error(f"❌ 无效的窗口索引: {target}")
                    return False
            elif target == 'new':
                if len(all_handles) > 1:
                    self.driver.switch_to.window(all_handles[-1])
                    logger.info(f"🪟 切换到最新窗口: {all_handles[-1]}")
                else:
                    logger.error("❌ 没有新窗口可切换")
                    return False
            else:
                logger.error(f"❌ 无效的窗口目标类型: {target}，应为 'new' 或整数索引")
                return False

            # 等待新窗口加载完成
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            new_handle = self.driver.current_window_handle
            logger.info(f"✅ 成功切换到窗口: {new_handle}")
            return True

        except Exception as e:
            logger.error(f"❌ 切换窗口时发生错误: {e}")
            self.take_screenshot(f"switch_window_error_{target}.png")
            return False

    def handle_alert(self, action='accept'):
        """
        处理 alert 弹窗
        :param action: 'accept' 接受弹窗，'dismiss' 取消弹窗
        """
        try:
            alert = WebDriverWait(self.driver, 10).until(EC.alert_is_present())
            if action == 'accept':
                alert.accept()
            elif action == 'dismiss':
                alert.dismiss()
        except TimeoutException:
            logger.warning("⚠️ 在指定时间内未找到 alert 弹窗.")

    def execute_script(self, script, *args):
        """
        执行 JavaScript 代码
        :param script: JavaScript 代码
        :param args: 传递给 JavaScript 代码的参数
        :return: JavaScript 执行结果
        """
        result = self.driver.execute_script(script, *args)
        logger.info(f"🖥️ 执行了 JavaScript: {script[:50]}...")
        return result
        

    def upload_file(self, by, value, file_path):
        """
        上传文件
        :param by: 定位策略 (e.g., By.XPATH)
        :param value: 定位值
        :param file_path: 文件路径
        """
        element = self.wait_for_element(by, value)
        if element:
            element.send_keys(file_path)

    def download_file(self, url, download_path):
        """
        下载文件
        :param url: 文件 URL
        :param download_path: 保存路径
        """
        response = requests.get(url)
        with open(download_path, 'wb') as file:
            file.write(response.content)

    def perform_action(self, actions):
        """
        执行一系列的动作
        :param actions: 动作列表，每个动作是一个字典
        """
        action_chains = ActionChains(self.driver)
        for action in actions:
            if action['type'] == 'click':
                element = self.wait_for_element(action['by'], action['value'])
                if element:
                    action_chains.click(element)
            elif action['type'] == 'send_keys':
                element = self.wait_for_element(action['by'], action['value'])
                if element:
                    action_chains.send_keys_to_element(element, action['value'])
            # 添加更多的 ActionChains 操作类型
        action_chains.perform()


    def get_form_data(self, by, value):
        """
        获取表单数据
        :param by: 定位策略 (e.g., By.XPATH)
        :param value: 定位值
        :return: 表单数据
        """
        form = self.wait_for_element(by, value)
        if form:
            return form.get_attribute('value')
        return None

    def read_case_yaml(self, yaml_case):
        """
        读取 caseyaml 目录中的 YAML 文件
        :param yaml_case: 用例名称，决定读取的 YAML 文件
        :return: 用例数据字典
        """
        yaml_case_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'yaml_case', f'{yaml_case}.yaml')
        if not os.path.isfile(yaml_case_path):
            logger.warning(f"⚠️ YAML file for case '{yaml_case}' not found at {yaml_case_path}")
            return None

        with open(yaml_case_path, 'r', encoding='utf-8') as file:
            case_data = yaml.safe_load(file)
        return case_data

    def get_test_data(self, yaml_case):
        """
        从 yaml_case 目录中的 YAML 文件中获取测试数据
        :param yaml_case: 用例名称，决定读取的 YAML 文件
        :return: 测试数据列表
        """
        case_data = self.read_case_yaml(yaml_case)
        if not case_data:
            return []
        test_data = case_data.get('testdata', [])
        # 确保返回的是列表，即使只有一组数据
        if isinstance(test_data, dict):
            test_data = [test_data]
        return test_data

    def get_case_title(self, yaml_case):
        """
        从 yaml_case 目录中的 YAML 文件中获取用例标题
        :param yaml_case: 用例名称，决定读取的 YAML 文件
        :return: 用例标题
        """
        case_data = self.read_case_yaml(yaml_case)
        if not case_data:
            return None

        return case_data.get('title', '')

    def get_case_name(self, yaml_case):
        """
        从 yaml_case 目录中的 YAML 文件中获取用例名称
        :param yaml_case: 用例名称，决定读取的 YAML 文件
        :return: 用例名称
        """
        case_data = self.read_case_yaml(yaml_case)
        if not case_data:
            return None

        return case_data.get('casename', '')


 

    def execute_step(self, step, test_data):
        """
        执行单个步骤
        """
        logger.debug(f"🔍 执行步骤: {step}")
        by = step.get('by')
        value = step.get('value')
        operate = step.get('operate')
        target = step.get('target')
        info = step.get('info', '')
        sleep = step.get('sleep', 0)
        optional = step.get('optional', False)  # 获取 'optional' 字段，如果不存在默认为 False


        # 确保 operate 始终存在，只有在操作类型不是 switch_window 时才检查 by 和 value 参数
        if operate != 'switch_window' and not all([by, value]):
            logger.error(f"❌ 步骤缺少必要的信息: {step}")
            return False

        logger.info(f"🚀 执行操作: {info}, 定位方式: {by}, 定位值: {value}, 操作: {operate}")

        try:
        # 如果操作类型是 switch_window，则跳过 by 和 value 的处理
            if operate == 'switch_window':
                logger.debug(f"准备切换到目标窗口: {target}")
                success = self.switch_window(target)
                if not success:
                    logger.error(f"❌ 切换到目标窗口失败: {target}")
                    return False
            else:
                by_type = self.get_by_type(by)
                logger.debug(f"🔎 定位方式: {by_type}")
                if operate == 'send_keys':
                    input_template = step.get('input', '')
                    # 处理两种不同的测试数据格式
                    if isinstance(test_data, dict):
                        input_text = input_template.format(**test_data)
                    else:
                        input_text = input_template.format(test_data=test_data)
                    logger.debug(f"⌨️ 准备输入的文本: {input_text}")
                    self.send_keys(by_type, value, text=input_text)
                elif operate == 'click':
                    # 添加显式等待3秒
                    element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((by_type, value))
                    )
                    element.click()
                elif operate == 'wait_for_element':
                    self.wait_for_element(by_type, value)
                elif operate == 'assert_title':
                    assert test_data in self.driver.title, f"❌ 标题不包含预期文本: {test_data}"
                elif operate == 'assert_element_text':
                    element = self.find_element(by_type, value)
                    assert test_data in element.text, f"❌ 元素文本不包含预期内容: {test_data}"
                elif operate == 'clear':
                    self.clear_element(by_type, value)
                elif operate == 'submit':
                    self.submit_form(by_type, value)
                elif operate == 'get_attribute':
                    return self.get_element_attribute(by_type, value, step.get('attribute'))
                elif operate == 'is_displayed':
                    return self.is_element_displayed(by_type, value)
                elif operate == 'is_enabled':
                    return self.is_element_enabled(by_type, value)
                elif operate == 'is_selected':
                    return self.is_element_selected(by_type, value)
                elif operate == 'select_by_value':
                    self.select_by_value(by_type, value, step.get('value'))
                elif operate == 'select_by_index':
                    self.select_by_index(by_type, value, step.get('index'))
                elif operate == 'select_by_text':
                    self.select_by_text(by_type, value, step.get('text'))
                elif operate == 'switch_to_frame':
                    self.switch_to_frame(by_type, value)
                elif operate == 'switch_to_default_content':
                    self.driver.switch_to.default_content()
                elif operate == 'switch_to_window':
                    self.switch_to_window(step.get('window_handle'))
                elif operate == 'maximize_window':
                    self.driver.maximize_window()
                elif operate == 'minimize_window':
                    self.driver.minimize_window()
                elif operate == 'refresh_page':
                    self.driver.refresh()
                elif operate == 'go_back':
                    self.driver.back()
                elif operate == 'go_forward':
                    self.driver.forward()
                elif operate == 'execute_script':
                    return self.execute_script(step.get('script'), *step.get('args', []))
                else:
                    logger.warning(f"⚠️ 未知的操作类型: {operate}")
                    return False

            # 在这里添加处理 sleep 参数的代码
            if 'sleep' in step:
                sleep_time = step['sleep']
                logger.info(f"⏳ 等待 {sleep_time} 秒")
                time.sleep(sleep_time)

            logger.info(f"✅ 步骤执行成功: {info}")
            return True    

        except KeyError as e:
            logger.error(f"❌ 测试数据中缺少键: {e}")
            return False    
        except Exception as e:
            logger.error(f"❌ 执行步骤时出错: {e}")
            screenshot_path = f"screenshots/{step.get('step', 'screenshot')}.png"
            self.take_screenshot(screenshot_path, category='web')
            allure.attach.file(screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
            if not optional:
                raise
            logger.warning(f"⚠️ 可选步骤执行失败，继续执行下一步: {step}")
            return False
            
        logger.info(f"✅ 步骤执行成功: {info}")
        return True    

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
            try:
                with allure.step(f"步骤 {step_index}: {step_info}"):
                    success = self.execute_step(step, test_data)
                    if not success:
                        if not step.get('optional', False):
                            error_msg = f"❌ 步骤-{step_index} 执行失败: {step_info}"
                            logger.error(error_msg)
                            allure.attach(str(step), f"失败的步骤 {step_index} 详情", allure.attachment_type.TEXT)
                            self.take_screenshot(f"step_{step_index}_failed.png")
                            raise AssertionError(error_msg)
                        else:
                            logger.warning(f"⚠️ 可选步骤 {step_index}-执行失败，但继续执行下一个步骤: {step_info}")
                    else:
                        logger.info(f"✅ 步骤 {step_index} 执行成功: {step_info}")
            except Exception as e:
                if step.get('optional', False):
                    logger.warning(f"⚠️ 可选步骤 {step_index} '{step_info}' 异常，原因：{e}")
                    continue
                else:
                    error_msg = f"❌ 步骤 {step_index} '{step_info}' 异常，原因：{e}"
                    logger.error(error_msg)
                    allure.attach(str(step), f"失败的步骤 {step_index} 详情", allure.attachment_type.TEXT)
                    self.take_screenshot(f"step_{step_index}_exception.png")
                    raise AssertionError(error_msg)

        logger.info("✅ 所有测试步骤执行完成")
        return True

    def retry_on_failure(self, func, *args, **kwargs):
        """
        执行操作，如果失败则重试一次
        :param func: 要执行的函数
        :param args: 函数的位置参数
        :param kwargs: 函数的关键字参数
        :return: 函数执行的结果
        """
        try:
            return func(*args, **kwargs)
        except (StaleElementReferenceException, ElementClickInterceptedException) as e:
            logger.warning(f"⚠️ 操作失败，准备重试。错误: {e}")
            time.sleep(1)  # 等待1秒后重试
            return func(*args, **kwargs)    

    # 以下是支持的操作方法
    def send_keys(self, by_type, value, *, text):
        def _send_keys():
            try:
                element = self.find_element(by_type, value)
                element.send_keys(text)
                logger.info(f"⌨️ 成功向元素 {value} 输入文本: {text}")
            except Exception as e:
                logger.error(f"❌ 向元素 {value} 输入文本时出错: {e}")
                raise
        self.retry_on_failure(_send_keys)        

    def click_element(self, by, value):
        def _click():
            element = self.find_element(by, value)
            element.click()
            logger.info(f"👆 点击了元素：{value}")
        self.retry_on_failure(_click)    

    def clear_element(self, by, value):
        def _clear():
            element = self.find_element(by, value)
            element.clear()
            logger.info(f"🧹 清除了元素 {value} 的内容")
        self.retry_on_failure(_clear)

    def submit_form(self, by, value):
        def _submit():
            element = self.find_element(by, value)
            element.submit()
            logger.info(f"📤 提交了表单 {value}")
        self.retry_on_failure(_submit)

    def get_element_attribute(self, by, value, attribute):
        element = self.find_element(by, value)
        return element.get_attribute(attribute)

    def is_element_displayed(self, by, value):
        element = self.find_element(by, value)
        is_displayed = element.is_displayed()
        logger.info(f"👀 元素是否可见: {value} - {'是' if is_displayed else '否'}")
        return is_displayed

    def is_element_enabled(self, by, value):
        element = self.find_element(by, value)
        is_enabled = element.is_enabled()
        logger.info(f"🔓 元素是否启用: {value} - {'是' if is_enabled else '否'}")
        return is_enabled

    def is_element_selected(self, by, value):
        element = self.find_element(by, value)
        is_selected = element.is_selected()
        logger.info(f"✅ 元素是否被选中: {value} - {'是' if is_selected else '否'}")
        return is_selected

    def take_screenshot(self, filename, category='web'):
        """
        截图
        :param filename: 截图文件名
        :param category: 截图类别，默认为 'web'
        """
        try:
            base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "screenshots", category)
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            if not filename.endswith('.png'):
                filename += '.png'
            screenshot_path = os.path.join(base_dir, filename)
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"📸 屏幕截图已保存: {screenshot_path}")
        except Exception as e:
            logger.error(f"❌ 保存屏幕截图时发生错误: {e}")

