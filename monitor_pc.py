#pyinstaller -w --onefile files.py
import requests,telebot,json,os,pyautogui,time,GPUtil,csv as csv,matplotlib.pyplot as plt,numpy as np,pandas as pd,socket,schedule,time,uptime
from pythonping import ping
from pathlib import Path
from matplotlib import pyplot as plt
from matplotlib import style
from dateutil import parser as dt_parser


#url = "https://ethereum.miningpoolhub.com/index.php?page=api&action=getuserworkers&api_key=1f3ab92a96dd360ab21566512de09b4738005519b29d958ee739e&id=55998"
turl = "https://api.telegram.org/bot"
token = '537569389:AAHcrQi9s7NLZKzeixwFpTrvot-E8C5z2YE'
chat_id = '-112425623'
#r = requests.get(url)
#data = json.loads(r.text)
filename = time.strftime("%Y%m%d-%H%M%S") + ".jpg"


def send_message(chat_id, text):
    requests.get(f'{turl}{token}/sendMessage?chat_id={chat_id}&text={text}')

def send_photo(chat_id, img):
    files = {'photo': open(img, 'rb')}
    requests.get(f'{turl}{token}/sendPhoto?chat_id={chat_id}', files=files)

#Построение графика по метрике
def send_grafs():
    time_job = time.strftime("%d.%m.%Y-%H:%M:%S")
    gpu_data = pd.read_csv('bd.csv', delimiter=';')
    style.use('ggplot')
    fig=plt.figure(dpi=128,figsize=(8,6))
    mycolors = ['tab:red', 'tab:blue', 'tab:green', 'tab:orange', 'tab:brown', 'tab:grey', 'tab:pink', 'tab:olive']
    unigue = []
    for n in gpu_data['id']:
        if n not in unigue:
            unigue.append(n)
    for u in unigue:
        z_data = gpu_data["temperature"][gpu_data["id"] == u]
        o_data = gpu_data["date"][gpu_data["id"] == u]
        plt.plot(o_data, z_data, label=u, linewidth=3, linestyle='-')
    plt.xlabel('date')
    fig.autofmt_xdate()
    plt.ylabel('temperaturedate')
    plt.legend()
    plt.savefig(filename)
    send_message(chat_id, 'График' +' - '+ node)
    send_photo(chat_id, filename)

#Метрика
def metrika_job():
        time_job = time.strftime("%d.%m.%Y-%H:%M:%S")
        count = 0
        gpu_count = 0
        try:
            file = open("bd.csv", mode="r+")
            base = file.readlines()
            for gpu in GPUtil.getGPUs():
                file.seek(0, 2)
                file.write('\n' + f'{gpu.id};{time.strftime("%d.%m.%Y-%H:%M:%S")};{gpu.name};{gpu.temperature};{gpu.load*100}%')
                gpu_count += 1
            print(gpu_count)
            file.close()
            print(time_job + " Добавлена запись в метрику")
            for row in base:
                count += 1
            print(count)
            if count >= 100:
                filename1 = "bd.csv"
                bkp_filename = filename1 + ".bkp"
                try:
                    Path(bkp_filename).unlink()
                    print("udalen fail")
                    Path(filename1).rename(bkp_filename)
                    fn_in = Path(bkp_filename)
                    fn_out = Path(filename1)
                    with open(fn_in) as fin, open(fn_out, "w") as fout:
                        for i, line in enumerate(fin):
                            if i >= 1 and i <= gpu_count:
                                continue
                            fout.write(line)
                except:
                    Path(filename1).rename(bkp_filename)
                    fn_in = Path(bkp_filename)
                    fn_out = Path(filename1)
                    with open(fn_in) as fin, open(fn_out, "w") as fout:
                        for i, line in enumerate(fin):
                            if i >= 1 and i <= gpu_count:
                                continue
                            fout.write(line)

        except:
            print("fail open bd file")
            file = open("bd.csv", mode="w")
            file.write("id;date;name;temperature;load")
            print(time_job + " Создание файла метрики")
            for gpu in GPUtil.getGPUs():
                file.write('\n' + f'{gpu.id};{time.strftime("%d.%m.%Y-%H:%M:%S")};{gpu.name};{gpu.temperature};{gpu.load*100}%')
            file.close()

#Запись хоста в файл
try:
    file = open("node.txt", mode="rt")
    node = file.read()
    file.close()
except:
    node = input('Введит название воркера: ')
    file = open("node.txt", "w")
    file.write(node)
    file.close()

