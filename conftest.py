import logging
import allure
from common.log_utils import logger
import pytest
import yaml
import os
from common.app_base import AppBase
from common.web_base import WebBase
import subprocess
import shutil
import time

# 获取项目根目录的绝对路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
ALLURE_RESULTS_DIR = os.path.join(REPORTS_DIR, "allure-results")
ALLURE_REPORT_DIR = os.path.join(REPORTS_DIR, "allure-report")

# 使用绝对路径加载配置文件
config_path = os.path.join(PROJECT_ROOT, 'config', 'setting.yaml')

# 加载配置文件
try:
    with open(config_path, 'r', encoding='utf-8') as file:
        settings = yaml.safe_load(file)
except FileNotFoundError:
    logger.error(f"❌ 配置文件未找到: {config_path}")
    settings = {}
except yaml.YAMLError as e:
    logger.error(f"❌ 解析YAML文件时出错: {e}")
    settings = {}

@pytest.fixture(scope="function")
def web_driver():
    logger.info("🚀 正在初始化 WebDriver...")
    web_app = WebBase()
    yield web_app
    logger.info("🛑 正在关闭 WebDriver...")
    web_app.quit_driver()

@pytest.fixture(scope="function")
def ios_driver(request):
    logger.info("🍏 正在初始化 iOS Driver...")
    ios_base = AppBase('ios')
    yield ios_base
    logger.info("🛑 正在关闭 iOS Driver...")
    ios_base.quit_driver()

@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    from common.log_utils import logger
    # 确保日志器已经正确配置
    logger.info("📝 日志配置已初始化")

@pytest.fixture(scope="session", autouse=True)
def manage_reports_dir():
    # 确保 reports 目录存在
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(ALLURE_RESULTS_DIR, exist_ok=True)
    yield
    # 测试结束后，可以在这里添加清理代码（如果需要）    

def load_settings():
    # 获取项目根目录的绝对路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    settings_file = os.path.join(project_root, 'config', 'setting.yaml')
    
    if not os.path.exists(settings_file):
        raise FileNotFoundError(f"❌ 配置文件未找到: {settings_file}")
    
    with open(settings_file, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def pytest_configure(config):
    settings = load_settings()
    config.settings = settings
    
    # 使用配置文件中的日志设置
    log_config = settings.get('logging', {})
    config.option.log_cli = log_config.get('log_cli', True)
    config.option.log_cli_level = log_config.get('log_cli_level', 'INFO')
    config.option.log_cli_format = log_config.get('log_cli_format', "%(asctime)s - %(levelname)s - %(message)s")
    config.option.log_cli_date_format = log_config.get('log_cli_date_format', "%Y-%m-%d %H:%M:%S")

    # 设置 Allure 报告目录
    config.option.allure_report_dir = ALLURE_RESULTS_DIR

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    logger.info(f"🎬 开始测试: {item.name}")

@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item):
    logger.info(f"🏁 结束测试: {item.name}")

@pytest.fixture(scope="function", autouse=True)
def log_test_result(request):
    yield
    if hasattr(request.node, "rep_call"):
        if request.node.rep_call.failed:
            logger.error(f"❌ 测试失败: {request.node.name}")
        elif request.node.rep_call.passed:
            logger.info(f"✅ 测试通过: {request.node.name}")

@pytest.fixture(scope="session", autouse=True)
# 在测试开始前，确保截图目录已创建
def create_screenshots_dir():
    screenshots_dir = os.path.join(REPORTS_DIR, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)        

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
# 钩子函数来捕获失败的测试并自动截图
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("web_driver")
        if driver and hasattr(driver, 'take_screenshot'):
            # 生成一个唯一的文件名
            filename = f"error_{item.name}_{time.strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_path = driver.take_screenshot(filename)
            if screenshot_path:
                with open(screenshot_path, "rb") as file:
                    allure.attach(
                        file.read(),
                        name="screenshot",
                        attachment_type=allure.attachment_type.PNG
                    )
                logger.info(f"📸 已保存失败测试的截图: {screenshot_path}")

def pytest_sessionfinish(session, exitstatus):
    logger.info("🏁 测试会话结束，正在生成 Allure 报告...")

    # 如果报告目录已存在，则删除它
    if os.path.exists(ALLURE_REPORT_DIR):
        shutil.rmtree(ALLURE_REPORT_DIR)

    # 生成报告
    try:
        subprocess.run([
            "allure", "generate", ALLURE_RESULTS_DIR,
            "-o", ALLURE_REPORT_DIR,
            "--clean",
            "--lang", "zh"  # 设置语言为中文
        ], check=True)
        logger.info(f"✨ Allure 报告生成完成，路径: {ALLURE_REPORT_DIR}")

        # 打开报告（可选）
        subprocess.Popen(["allure", "open", ALLURE_REPORT_DIR])
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ 生成 Allure 报告时出错: {e}")