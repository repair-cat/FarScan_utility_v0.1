from pywinauto.application import Application
import schedule
import os
import datetime
import time
import sys
import psutil


def pid_search():
    '''Поиск PID процесса FarScan - ntvdm.exe'''
    for process in psutil.process_iter():
        try:                                                         # для ловли ошибок доступа к системным процессам
            if process.name() == "ntvdm.exe":
                return process.pid
        except:
            continue


def start_farscan():
    """запуск FarScan"""
    os.startfile(r'C:\Program Files\FS4W_31.yamsovey\FS4W.EXE')             # запуск исполняемого файла FarScan
    pid = pid_search()                                                      # вызов функции поиска PID FarScan
    app = Application().connect(process=pid)                                # подключиться к окну авторизации
    app["Пожалуйста введите ваши"]['ИмяEdit'].type_keys("FARSCAN")          # вводим логин
    app["Пожалуйста введите ваши"]['ПарольEdit'].type_keys("MANAGER")       # вводим пароль
    app["Пожалуйста введите ваши"].Да.click()


def confirm_alarm(pid):
    """Подтверждение и сброс аварийной сигнализации"""
    app = Application().connect(process=pid)                                    # подлючаемся к процессу
    win = app.FS4W_Manager_Class
    win.menu_select("Команды->Сводный отчет...")
    report = app.window(title="Сводный отчет")
    report.menu_select("Команды->Подтверждение аварийной сигнализации...")
    app.window(title="Подтверждение аварийной сигнализации").Все.click()        # подтверждаем сброс всех ошибок


def create_dir(filename):
    """Ежемесячное создание директории"""
    # Создает директорию C:\LOG\год\месяц
    # % B - месяц,% Y - год
    path = r'C:\LOG\{year}\{month}'.format(
            year=filename.strftime("%Y"),
            month=filename.strftime("%B")
        )
    os.makedirs(path)                                                           # создаем директорию
    print('directory was created')
    print()


def change_log(pid):
    filename = datetime.date.today()  # получаем текущую дату
    '''Создаем экземляр класса приложения, подключаемся к уже запущенному FarScan через PID процесса'''
    app = Application().connect(process=pid)
    '''Альтернаивное имя окна программы "FS4W_Manager_Class"'''
    win = app.FS4W_Manager_Class                                                # определяем окно программы.
    win.menu_select("Конфигруация->Режим файла регистрации...")                 # выбирает нужный элемент меню программы
    win_journal = app["Режим дискового\принтерного журнала"]                    # обьект окна "Режим дискового\принтерного журнала" присваиваем переменной
    win_journal.Отключить.click()                                               # кликает Отключить в окне выбора пути лога
    win_journal.Да.click()                                                      # кликает Да в окне выбора пути лога
    win.menu_select("Конфигруация->Режим файла регистрации...")
    win_journal.Edit.click()                                                    # кликнуть на поле пути лога
    win_journal.Edit.select()                                                   # выделить текст пути лога
    win_journal.Edit.type_keys(r'C:\LOG\{year}\{month}\{day}.log'.format(       # смена имени лога в соответсвии с текущей датой
                year=filename.strftime("%Y"),
                month=filename.strftime("%B"),
                day=filename.strftime("%d")
        )
    )
    win_journal.Включить.click()                                   # кликает "Включить" в окне выбора пути лога
    win_journal.Да.click()
    print('log was changed')
    print(filename)
    print()
    global log_flag
    log_flag = True                                                # флаг - "лог создан"
    return log_flag


log_flag = False                                                   # флаг - "создан ли лог"

"""Автозапуск FarScan при запуске системы"""
start = sys.argv[1]                                                # параметр для автозапуска FarScan
if start == 'start':
    start_farscan()


schedule.every().day.at('00:01').do(change_log, pid_search())       # создание нового лог-файла каждый день в 00:01

"""Запуск цикла обновления лог-файла"""
while True:
    log_name = datetime.date.today()
    directory = r'C:\LOG\{year}\{month}'.format(
        year=log_name.strftime("%Y"),
        month=log_name.strftime("%B"),
    )
    # если наступило 1 число месяца и директория не была создана
    if log_name.strftime("%d") == '01' and not os.path.exists(directory):
        create_dir(log_name)                                      # создаем директорию
    schedule.run_pending()                                        # запуск функции создания лога
    if log_flag:                                                  # если лог был создан
        time.sleep(10)                                            # пауза в программе на 10 сек, чтобы ошибки обновились
        confirm_alarm(pid_search())                               # сброс ошибок после создания лога
        log_flag = False                                          # возврат флага в исходное состояние
