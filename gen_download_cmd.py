#!/volume1/@appstore/py3k/usr/local/bin/python3
import requests
import re
import json
import os
import logging
import argparse
import time
import json
#import pandas
from openpyxl import load_workbook
from openpyxl import Workbook

aid_file = "./aid_done.list"
cid_file = "./cid_done.list"
down_file= "./download.list"
json_file = "./download.json" 
fail_file = "./fail.list"
base_out_dir = '.'

#excel_file = "./log.xlsx"
in_excel= "./bilibili.xlsx"

pat_filter = re.compile(r'/|\s|\x10')

def dump_log(args):
    abs_cur_path = os.path.abspath(os.path.expandvars(os.path.curdir))
    if args.debug:
        level = logging.DEBUG
    else :
        level = logging.INFO

    format_sh = '[%(levelname)s] %(message)s'
    format_fh = '%(asctime)s | %(funcName)s() | L%(lineno)s | [%(levelname)s] \n\t%(message)s'
    '''
        %(levelno)s     打印日志级别的数值
        %(levelname)s   打印日志级别名称
        %(pathname)s    打印当前执行程序的路径
        %(filename)s    打印当前执行程序名称
        %(funcName)s    打印日志的当前函数
        %(lineno)d      打印日志的当前行号
        %(asctime)s     打印日志的时间
        %(thread)d      打印线程id
        %(threadName)s  打印线程名称
        %(process)d     打印进程ID
        %(message)s     打印日志信息
    '''

    if args.log_file:

        logging.basicConfig(
            filename = args.log_file, 
            filemode = 'w', 
            datefmt  = "%y-%m-%d %H:%M:%S",
            format   = format_fh, 
            level    = level)

        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(logging.Formatter(format_sh))
        logging.getLogger('').addHandler(console);
    else:
        logging.basicConfig(
            format = format_sh, 
            level  = level)

def get_args_top():
    #TODO 指定输出路径
    parser = argparse.ArgumentParser()
    st = "debug option"
    parser.add_argument('-d', '--debug', default = False, action='store_true', help=st)

    st = "only print info"
    parser.add_argument('-oi', '--only_info', default = False, action='store_true', help=st)

    st = "download enable"
    parser.add_argument('-ed', '--enable_download', default = False, action='store_true', help=st)

    st = "download skip"
    parser.add_argument('-es', '--enable_skip', default = False, action='store_true', help=st)

    st = "gen_download_list"
    parser.add_argument('-gd', '--gen_download_list', default = False, action='store_true', help=st)

    st = "add mid"
    parser.add_argument('-mid', '--add_mid', default = "", help=st)

    st = "add aid"
    parser.add_argument('-aid', '--add_aid', default = "", help=st)

    st = "set output log file"
    parser.add_argument('-l', '--log_file', default = "", help=st)

    st = "set output dir name"
    parser.add_argument('-o', '--out_dir', default = ".", help=st)

    args = parser.parse_args()
    return args

def youget_download(cmd):
    try :
        info = os.system(cmd)
        print(info)
        return True
    except Exception as e:
        print(e)

