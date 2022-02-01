#!/usr/bin/env python3

import asyncio, aiofiles, pathlib, aiohttp
import re, json, traceback
import random

ids_map = {
    "⿰": {"k": 's', "n": 2},
    "⿱": {"k": 'd', "n": 2},
    "⿲": {"k": 't', "n": 3},
    "⿳": {"k": 'y', "n": 3},
    "⿴": {"k": 'q', "n": 2},
    "⿵": {"k": 'w', "n": 2},
    "⿶": {"k": 'e', "n": 2},
    "⿷": {"k": 'r', "n": 2},
    "⿸": {"k": 'u', "n": 2},
    "⿹": {"k": 'i', "n": 2},
    "⿺": {"k": 'o', "n": 2},
    "⿻": {"k": 'p', "n": 2},
}

py_a = ['ā', 'á', 'ǎ', 'à']
py_o = ['ō', 'ó', 'ǒ', 'ò']
py_e = ['ē', 'é', 'ě', 'è']
py_i = ['ī', 'í', 'ǐ', 'ì']
py_u = ['ū', 'ú', 'ǔ', 'ù']
py_v = ['ǖ', 'ǘ', 'ǚ', 'ǜ', 'ü']
py_n = {'ǹ', 'ń', 'ň'}
py_m = {'ḿ'}

async def drop_shengdiao(py):
    ret = ""
    sd = 1
    for c in py:
        if c in py_a:
            sd = py_a.index(c) + 1
            ret = ret + "a"
        elif c in py_o:
            sd = py_o.index(c) + 1
            ret = ret + "o"
        elif c in py_e:
            sd = py_e.index(c) + 1
            ret = ret + "e"
        elif c in py_i:
            sd = py_i.index(c) + 1
            ret = ret + "i"
        elif c in py_u:
            sd = py_u.index(c) + 1
            ret = ret + "u"
        elif c in py_v:
            sd = py_v.index(c) + 1
            if sd == 5:
                sd = 1
            ret = ret + "v"
        elif c in py_n:
            ret = ret + "n"
        elif c in py_m:
            ret = ret + "m"
        else:
            ret = ret + c
    return ret, sd

async def get_zdic_data(hz):
    if not pathlib.Path(f"./zdic_data/{hz}.txt").exists():
        # print(f"download {hz}")
        async with aiohttp.ClientSession() as session:
            async with session.request("get", f"https://www.zdic.net/hans/{hz}") as resp:
                async with aiofiles.open(f"./zdic_data/{hz}.txt", mode="w") as f:
                    await f.write(await resp.text())
    async with aiofiles.open(f"./zdic_data/{hz}.txt", mode="r") as f:
        return await f.read()

async def get_py(zdic_data, hz):
    py_list = []
    for py in zdic_data[hz]['pinyin']:
        # print(py)
        py_dropped, sd = await drop_shengdiao(py)
        # print(py_dropped)
        ret = list()
        ret.append(py_dropped[0])
        yunmu = ['a', 'o', 'e', 'i', 'u', 'v']
        if py_dropped[0] in yunmu or py[0] in py_n or py[0] in py_m:
            ret.append(py_dropped[0:])
        else:
            if py_dropped[1] != "h":
                ret.append(py_dropped[1:])
            else:
                ret.append(py_dropped[2:])
        # py_list.append((ret, sd))
        py_list.append(ret)
    return py_list

async def get_bihua(zdic_data, hz):
    return zdic_data[hz]['bihua']

async def check_special_part(zdic_data, hz):
    if hz in {'钅'}:
        return 'z'
    elif hz in {'艹'}:
        return 'b'
    elif hz in {'亻'}:
        return 'f'
    elif hz in {'氵'}:
        return 'c'
    elif hz in {'日', '犭'}:
        return 's'
    elif hz in {'月'}:
        return 'd'
    elif hz in {'口'}:
        return 'l'
    elif hz in {'土'}:
        return 'v'
    elif hz in {'木'}:
        return 'x'
    elif hz in {'扌'}:
        return 'u'
    elif hz in {'山', '𧾷'}:
        return 'n'
    elif hz in {'目', }:
        return 'a'
    elif hz in {'纟', }:
        return 'e'
    elif hz in {'讠', }:
        return 'w'
    else:
        return ''






