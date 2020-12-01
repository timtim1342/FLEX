import re

def o():
    with open('glosses.csv', 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def lit():
    text = o()
    lt = text.split('\n')
    for i in range(len(lt)):
        lt[i] = lt[i].split(',')
    return lt

def morphs_dict():
    lt = lit()
    dt = {}  # словарь это плохой формат. и глосса и морф могут повторяться

    for i in range(len(lt)):
        if len(lt[i]) == 1:  # проверка на пустую строку
            continue
        p, l, m, g = lt[i]

        m = re.sub('=\w*', '', m)  # чистит от проклитик
        g = re.sub('=\w*','', g)

        if len(m.split('-')) != len(g.split('-')):  # проверка на зеркальное соотвествие глосс морфу
            continue

        if "'" in m:  # переделать, должно как-то отключатся при чтении данных
            m = m.replace("''", "+").replace(m[0], '').replace(m[-1], '').replace('+', "'")

        if re.findall('^([\dA-Z]+-)[\w][a-z]+', g) != []:  # в слове есть префикс. исходит, что один
            affg = re.findall('^([\dA-Z]+)-[\d\w][\.a-z]+', g)[0]
            affm = re.findall('^[\w\']+-', m)[0]
            m = re.sub(affm, '', m, count=1)  # дальше остаются слова без префиксов
            g = re.sub(affg + '-', '', g, count=1)
            dt[affm] = ['pre', affg]



        m, g = m.split('-'), g.split('-')

        for i in range(len(m)):  # пилит на префиксы, корни, постфиксы

            if g[i].islower() and g[i].isalpha():  # корень
                if m[i] in dt.keys() and g[i] not in dt[m[i]][1]:
                    new = dt[m[i]][1] + ';' + g[i]
                    dt[m[i]] =['root', new, dt[m[i]][2], dt[m[i]][3] + 1]  # эм тут косяк, кажется.
                elif m[i] not in dt.keys():
                    dt[m[i]] = ['root', g[i], p, 1]
                else:  # эти элсы нужны только для подсчета морфем
                    dt[m[i]] = ['root', dt[m[i]][1], dt[m[i]][2], dt[m[i]][3] + 1]

            elif g[i].isupper():  # аффикс
                if '-' + m[i] in dt.keys() and g[i] not in dt['-' + m[i]][1]:
                    new = dt['-' + m[i]][1] + ';' + g[i]
                    dt['-' + m[i]] =['post', new, dt['-' + m[i]][2] + 1]
                elif '-' + m[i] not in dt.keys():
                    dt['-' + m[i]] = ['post', g[i], 1]
                else:
                    dt['-' + m[i]] = ['post', dt['-' + m[i]][1], dt['-' + m[i]][2] + 1]

            else:  # микс потом надо разбить. иногда меняет их глоссу на .
                if m[i] in dt.keys() and g[i] not in dt[m[i]][1]:
                    new = dt[m[i]][1] + ';' + g[i]
                    dt[m[i]] = ['mix', new, dt[m[i]][2], dt[m[i]][3] + 1]
                elif m[i] not in dt.keys():
                    dt[m[i]] = ['mix', g[i], p, 1]
                else:
                    dt[m[i]] = ['mix', dt[m[i]][1], dt[m[i]][2], dt[m[i]][3] + 1]

    return dt

def morph_dict_go_out():  # чтобы выводить словарь для ручного редактирования. эта и след функции надстройка для ввода и вывода словаря для ручной чистки. лучше оформить отдельно
    dt = morphs_dict()
    with open('morphs.csv', 'w', encoding='utf-8') as f:
        pass
    for key in dt.keys():
        if dt[key][0] == 'root':
            s = key + '\t' + dt[key][2] + '\t' + dt[key][1] + '\t' + str(dt[key][3]) + '\n'
        elif dt[key][0] == 'post':
            s = key + '\t' + '\t' + dt[key][1] + '\t' + str(dt[key][2]) + '\n'
        elif dt[key][0] == 'mix':  # есть превербы еще
            s = key + '\t' + dt[key][2] + '\t' + dt[key][1] + '\t' + str(dt[key][3]) + '\n'
        with open('morphs.csv', 'a', encoding='utf-8') as f:
            f.write(s)

def morph_dict_back():  # тип добавлен руками, нет микса лучше переделать
    dt = {}  # опять же. плохой формат часть форм теряет
    with open('morphs_cleaned.csv', 'r', encoding='utf-8') as f:
        txt = f.read().split('\n')
    for s in txt[:len(txt)-1]:  # убирает последний \н
        type, key, pos, gloss = s.split('\t')
        if "'" in key:  # переделать, должно как-то отключатся при чтении данных
            key = key.replace("''", "+").replace(key[0], '').replace(key[-1], '').replace('+', "'")
        dt[key] = [type, gloss, pos]  # для постф чр будет \т
    return dt



def db_gener(dt):
    m()
    for key in dt.keys():
        if dt[key][0] == 'root':
            s = root(key, dt[key][2], dt[key][1])
            w(s)
        elif dt[key][0] != 'mix':
            s = aff(key, dt[key][1])
            w(s)


def m():  # создает шаблон БД
    with open('lexicon.db', 'w', encoding='utf-8') as f:
        f.write('\n')

def w(s):  # вписывает строчку в БД
    with open('lexicon.db', 'a', encoding='utf-8') as f:
        f.write(s)

def root(lx, ps, g):  # создаает строчку для корня. лемму еще надо деть куда-то
    s = '\n\\lx %s\n\\lx_Rut %s\n\\sn 1\n\\ps_Eng %s\n\\g_Eng %s\n\\dt 30/Jan/2020\n' % (lx, lx, ps, g)
    return s

def aff(lx, g):  # для аффикса. клитики тоже аффиксы(
    s = '\n\\lx %s\n\\lx_Rut %s\n\\sn 1\n\\g_Eng %s\n\\dt 30/Jan/2020\n' % (lx, lx, g)
    return s

def main():
    # dt = morphs_dict()
    dt = morph_dict_back()  # это если руками править. предыд, если нет
    db_gener(dt)


if __name__ == '__main__':
    main()