def get_download_list(args, log):
    def gen_sheet(ws, aid_list):
        skip_cnt = 0
        curr_row = 1
        curr_col = 1
        headerList = ['', 'aid' ,'cid' ,'title' ,'flag' ,'status' ,'author' ,'created_at' ,'description' ,'page' ,'download_url' ,'output_dir' ,'output_name']
        headerHash = {}
        for i in range(1, len(headerList)):
            e = headerList[i]
            headerHash[e] = i
            ws.cell(row = curr_row, column = i, value = e)

        for aid in aid_list :
            #log.debug("aid= %s "%(aid))
            curr_row += 1
            #status = ws.cell(row = curr_row, column = 4).value
            #enable_skip = True
            #enable_skip = False
            
            status = 'done' if str(aid) in aid_done_set else 'todo'
            ws.cell(row = curr_row, column =headerHash['status']        , value = status)
            if status == 'done' and args.enable_skip == True:
                #log.debug("skip %s "%(aid))
                skip_cnt += 1
                continue
            api = "http://api.bilibili.com/view?type=json&appkey=8e9fc618fbd41e28&id=" + str(aid) + "&batch=1"
            log.debug("get video info api is %s "%(api))
            r = requests.get(api)
            j = json.loads(r.text)
            #log.info("json = \n%s"%j)
            if 'code' in j.keys() :
                continue

            '''
            while 'code' in j.keys() :
                log.info("json = \n%s"%j)
                for i in range(10):
                    log.info('return 403, wait %s'%i)
                    time.sleep(1)
                r = requests.get(api)
                j = json.loads(r.text)
            '''

            up_name = j['author']
            title = j['title']
            #title = re.sub('\x10' ,'', title)
            #title = re.sub(r'/|\s','', title)
            title = pat_filter.sub('', title)
            #status = 'done' if str(aid) in done_set else 'todo'
            #if "%s%s"%("av",aid) in aid_done_set:
            ws.cell(row = curr_row, column = headerHash['aid'],         value = aid)
            ws.cell(row = curr_row, column = headerHash['title'],       value = title)
            ws.cell(row = curr_row, column = headerHash['author'],      value = up_name)
            ws.cell(row = curr_row, column = headerHash['created_at'],  value = j['created_at'])
            ws.cell(row = curr_row, column = headerHash['description'], value = j['description'])
            ws.cell(row = curr_row, column = headerHash['page'],        value = len(j['list']))
            if len(j['list']) > 1 :
                for e in j['list']:
                    curr_row += 1
                    cid = e['cid']
                    status = 'done' if str(cid) in cid_done_set else 'todo'

                    ws.cell(row = curr_row, column = 5, value = status)
                    if status == 'done' and args.enable_skip == True:
                        continue

                    url = "https://www.bilibili.com/video/av%s/index_%s.html"%(aid, e['page'])
                    output_dir = "%s/%s/%s"%(base_out_dir, up_name, title )
                    output_name= pat_filter.sub('', e['part'].strip())
                    ws.cell(row = curr_row, column =headerHash['cid']           , value = cid)
                    ws.cell(row = curr_row, column =headerHash['title']         , value = e['part'])
                    ws.cell(row = curr_row, column =headerHash['author']        , value = up_name)
                    ws.cell(row = curr_row, column =headerHash['page']          , value = e['page'])
                    ws.cell(row = curr_row, column =headerHash['download_url']  , value = url)
                    ws.cell(row = curr_row, column =headerHash['output_dir']    , value = output_dir)
                    ws.cell(row = curr_row, column =headerHash['output_name']   , value = output_name)
                    flag = ws.cell(row = curr_row, column =headerHash['flag']).value
                    flag = True if flag is not None and str(flag) != 'OFF' else False
                    if status != 'done':
                        log.info("append video %s -> '%s' by %s"%(aid, title, up_name))
                        download_list.append((url, output_dir, output_name, aid, cid, flag))
            else :
                url = "https://www.bilibili.com/video/av%s"%(aid)
                output_dir  = "%s/%s"%(base_out_dir, up_name)
                output_name = pat_filter.sub('', title)
                cid = j['list'][0]['cid']
                ws.cell(row = curr_row, column =headerHash['cid']           , value = cid)
                ws.cell(row = curr_row, column =headerHash['download_url']  , value = url)
                ws.cell(row = curr_row, column =headerHash['output_dir']    , value = output_dir)
                ws.cell(row = curr_row, column =headerHash['output_name']   , value = output_name)

                flag = ws.cell(row = curr_row, column =headerHash['flag']).value
                flag = True if flag is not None and str(flag) != 'OFF' else False
                if status != 'done':
                    log.info("append video %s -> '%s' by %s"%(aid, title, up_name))
                    download_list.append((url, output_dir, output_name, aid, cid, flag))
        return (skip_cnt, download_list) 
        
    def get_done_set(filename):
        if not os.path.exists(filename) :
            os.system("touch %s"%filename)

        done_set = set()
        fr = open(filename, 'r')
        for line in fr:
            done_set.add(pat_av_number.sub('', line.strip()))
        fr.close()
        return done_set

    def get_mid_list(sheetname):
        ws = wb[sheetname]
        mid_list = []
        for curr_row in range(2, ws.max_row + 1):
            cell_value = ws.cell(row = curr_row, column = 1).value
            enable = ws.cell(row = curr_row, column = 2).value
            if cell_value is not None and str(enable) == 'enable':
                mid_list.append(cell_value)

        log.info("total up number is %s"%len(mid_list))
        return ws, mid_list

    def get_aid_list(sheetname):
        ws = wb[sheetname]
        aid_list = []
        for curr_row in range(2, ws.max_row + 1):
            cell_value = ws.cell(row = curr_row, column = 1).value
            if cell_value is not None :
                aid = pat_av_number.sub('', cell_value.strip())
                log.debug("aid = '%s'"%aid)
                aid_list.append(aid)
        log.info("total video number is %s"%len(aid_list))
        return ws, aid_list

    download_list = []

    pat_av_number = re.compile(r'^av')

    wb = load_workbook(in_excel)

    aid_done_set = get_done_set(aid_file)
    cid_done_set = get_done_set(cid_file)
    #log.debug(aid_done_set)

    ws, mid_list = get_mid_list('mid')
    ws, aid_list = get_aid_list('aid')
    gen_sheet(ws, aid_list)

    #log.debug("mid list : %s"%mid_list)

    #mid_list = [] # debug
    curr_row = 2
    for mid in mid_list :
        log.info("curr mid is %s"%(mid))
        av_dict, av_list, up_name = get_up_vlist(log, mid)
        if up_name not in wb.sheetnames:
            ws = wb.create_sheet()
            ws.title = up_name
        else :
            #wb.remove_sheet(up_name)
            #ws = wb.create_sheet()
            #ws.title = up_name
            ws = wb[up_name]
        skip_cnt, download_list = gen_sheet(ws, av_list)

        ws = wb['mid']
        ws.cell(row = curr_row, column = 1, value = mid)
        ws.cell(row = curr_row, column = 3, value = up_name)
        ws.cell(row = curr_row, column = 4, value = len(av_list))
        ws.cell(row = curr_row, column = 5, value = skip_cnt)
        curr_row += 1

        log.info("skip/total %s/%s"%(skip_cnt, len(av_list)))
        
    wb.save(in_excel)

    log.info("total %s video(s) to download"%len(download_list))

    #for e in download_list :
    #    log.info("av%s\t%s"%(e[3], e[4]))

    download_json = json.dumps(download_list)
    fw = open(json_file, 'w')
    fw.write(download_json)
    fw.close()
    log.info("Generate json file %s"%(json_file))

    return download_list