async def bihua_parser(bihua_string):
    ret = ""
    tmp = ""
    for bh in bihua_string:
        tmp = tmp + bh
        if len(tmp) == 2:
            if tmp == "11":
                ret = ret + "h"
            elif tmp == "12":
                ret = ret + "j"
            elif tmp == "13":
                ret = ret + "k"
            elif tmp == "14":
                ret = ret + "l"
            elif tmp == "15":
                ret = ret + "m"
            elif tmp == "21":
                ret = ret + "a"
            elif tmp == "22":
                ret = ret + "s"
            elif tmp == "23":
                ret = ret + "d"
            elif tmp == "24":
                ret = ret + "f"
            elif tmp == "25":
                ret = ret + "g"
            elif tmp == "31":
                ret = ret + "q"
            elif tmp == "32":
                ret = ret + "w"
            elif tmp == "33":
                ret = ret + "e"
            elif tmp == "34":
                ret = ret + "r"
            elif tmp == "35":
                ret = ret + "t"
            elif tmp == "41":
                ret = ret + "y"
            elif tmp == "42":
                ret = ret + "u"
            elif tmp == "43":
                ret = ret + "i"
            elif tmp == "44":
                ret = ret + "o"
            elif tmp == "45":
                ret = ret + "p"
            elif tmp == "51":
                ret = ret + "z"
            elif tmp == "52":
                ret = ret + "x"
            elif tmp == "53":
                ret = ret + "c"
            elif tmp == "54":
                ret = ret + "v"
            elif tmp == "55":
                ret = ret + "b"
            tmp = ""

    if tmp == "1":
        ret = ret + "z"
    elif tmp == "2":
        ret = ret + "x"
    elif tmp == "3":
        ret = ret + "c"
    elif tmp == "4":
        ret = ret + "v"
    elif tmp == "5":
        ret = ret + "b"
    return ret

async def sort_danzi():
    async with aiofiles.open("danzi_freq.txt", mode="r") as f:
        ma = re.findall(r"[0-9]\s(\S{1})\s([0-9]+)\s", await f.read())
        freq = { k: int(v) for k, v in ma }
        ty7k = list()
        async with aiofiles.open("ty7k/words.txt", mode="r") as f:
            async for line in f:
                hz = line.strip()
                if not hz in freq:
                    freq[hz] = 1
                ty7k.append(hz)
        return sorted(ty7k, key=lambda item: freq[item], reverse=True)