#Проверка uptime Pc
if uptime.uptime() <= 720.000:
    print(time_job + ' ' + node + " - был перезагружен, uptime: " + str(float('{:.1f}'.format(uptime.uptime()/60))) + " минут")
    send_message(chat_id, node + " - был перезагружен, uptime: " + str(float('{:.1f}'.format(uptime.uptime()/60))) + " минут")

#Проверка количества видеокарт при загрузке
g_count = 0
for gpu in GPUtil.getGPUs():
    g_count += 1
print(g_count)

#Проверка количества видеокарт во время работы
def gpus_job():
    time_job = time.strftime("%d.%m.%Y-%H:%M:%S")
    gpus_count = 0
    for gpu in GPUtil.getGPUs():
        gpus_count += 1
    if g_count != gpus_count:
        print( time_job +' '+ u+' - '+'Упала одна из видеокарт')
        send_message(chat_id, u+' - '+'Упала одна из видеокарт')

#Проверка температуры видеокарты
def alarm_job():
    time_job = time.strftime("%d.%m.%Y-%H:%M:%S")
    alarm = []
    al_count = 0
    for gpu in GPUtil.getGPUs():
        if gpu.temperature >= 68.0:
            print(time_job + ' ' +node + " - Повышенный уровень температуры у видеокарты" + ' №' + f'{gpu.id}' + " - " + f'{gpu.temperature}')
            ala = (node + " - Повышенный уровень температуры у видеокарты" + ' №' + f'{gpu.id}' + " - " + f'{gpu.temperature}')
            alarm.append(ala)
    if alarm:
        print(time_job + " Отправлено сообщение о превышении температуры")
        send_message(chat_id, ''.join(alarm))

#Проверка доступности хоста
def socket_job():
    time_job = time.strftime("%d.%m.%Y-%H:%M:%S")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("europe.ethash-hub.miningpoolhub.com", 20535))
    except socket.error:
        if ping("8.8.8.8", verbose=False).success:
            print(time_job + " Хост доступен")
        else:
            os.system('shutdown -r -t 0')
    else:
        print(time_job + " Хост доступен")
    finally:
        s.close()

#Проверка хэшрейта по API (Если хэш 0 записывает в файл, если в файле больше 4 строк - отправка сообщения)
def api_job():
    url = "https://ethereum.miningpoolhub.com/index.php?page=api&action=getuserworkers&api_key=1f3ab92a96dd360abcf9e86e04d3456c1f12de09b4738005519b29d958ee739e&id=590194"
    r = requests.get(url)
    data = json.loads(r.text)
    time_job = time.strftime("%d.%m.%Y-%H:%M:%S")
    h_count = 0
    for worker in data['getuserworkers']['data']:
        u = worker ['username']
        w = worker['hashrate']
        if w == 0  and u != "Denis173.ram" and u != "Denis173.home02":
            try:
                h_file = open("zero_hashrate.csv", mode="r+")
                hash = h_file.readlines()
                for h_row in hash:
                    h_count += 1
                if h_count >= 3:
                    send_message(chat_id, u+' - '+'Упала')
                    Path("zero_hashrate.csv").unlink()
                else:
                    h_file.seek(0, 2)
                    h_file.write(u+' - '+'Упала'+'\n')
                    print(time_job + ' ' + u + ' - '+'Упала')
                    h_file.close()
            except:
                h_file = open("zero_hashrate.csv", mode="w")
                h_file.seek(0, 2)
                h_file.write(u+' - '+'Упала'+'\n')
                print(time_job + ' ' + u + ' - '+'Упала')
                h_file.close()
        else:
            try:
                h_file = open("zero_hashrate.csv", mode="r")
                h_file.close()
                Path("zero_hashrate.csv").unlink()
                print(time_job + " Файл отслеживания ноды по API удалён")
            except:
                print(time_job + " Все ноды в норме")

# спланируй.каждые(10).минут.сделать(работу)
schedule.every(4).minutes.do(api_job)
schedule.every(7).minutes.do(socket_job)
schedule.every(3).minutes.do(alarm_job)
schedule.every(10).minutes.do(gpus_job)
schedule.every(60).minutes.do(metrika_job)
schedule.every().day.at("21:00").do(send_grafs)

while True:
  schedule.run_pending()
  time.sleep(1)
        #screen = pyautogui.screenshot(filename)
#       #send_message(chat_id, text)
#       #send_photo(chat_id, filename)
#       #os.system('shutdown -r -t 0')
