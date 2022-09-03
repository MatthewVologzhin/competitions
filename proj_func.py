import re
import numpy as np
import pytesseract

def time_transformator(time):
    """
    Функция принимает строку времени и преобразует её в СЕКУНДНЫЙ формат
    :param time: Строковый параметр вида "**:**:**"
    :return: Численный параметр
    """
    time = re.split(r'[:,.]', time)
    new_time = list()
    for el in time:
        if el[0] == 0 and el[1] != 0:
            new_time.append(int(el[1]))
        else:
            new_time.append(int(el))
    new_time[0] = new_time[0]*60**2
    new_time[1] = new_time[1]*60
    new_time[2] = new_time[2]
    return sum(new_time)

def normalize_dt(date, time):
    """
    Функция возвращает Дату и Время, исключая возможные артефакты DataSet'а
    :param date: Строковый параметр вида "**-**-****"
    :param time: Строковый параметр вида "**:**:**"
    :return: Одномерный массив [Дата, Время]
    """
    if type(date) != str or type(time) != str:
        print('Ошибка типа данных! Не строковый формат входных данных')
    artefacts = re.compile(r'[.;,]')
    tab_artefs = re.compile(r'[ \t\n]')
    if tab_artefs.search(date) != None:
        date = tab_artefs.sub('', date)
    if tab_artefs.search(time) != None:
        time = tab_artefs.sub('', time)
    if artefacts.search(time) != None:
        time = artefacts.sub('', time)
    return [date, time]

def correct_data(data):

    """Функция, полностью обрабатывающая предоставляемый DataSet"""

    def change_type(data, format_='int64'):
        """
        Функция преобразует все численные данные в один тип данных
        :param data:  DataFrame (pandas)
        :return: DataFrame (pandas)
        """
        switcher = 0
        names = list(data.columns)
        for i in range(len(names)):
            if type(data[names[i]][0]) == np.float64:
                data[names[i]] = data[names[i]].astype(format_)
                switcher = 1
        if switcher == 1:
            print('Типы численных данных были изменены!')
        return data

    def fix_dt(str_):
        """
        Функция уничтожает артефакты данных Даты и Времени, а также меняет положение дат
        :param str_: Строка формата **-**-**** **:**:**
        :return: Строка формата **-**-**** **:**:**
        """
        artef_date = re.compile(r'[,.: ]')
        artef_time = re.compile(r'[.,]',)
        dt_list = re.split(r' ',str_ , maxsplit=1)
        dt_list[0] = artef_date.sub('', dt_list[0])
        dt_list[1] = artef_time.sub(':', dt_list[1])
        dt_list[1] = re.sub(r' ', '', dt_list[1])
        date_list = dt_list[0].split('-')
        date_list = [date_list[1], date_list[2], date_list[0]]
        date_list = '-'.join(date_list)
        dt_list[0] = date_list
        return ' '.join(dt_list)

    def correct_id(data):
        """
        Функция, возвращающая DataFrame с корректными ID
        :param data: DataFrame (pandas)
        :return: DataFrame (pandas)
        """
        pos = 1
        for i in list(data['id']):
            data.loc[pos-1, 'id'] = pos
            pos += 1
        print('ID были исправлены!')
        print('--------')
        return data

    def find_artef_time(data):
        """
        Функция, имплементирующая поиск ошибок во времени (дни, месяцы и годы не проверяются)
        :param data: DataFrame (pandas)
        :return: DataFrame (pandas)
        """
        hours_error = list()
        minute_error = list()
        seconds_error = list()
        dict_ = dict()
        counter = 0
        for date in data['date']:
            date = date.split(' ')
            switcher = 0
            time = [int(x) for x in date[1].split(':')]
            hours, minute, seconds = time[0], time[1], time[2]
            time_1 = [str(x) for x in time]
            if seconds > 59:
                switcher = 1
                minute += seconds//60
                seconds %= 60
                seconds_error.append(':'.join(time_1))
            if minute > 59:
                switcher = 1
                hours += minute//60
                minute %= 60
                minute_error.append(':'.join(time_1))
            if hours > 23:
                switcher = 1
                hours %= 24
                hours_error.append(':'.join(time_1))
            if switcher == 1:
                dict_.update({counter: date[0] + ' {}:{}:{}'.format(hours,
                                                                minute,
                                                                seconds)})
            counter += 1

        indices = list(dict_.keys())
        values = list(dict_.values())
        data.loc[indices, 'date'] = values

        print('Исправленные ошибки времени:')
        print('По часам', hours_error)
        print('По минутам', minute_error)
        print('По секундам', seconds_error)

        return data

    print('Обрабатываем данные:\n----------------')
    data = change_type(data)
    print('--------')
    data['date'] = data['date'].apply(lambda x: fix_dt(x))
    print('Артефакты времени были исправлены!\n--------')
    data = find_artef_time(data)
    print('--------')
    data = correct_id(data)
    print('----------------')
    return data

def detect_pos_dt(config, frame):
    data = pytesseract.image_to_data(frame, config=config)     #Определяем ВСЕ тексты
    data = data.splitlines()
    for el in data:
        if re.findall(r'..:..:..', el) == []:                       #Поиск времени
            pass
        else:
            e = el.split()
            x_t, y_t, w_t, h_t = int(e[6]), int(e[7]), int(e[8]), int(e[9])

        if re.findall(r'..[-]..[-]....', el) == []:                 #Поиск даты
            pass
        else:
            e = el.split()
            x_d, y_d, w_d, h_d = int(e[6]), int(e[7]), int(e[8]), int(e[9])
    return (x_d, y_d, w_d, h_d), (x_t, y_t, w_t, h_t)