class GenMB:
    def __init__(self):
        self.yunmu_groups = [
            {'a',  'ai',  'ao',  'ou',  'ei'},
            {'o',  'an',  'ang', 'in',  'ing'},
            {'e',  'en',  'eng',  'un',  'ong'},
            {'i',  'ia',  'ie',  'iu'},
            {'u',  'uo',  'ua',  'ui',  'ue', 've'},
            {'v',  'iao',  'iang',  'ian',  'iong', 'uang', 'uai', 'uan'}
        ]
        self.fast_code = {
            "的": "d",
            "一": "y",
            "不": "b",
            "是": "s",
            "人": "r",
            "在": "z",
            "有": "yu",
            "我": "w",
            "他": "t",
            "和": "h",
            "而": "e",
            "你": "n",
            "那": "na",
            "可": "k",
            "啊": "a",
            "了": "l",
            "这": "v",
            "们": "m",
        }
        self.special_ids_map = {
            "⿰--": "a",
            "⿰-⿰": "s",
            "⿰-⿸": "d",
            "⿰-⿳": "f",
            "⿰⿱-": "c",
            "⿱--": "h",
            "⿱-⿰": "j",
            "⿱-⿱": "k",
            "⿱⿰-": "l",
            "⿱⿱-": "n",
        }

    def get_ids_string(self, hz):
        ma = re.search(r"U\S+\s+(" + hz + r")\s+([^\[\s]+)", self.ids_data)
        ids_string = ma.group(2)
        return ids_string

    # bh_list i ids_tag
    async def ids_parser_inner(self, ids_string, start, depth):
        if ids_string[start] in ids_map:
            ret = []
            i = start + 1
            n = ids_map[ids_string[start]]['n']
            for ii in range(n):
                bh_list, i, ids_tag = await self.ids_parser_inner(ids_string, i, depth - 1)
                for bh in bh_list:
                    ret.append(bh)
            return ret, i, ids_string[start]
        else:
            sp_key = await check_special_part(self.zd_data, ids_string[start])
            if sp_key != "":
                return [sp_key, ], start + 1, "-"
            try:
                st = self.zd_data[ids_string[start]]['struct']
                if "单" in st or "独" in st:
                    return [await get_bihua(self.zd_data, ids_string[start]), ], start + 1, '-'
            except:
                pass
            if depth >= 1:
                sub_ids = self.get_ids_string(ids_string[start])
                if sub_ids[0] in ids_map:
                    bh_list, i, ids_tag = await self.ids_parser_inner(sub_ids, 0, depth - 1)
                    return bh_list, start + 1, ids_tag
                else:
                    return [await get_bihua(self.zd_data, ids_string[start]), ], start + 1, '-'
            else:
                return [await get_bihua(self.zd_data, ids_string[start]), ], start + 1, '-'



    async def ids_parser(self, ids_string):
        # print(ids_string)
        ret = []
        ids_ret = ""
        i = 0
        if ids_string[i] in ids_map:
            if ids_string[i] in ("⿰", "⿱"):
                dep = 1
            else:
                dep = 1
            ids_ret = ids_string[i]
            n = ids_map[ids_string[i]]['n']
            k = ids_map[ids_string[i]]['k']
            i = i + 1
            for ii in range(n):
                bh_list, i, ids_tag = await self.ids_parser_inner(ids_string, i, dep)
                ret.append(bh_list)
                ids_ret = ids_ret + ids_tag
        else:
            return "" , "-"
        # keya = await bihua_parser(ret[0][0] + ret[1][0])
        parta = ret[0][0]
        if parta[0].isdigit():
            bh = ""
            for b in parta:
                if b.isdigit():
                    bh = bh + b
            keya = await bihua_parser(bh)
        else:
            keya = parta[0]

        partb = ret[1][0]
        if partb[0].isdigit():
            bh = ""
            for b in partb:
                if b.isdigit():
                    bh = bh + b
            keyb = await bihua_parser(bh)
        else:
            keyb = partb

        if k in ['s']:
            if ids_ret in ("⿰-⿱",):
                partc = ret[1][1]
                if partc[0].isdigit():
                    bh = ""
                    for b in partc:
                        if b.isdigit():
                            bh = bh + b
                    keyc = await bihua_parser(bh)
                else:
                    keyc = partc
                return keya[0] + keyb[0] + keyc[0], ids_ret
            if ids_ret in self.special_ids_map:
                return self.special_ids_map[ids_ret] + keya[0] + keyb[0], ids_ret
            return 'v' + keya[0] + keyb[0], ids_ret
        if k in ['d']:
            if ids_ret in self.special_ids_map:
                return self.special_ids_map[ids_ret] + keya[0] + keyb[0], ids_ret
            return 'm' + keya[0] + keyb[0], ids_ret


        return k + keya[0] + keyb[0], ids_ret

    async def get_code(self, hz, py_list):
        ids_ret = "-"
        ma = re.search(r"U\S+\s+(" + hz + r")\s+([^\[\s]+)", self.ids_data)
        ids_string = ma.group(2)
        if "单" in self.zd_data[hz]['struct'] or "独" in self.zd_data[hz]['struct']:
            bh_parsed = "g" + (await bihua_parser(await get_bihua(self.zd_data, hz)))[:2]
        else:
            try:
                bh_parsed, idst = await self.ids_parser(ids_string)
                ids_ret = idst
                # if ids_ret == "⿰-⿱":
                #     print(f'{hz} - {ids_string}')
            except Exception as e:
                # traceback.print_exc()
                bh_parsed = ""
                print(f'{e}: {hz} - {ids_string}')
        if bh_parsed == "":
            bh_parsed = "g" + (await bihua_parser(await get_bihua(self.zd_data, hz)))[:2]
        m = set()
        for py in py_list:
            py1 = py[0]
            m.add(py1 + bh_parsed)
        return m, ids_ret

    async def run(self):
        mb_data = dict()
        ids_stats = dict()
        async with aiofiles.open("zdic_data.json", mode="r") as f:
            self.zd_data = json.loads(await f.read())

        async with aiofiles.open("ids_data/ids.txt", mode="r") as ids_file:
            self.ids_data = await ids_file.read()

        count = 0
        for hz in await sort_danzi():
            py_list = await get_py(self.zd_data, hz)
            m, ids_tag = await self.get_code(hz, py_list)
            if ids_tag in ids_stats:
                ids_stats[ids_tag] += 1
            else:
                ids_stats[ids_tag] = 1
            if hz in self.fast_code:
                m.add(self.fast_code[hz])
            mb_data[hz] = { 'm': m }
            count += 1

        async with aiofiles.open("./cizu.txt", mode="r") as f:
            cizu_data = await f.read()
        async with aiofiles.open("./corpus/words100000.txt", mode="r") as f:
            ma = re.findall(r"(\S{2,4})\s[a-z]+\s", await f.read())
            for i, cizu in enumerate(ma):
                if i >= 0:
                    break
                codes = list()
                ma = re.search(r"\s" + cizu + r"\s[0-9]+\s([a-z']+)", cizu_data)
                try:
                    py_list = ma.group(1).split("'")
                except:
                    # print(cizu)
                    continue
                for i, py in enumerate(py_list):
                    py_parsed = list()
                    py_parsed.append(py[0])
                    yunmu = ['a', 'o', 'e', 'i', 'u', 'v']
                    if py[0] in yunmu or py[0] in py_n or py[0] in py_m:
                        py_parsed.append(py[0:])
                    else:
                        if py[1] != "h":
                            py_parsed.append(py[1:])
                        else:
                            py_parsed.append(py[2:])
                    try:
                        co = await self.get_code(cizu[i], [py_parsed, ])
                        for c in co:
                            codes.append(c)
                    except:
                        print(f'{i} {cizu}')
                cizu_code = ""
                for i, hz in enumerate(cizu):
                    if i == 0:
                        cizu_code = codes[i]
                    elif i == 1:
                        # cizu_code = cizu_code[0:2] + codes[i][0] + codes[i][-1]
                        cizu_code = cizu_code[0:2] + codes[i][0:2]
                    elif i == 2:
                        cizu_code = cizu_code[0:3] + codes[i][0]
                    elif i == 3:
                        cizu_code = cizu_code[0] + cizu_code[2] + cizu_code[3] + codes[i][0]

                mb_data[cizu] = { 'm':  { cizu_code, } }

        # print(f'{mb_data}')
        mb_stats = dict()
        async with aiofiles.open(f"./mb.txt", mode="w") as f:
            for k, v in mb_data.items():
                ms = v['m']
                for m in ms:
                    if "⿰--" in m:
                        print(k)
                    if m in mb_stats:
                        mb_stats[m] += 1
                    else:
                        mb_stats[m] = 1
                    await f.write(f"{m} {k}\n")
        # mb_stats = dict()
        # async with aiofiles.open(f"./mb.txt", mode="w") as f:
        #     for k, v in mb_data.items():
        #         ms = v['m']
        #         for m1 in ms:
        #             if len(m1) >= 3:
        #                 m = m1[2]
        #             else:
        #                 continue
        #             if m == 'u':
        #                 print(k)
        #             if m in mb_stats:
        #                 mb_stats[m] += 1
        #             else:
        #                 mb_stats[m] = 1
        #             await f.write(f"{m} {k}\n")
        cp = 99454797
        async with aiofiles.open(f"./mb_rime.txt", mode="w") as f:
            for k, v in mb_data.items():
                ms = v['m']
                for m in ms:
                    await f.write(f"{k}\t{m}\n")
                    cp -= 1

        dup_code = 0
        for k, v in sorted(mb_stats.items(), key=lambda item: item[1]):
            if v > 1:
                dup_code += v
                hzs = list()
                for hz, vv in mb_data.items():
                    if k in vv['m']:
                        hzs.append(hz)
                print(f'{k}: {hzs}')
        print(dup_code)
        # print({k: v for k, v in sorted(mb_stats.items(), key=lambda item: item[1])})
        # print({k: v for k, v in sorted(ids_stats.items(), key=lambda item: item[1])})


gen_mb = GenMB()
asyncio.run(gen_mb.run())
