#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import random
import argparse
import sys

parser = argparse.ArgumentParser(description='Введи аргументы')
# обязательные аргументы
parser.add_argument('length', type=int, help='длина генерируемой последовательности')
# необязательные аргументы
parser.add_argument('--input_dir', type=str, help='путь к директории, в которой лежит коллекция документов', default='')
parser.add_argument('--prefix', type=str, help='начало предложения', default='')
# parser.add_argument('--model', type=str, help='путь к файлу, в который сохраняется модель') не успел реализовать
args = parser.parse_args()
if args.input_dir == '':
    # если имя файла с данными нет, вводим через stdin
    args.input_dir = 'file.txt'
    f = open('file.txt', 'w+', encoding='utf-8')
    for line in sys.stdin:
        if '' == line.rstrip():
            break
        f.write(line)
    f.close()


class Trigram:
    def __init__(self, path, n, prefix=''):
        self.path = path
        self.n = n
        self.prefix = prefix

    def trigrams(self):
        # тут я открываю txt файл и формирую триграммы
        ff = open(self.path, 'r+', encoding='utf-8')
        text = ff.read()

        text = re.sub(r'[^а-я0-9]', ' ', text.lower())
        tokens = [token for token in text.split(" ") if token != ""]

        for i in range(0, len(tokens) - 2):
            yield tokens[i], tokens[i + 1], tokens[i + 2]

    def fit(self):
        # тут я тренирую модель
        trigrams = self.trigrams()

        bi, tri = dict(), dict()

        for w0, w1, w2 in trigrams:
            # тут обязательно делаем проверку на наличие би/триграммы в словаре
            if (w0, w1) in bi:
                bi[w0, w1] += 1.0
            else:
                bi[w0, w1] = 1.0
            if (w0, w1, w2) in tri:
                tri[w0, w1, w2] += 1.0
            else:
                tri[w0, w1, w2] = 1.0

        model = {}
        # создаем словарь, и для каждой биграммы собираем следущее слово и его вероятность
        # вероятность считаем так: количество триграммы в тексте / колечество биграммы в тексте
        # P(раму|мама мыла) = C(мама мыла раму)/С(мама мыла)
        for (w0, w1, w2), chance in tri.items():
            if (w0, w1) in model:
                model[w0, w1].append((w2, chance / bi[w0, w1]))
            else:
                model[w0, w1] = [(w2, chance / bi[w0, w1])]
        return model

    def generate(self):
        phrase = []
        model = self.fit()
        if self.prefix == '':
            # если префикс пустой - выбираем любую биграмму радомно
            prefix, next_word = random.choice(list(model.items()))
            phrase.append(prefix[0])
            phrase.append(prefix[1])
        else:
            rand_list = []
            prefix = self.prefix.lower().split()
            if len(prefix) == 1:
                # если префикс это одно слово, ищем в модели биграммы, где встречается это слово.
                # Если их много, выбираем одну из них рандомно
                phrase.append(prefix[0])
                for i in model.keys():
                    if i[0] == prefix[0]:
                        rand_list.append(i[1])
                if len(rand_list) == 0:
                    # если слово вообще не встретилось в нашем тексте, выбираем следщие два слова.
                    prefix, next_word = random.choice(list(model.items()))
                    phrase.append(prefix[0])
                    phrase.append(prefix[1])
                else:
                    phrase.append(random.choice(rand_list))
            else:
                # если в префиксе больше одного слова,
                # продолжаем последовательность, основываясь на последних двух словах
                for i in prefix:
                    phrase.append(i)
                if (prefix[-2], prefix[-1]) not in model:
                    for i in model.keys():
                        if i[0] == prefix[-1]:
                            rand_list.append(i[1])
                    if len(rand_list) == 0:
                        prefix, next_word = random.choice(list(model.items()))
                        phrase.append(prefix[0])
                        phrase.append(prefix[1])
                    else:
                        phrase.append(random.choice(rand_list))
        self.n -= len(phrase)
        for i in range(self.n):
            phrase.append(random.choice(model[phrase[-2], phrase[-1]])[0])
        return ' '.join(phrase)


if __name__ == '__main__':
    Model = Trigram(args.input_dir, args.length, args.prefix)
    print(Model.generate())
