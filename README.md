# 自动化测试框架

这是一个基于Python的自动化测试框架，支持Web端和移动端(iOS/Android)的自动化测试。框架采用YAML管理测试用例，一键生成测试脚本，真正做到低代码自动化测试。

## 特色功能

- 🚀 开箱即用：只需编写YAML用例文件，一键生成测试脚本
- 📱 全平台支持：Web端、iOS端、Android端自动化测试
- 🔄 并行测试：支持多设备同时执行测试
- 🎯 智能重试：内置元素查找重试机制
- 📝 YAML驱动：通过YAML文件管理测试用例，降低维护成本
- 📊 报告展示：集成Allure测试报告
- 🔔 多渠道通知：支持钉钉/企业微信/邮件通知
- 🛠 丰富的API：支持多种定位方式和操作类型

## 环境准备

### 必需环境
- Python 3.7+
- Node.js 12+
- Appium 2.0+
- Chrome/Firefox浏览器

### iOS测试环境
- Xcode
- iOS真机或模拟器
- WebDriverAgent配置

### Android测试环境
- Android SDK
- Android真机或模拟器
- adb工具

## 安装

1. 克隆项目:
```bash
git clone [项目地址]
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

## 项目结构

```
├── case                    # 测试用例目录
│   ├── app_demo           # App测试用例
│   └── web_demo           # Web测试用例
├── common                  # 公共模块
│   ├── app_base.py        # App测试基类
│   ├── web_base.py        # Web测试基类
│   └── log_utils.py       # 日志工具
├── config                  # 配置文件目录
│   └── setting.yaml       # 全局配置文件
├── driver                  # 驱动文件目录
├── logs                    # 日志目录
├── reports                 # 测试报告目录
│   └── screenshots        # 截图目录
├── yaml_case              # YAML测试用例文件
└── conftest.py            # pytest配置文件
```

## 快速开始

### 1. 配置测试环境
修改 `config/setting.yaml` 文件，配置测试环境参数：

```yaml
# Web测试配置
web:
  web_type: "chrome"  
  urls:
    url1: "http://baidu.com"    # Web测试地址1
    url2: "http://dev.admin.zuzuya.cn"  # Web测试地址2

# iOS测试配置
ios:
  capabilities:
    platformName: "ios"
    platformVersion: "18.0"  # iOS版本
    deviceName: "您的设备名称"
    udid: "设备UDID"
    bundleId: "com.example.app"
```

### 2. 编写YAML测试用例
在 `yaml_case` 目录创建YAML文件(例如: test_demo.yaml):
```yaml
casename: test_demo
title: "登录测试"
testdata:
  - username: "test"
    password: "123456"
locators:
  - step: "点击登录"
    by: xpath
    value: "//button[@id='login']"
    operate: click
```

### 3. 生成测试用例
运行根目录下的generate_test_case.py:
```python
# 设置测试类型和YAML文件名
TEST_TYPE = 'web'  # 或 'app'
YAML_FILE = 'test_demo.yaml'
PLATFORM = 'ios'   # 可选，默认android

# 运行生成器
python generate_test_case.py
```

### 4. 执行测试
```bash
# 运行单个测试
pytest case/web_demo/test_demo.py -v

# 生成报告
pytest --alluredir=./reports/allure-results
allure serve ./reports/allure-results
```

## 用例生成配置说明

### 1. 配置generate_test_case.py

在项目根目录下的generate_test_case.py文件中配置以下参数：

```python
# 基础配置
CONFIG = {
    'yaml_dir': 'yaml_case',     # YAML用例文件目录
    'case_dir': 'case',          # 生成的测试用例目录
    'web_subdir': 'web_demo',    # Web测试用例子目录
    'app_subdir': 'app_demo',    # App测试用例子目录
}

# 文件已存在时的处理方式
FILE_EXISTS_ACTION = 'skip'      # 可选值: 'skip'(跳过), 'overwrite'(覆盖), 'rename'(重命名)

# 测试类型和YAML文件配置
TEST_TYPE = 'app'                # 测试类型: 'web' 或 'app'
YAML_FILE = 'test_demo.yaml'     # 要处理的YAML文件名
PLATFORM = 'ios'                 # 移动端平台: 'ios' 或 'android'(默认)

# 批量处理配置
PROCESS_ALL_YAML = False         # 是否处理所有YAML文件
```

### 2. YAML用例文件结构

在`yaml_case`目录下创建YAML文件，基本结构如下：

```yaml
casename: test_case_name        # 用例名称(必填)
title: "测试用例标题"           # 用例标题(必填)
type: "web"                    # 用例类型：web或app(批量处理时必填)
testdata:                      # 测试数据(可选)
  - username: "test"
    password: "123456"
locators:                      # 元素定位(必填)
  - step: "步骤描述"
    by: xpath                  # 定位方式
    value: "//button[@id='login']"  # 定位值
    operate: click            # 操作类型
    input: "{username}"       # 输入值(可选)
    sleep: 1                 # 等待时间(可选)
    timeout: 10              # 超时时间(可选)
```

### 3. 生成测试用例

#### 单个用例生成
```bash
# 修改generate_test_case.py中的配置后运行
python generate_test_case.py
```

#### 批量生成用例
```bash
# 设置PROCESS_ALL_YAML = True后运行
python generate_test_case.py
```

## 元素定位方式

### Web端支持的定位方式:
- id
- name 
- xpath
- css
- class
- link
- partlink
- tag

### 移动端支持的定位方式:
- ACCESSIBILITY_ID
- IOS_PREDICATE 
- IOS_CLASS_CHAIN
- ANDROID_UIAUTOMATOR
- ANDROID_VIEWTAG
- XPATH
- NAME
- CLASS_NAME
- ID
- CSS_SELECTOR
- COORDINATES (坐标定位)

### 支持的操作类型
```yaml
operate:
  - click            # 点击元素
  - send_keys        # 输入文本
  - clear           # 清除输入
  - submit          # 提交表单
  - get_text        # 获取文本
  - wait_for_element # 等待元素
  - scroll          # 滚动页面
  - switch_window   # 切换窗口
  - jsclear         # JS清除内容
  - coordinates     # 坐标点击
```

## 调试与故障排除

### 常见问题

1. 元素定位失败
- 检查定位方式是否正确
- 增加等待时间(sleep/timeout)
- 使用optional: true标记可选步骤

2. iOS真机测试问题
- 确认WebDriverAgent正确安装
- 检查开发者证书是否有效
- 确认UDID配置正确

3. 并行测试问题
- 确保设备ID不重复
- 配置不同的Appium端口
- 检查资源占用情况

### 日志说明
```yaml
logging:
  level: INFO  # 日志级别(DEBUG/INFO/WARNING/ERROR)
  format: "%(asctime)s - %(levelname)s - %(message)s"
```

### 截图路径
失败用例截图保存在: ./reports/screenshots/

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交代码
4. 发起Pull Request

## 许可证

[许可证类型]

## 联系方式

[wechat:o3o0421]
