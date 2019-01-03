# -*- coding: UTF-8 -*-
from urllib import request
import ssl
import json
import time
import datetime
import requests

ssl._create_default_https_context = ssl._create_unverified_context


class TrainData:

    def __init__(self):
        self._set_train_name()

    def get_filter_train_info(self, train_date, form_station, to_station):
        """
        功能:获取可以预约火车的下标
        :param train_date 发车时间
        :param form_station 火车起始站
        :param to_station 火车终点站
        :return:
        """
        train_info = self.get_train_info(train_date, form_station, to_station)
        return self._get_yz_rz(train_info)

    def get_train_info(self, train_date, form_station, to_station):
        """
         功能:获取可以预约火车的信息
         :param train_date 发车时间
         :param form_station 火车起始站
         :param to_station 火车终点站
        :return:
        """
        train_list = {}
        interface = self._get_interface_url(form_station, to_station)
        query_url = f'{"https://kyfw.12306.cn/otn/"}{interface}' \
            f'{"?leftTicketDTO.train_date="}{train_date}' \
            f'{"&leftTicketDTO.from_station="}{self.station[form_station]}' \
            f'{"&leftTicketDTO.to_station="}{self.station[to_station]}{"&purpose_codes=ADULT"}'

        print('查询接口：' + query_url)
        response = request.Request(query_url)
        response.add_header('User-Agent',
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' +
                            ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')
        result = json.loads(request.urlopen(response).read())['data']['result']

        # 索引3=车次
        # 索引8=出发时间
        # 索引9=到达时间
        index = 0
        for data in result:
            split_item = data.split('|')
            item_dict = {}
            if split_item[11] == 'Y':  # 已经开始卖票了
                item_dict['train_name'] = split_item[3]  # 车次名
                item_dict['depart_date'] = split_item[13]  # 出发日期
                item_dict['depart_time'] = split_item[8]  # 出发时间
                item_dict['arrive_time'] = split_item[9]  # 到站时间
                item_dict['spend_time'] = split_item[10]  # 经历时长
                item_dict['wz'] = split_item[26]  # 无座
                item_dict['yz'] = split_item[29]  # 硬座
                item_dict['yw'] = split_item[28]  # 硬卧
                item_dict['rw'] = split_item[23]  # 软卧
                item_dict['td'] = split_item[32]  # 特等座
                item_dict['yd'] = split_item[31]  # 一等座
                item_dict['ed'] = split_item[30]  # 二等座
                item_dict['dw'] = split_item[33]  # 动卧
                item_dict['index'] = index  # 下标
                train_list[split_item[3]] = item_dict
                # 无法买票的车次,有可能是已卖光,也有可能是还不开卖
            elif split_item[0] == '':
                '''
                print('车次{}的票暂时不能购买!'
                      .format(split_item[3]))
                      '''
            else:
                '''
                print('车次{}还未开始卖票,起售时间为:{}'
                      .format(split_item[3], split_item[1]))
                      '''
            index += 1

        return train_list

    def _get_yz_rz(self, json_data):
        """
        功能:筛选出有软座或硬座的数据
        :param json_data 可预约的火车数据
         """
        train_arr = []
        for key in json_data:
            yz = json_data[key]['yz']
            ed = json_data[key]['ed']
            if (yz == '无' or yz == '') and (ed == '无' or ed == ''):
                '''
                print('车次{}硬座已售完'
                      .format(json_data[key]['train_name']))
                      '''
            else:
                depart_time = datetime.datetime.strptime(
                    json_data[key]['depart_date'] + ' ' + json_data[key]['depart_time'], '%Y%m%d %H:%M')
                start_time = datetime.datetime.strptime(json_data[key]['depart_date'] + ' 08:00', '%Y%m%d %H:%M')
                end_time = datetime.datetime.strptime(json_data[key]['depart_date'] + ' 18:00', '%Y%m%d %H:%M')
                if (depart_time - start_time).days == 0 and (end_time - depart_time).days == 0:
                    train_arr.append(json_data[key]['train_name'])
        return train_arr

    def _get_interface_url(self, form_station, to_station):
        url = 'https://kyfw.12306.cn/otn/leftTicket/queryA?' \
              'leftTicketDTO.train_date=' + time.strftime("%Y-%m-%d", time.localtime()) + \
              '&leftTicketDTO.from_station=' + self.station[form_station] + \
              '&leftTicketDTO.to_station=' + self.station[to_station] + \
              '&purpose_codes=ADULT'
        try:
            request_result = requests.get(url)
            http_status_code = request_result.status_code
            if http_status_code == 302:
                return request_result.json()['c_url']
            elif http_status_code == 200:
                return 'leftTicket/queryA'
            else:
                print('获取火车查询接口时返回未知状态：{}'.format(http_status_code))
                exit()
        except requests.exceptions.HTTPError as e:
            print('获取火车查询接口出错：{}'.format(e))
            exit()

    def _set_train_name(self):
        # 获取站点名缩写
        station = requests.get('https://kyfw.12306.cn/otn/resources/js/framework/station_name.js')
        start_index = station.text.find('\'') + 1
        self.station_names = station.text[start_index: -2]

        self.station = {}
        for item in self.station_names.split('@'):
            if item:
                tmp = item.split('|')
                self.station[tmp[1]] = tmp[2]


def main():
    train_data = TrainData()
    list_data = train_data.get_filter_train_info('2019-01-20', '广州', '茂名')
    print(list_data)


if __name__ == '__main__':
    main()