def bilibili_downloader(args, log, download_list = []):
    def refresh_download_list(i):
        fw = open(down_file, 'w')
        total_num = len(download_list)
        for j in range(len(download_list)) :
            url, output_dir, output_name ,aid ,cid, flag = download_list[j]
            if flag == False :
                fw.write("(%d/%d) %-15s %s \n"%(j+1, total_num, "Skip", output_name))
            elif j < i :
                fw.write("(%d/%d) %-15s %s \n"%(j+1, total_num, "Completed", output_name))
            elif j == i :
                fw.write("============== \n")
                fw.write("(%d/%d) %-15s %s \n"%(j+1, total_num, "Download ->", output_name))
                fw.write("============== \n")
            else:
                fw.write("(%d/%d) %-15s %s \n"%(j+1, total_num, "Waiting...", output_name))

        fw.close()

    fr = open(json_file, 'r')
    for line in fr:
        download_json = line
    fr.close()

    download_list = json.loads(download_json)

    refresh_download_list(0)
    for i in range(len(download_list)):
        url, output_dir, output_name, aid ,cid, flag= download_list[i]
        if flag == False:
            log.info("Skip %s/%s"%(output_dir, output_name))
            continue


        output_dir = re.sub(r'\.+$', '', output_dir)
        down_cmd = "you-get --output-dir '%s' --output-filename '%s' %s"%(output_dir, output_name, url)
        log.info(down_cmd)
        if args.only_info :
            info_cmd = "you-get --info %s"%(url)
            log.info(info_cmd)
            log.info(down_cmd)
            continue

        if args.enable_download :
            refresh_download_list(i)
            youget_download(down_cmd)
            flag = os.path.isfile(os.path.join(output_dir, "%s.%s"%(output_name, 'flv')))
            if flag == True:    #TODO 判断下载成功
                fa = open(aid_file, 'a')
                fa.write('av%s \n'%(aid))
                fa.close()

                fa = open(cid_file, 'a')
                fa.write('%s \n'%(cid))
                fa.close()
            else :
                fa = open(fail_file, 'a')
                fa.write("av %s/%s %s.flv not found at %s"%(aid, cid, output_name, output_dir))
                fa.close()

def get_up_vlist(log, mid):
    cookies = {
    }

    headers = {
    }

    params = (
    )
    av_dict = {}
    av_list = []
    page_size = 100
    page = 1
    av_cnt = None
    while True:
        url = "http://space.bilibili.com/ajax/member/getSubmitVideos?mid=%s&pagesize=%s&page=%s"%(mid, page_size, page)
        log.debug("get up info api is %s"%url)
        response = requests.get(url, headers=headers, params=params, cookies=cookies)
        j = json.loads(response.text)
        for e in j['data']['vlist'] :
            log.debug("%10s : %s"%(e['aid'], e['title']))
            av_dict[e['aid']] = e['title']
            av_list.append(e['aid'])

        up_name = e['author']

        if av_cnt == None:
            av_cnt = j['data']['count']
            page    += 1
        elif av_cnt > 0:
            av_cnt  -= page_size
            page    += 1
        else:
            break
    return av_dict, av_list, up_name

def main():
    args = get_args_top()
    dump_log(args)
    log = logging
    if args.gen_download_list :
        get_download_list(args, log)

    if args.enable_download or args.only_info :
        bilibili_downloader(args, log)

    if args.add_aid is not None:
        wb = load_workbook(in_excel)
        ws = wb['aid']
        ws.cell(row = ws.max_row + 1, column = 1, value = args.add_aid)
        wb.save(in_excel)

    if args.add_mid is not None:
        wb = load_workbook(in_excel)
        ws = wb['mid']
        ws.cell(row = ws.max_row + 1, column = 1, value = args.add_mid)
        wb.save(in_excel)

if __name__ == '__main__':

    main()
