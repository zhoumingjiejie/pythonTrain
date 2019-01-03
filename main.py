# -*- coding: utf-8 -*-
from splinter.browser import Browser
from time import sleep
import trainData
import time


class Train(object):
    # 用户名，密码
    username = ""
    password = ""

    """网址"""
    ticket_url = "https://kyfw.12306.cn/otn/leftTicket/init"
    login_url = "https://kyfw.12306.cn/otn/login/init"
    view_url = "https://kyfw.12306.cn/otn/view/index.html"
    buy = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"

    def __init__(self):
        # 初始化站点信息
        self.train_data = trainData.TrainData()
        # 输入
        # train_date = raw_input('请输入出发时间(格式：yyyy-MM-dd):')
        # from_station = raw_input('请输入出发城市:')
        # to_station = raw_input('请输入到达城市:')
        self.from_station = '广州'
        self.to_station = '茂名'
        self.train_date = time.strftime('%Y-%m-%d', time.localtime())
        self.train_date = '2019-01-09'
        self.cookie_from_station = self._chinese_conversion_unicode(self.from_station)
        self.cookie_to_station = self._chinese_conversion_unicode(self.to_station)
        # 查询次数
        self.query_count = 0
        # 初始化浏览设备,打开浏览器，默认火狐
        self.driver = Browser()

    def login(self):
        self.driver.visit(self.login_url)
        self.driver.driver.maximize_window()
        # 填写账号密码
        self.driver.fill("loginUserDTO.user_name", self.username)
        self.driver.fill("userDTO.password", self.password)
        print("等待验证码，自行输入...")
        while True:
            if self.driver.url != self.view_url:
                sleep(1)
            else:
                break

    def query_train(self):
        """
        功能：查询火车信息后预订
        :return:
        """
        # 判断抢票是否成功
        self.query_count += 1
        if self.query_count > 3:
            print('抢票失败')
            exit()

        # 登陆完成后跳转到查询页面
        self.driver.visit(self.ticket_url)
        try:
            # 查询条件
            self.driver.cookies.add({"_jc_save_fromStation": self.cookie_from_station})
            self.driver.cookies.add({"_jc_save_toStation": self.cookie_to_station})
            self.driver.cookies.add({"_jc_save_fromDate": self.train_date})
            self.driver.reload()
            # 点击查询按钮
            self.driver.find_by_id('query_ticket').click()

            # 符合条件的火车列表
            list_data = self.train_data.get_filter_train_info(self.train_date, self.from_station, self.to_station)
            print(list_data)

            index = 0
            # 防止系统繁忙时没有获取到【预订】按钮的正确下标
            while True:
                train_index_list = []
                for i in self.driver.find_by_xpath('//a[@class="number"]'):
                    if i.text in list_data:
                        train_index_list.append(index)
                    index += 1
                if train_index_list.__len__() == train_index_list.__len__():
                    print(train_index_list)
                    break

            if train_index_list.__len__() == 0:
                print('没有符合条件的火车可预约，goodbye！')
                exit()

            # 火车预定
            count = 0
            while self.driver.url == self.ticket_url and count <= train_index_list[train_index_list.__len__() - 1]:
                # 检查页面预约按钮是否加载完成
                if self.driver.is_element_present_by_text('预订'):
                    try:
                        for i in self.driver.find_by_text("预订"):
                            # 判断预约的火车是否符合条件（条件：有硬座或二等座）
                            if count in train_index_list:
                                i.click()
                                # 填写用户信息
                                self._submit_user_info()
                                break
                            count += 1
                    except Exception as e:
                        print(e)
                        count += 1
                        if count > train_index_list[train_index_list.__len__() - 1]:
                            self.query_train()
                        continue
                else:
                    print('等待页面记载')
        except Exception as e:
            print(e)

    def _submit_user_info(self):
        """
        功能：提交用户信息购票
        :return:
        """
        # 选择用户
        self.driver.find_by_id('normalPassenger_0').click()

        # 定位选项，硬座：1；硬卧：3；软卧：4；二等座：O；一等座：M
        text_arr = ['1', 'O']
        for text in text_arr:
            if self.select_id_by_value('seatType_1', text):
                print('已选择：' + text)
                break
        exit()

        # 提交订单
        self.driver.find_by_id('submitOrder_id').click()

        # 确认订单
        while True:
            if self.driver.is_element_present_by_id('qr_submit_id'):
                self.driver.find_by_id('qr_submit_id').click()
                break

    def _chinese_conversion_unicode(self, chinese):
        """
        功能： 获取cookies的unicode编码
        :param chinese: 站点名字
        :return:站点cookies
        """
        unicode_str = str(bytes(chinese, encoding='unicode_escape'))[2:-1] \
            .replace('\\\\', '%') \
            .upper() \
            .replace('%U', '%u')
        station_name = self.train_data.station[chinese]
        cookie_station_name = unicode_str + '%2C' + station_name
        return cookie_station_name

    def select_id_by_value(self, select_id, value):
        """
        功能：根据下拉框的id和value值来确认选择
        :param select_id: 下拉框id
        :param value: select中option的value值
        :return:是否选择成功的布尔值
        """
        train_select = '//select[@id="%s"]//option[@value="%s"]' % (select_id, value)
        if self.driver.is_element_present_by_xpath(train_select):
            select = self.driver.find_by_xpath(train_select)
            select.first._element.click()
            print('已选择：' + value)
            return True
        else:
            print(f'{"没有value=("}{value}{")的下拉框"}')
            return False

    def select_id_by_text(self, select_id, text):
        """
        功能：根据下拉框的id和text值来确认选择
        :param select_id: 下拉框id
        :param text: select中option的值
        :return: 是否选择成功的布尔值
        """
        train_select = '//select[@id="%s"]//option[text()="%s"]' % (select_id, text)
        if self.driver.is_element_present_by_xpath(train_select):
            select = self.driver.find_by_xpath(train_select)
            select.first._element.click()
            return True
        else:
            print(f'{"text=("}{text}{")的下拉框"}')
            return False


if __name__ == '__main__':
    train = Train()
    # 登陆
    train.login()
    # 查询
    train.query_train()
    """
    # 定时任务
    # schedule.every().day.at("10:55").do(train.login)
    # schedule.every().day.at("11:00").do(train.start)
    while True:
        schedule.run_pending()
        time.sleep(1)
    """
