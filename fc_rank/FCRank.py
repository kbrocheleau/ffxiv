#!./venv/bin/python3
from lxml import html
import requests
#import matplotlib.pyplot as plt
import yaml

ROOT_URL = 'http://na.finalfantasyxiv.com'
ORDERED_CLASS_NAMES = ''


class FreeCompany:
    def __init__(self, url=None):
        self.name = ''
        self.members = []
        if url is not None:
            self.build(url)

    def add_member(self, character):
        self.members.append(character)

    def build(self, url):
        fc_tree = html.fromstring(requests.get(ROOT_URL + url).content)
        self.name = str(fc_tree.xpath('//p[@class="entry__freecompany__name"]/text()')[0])
        print('Building FC {}'.format(self.name))

        fc_members_tree = fc_tree.xpath('//li[@class="entry"]')
        members_urls = []
        for member in fc_members_tree:
            for element in member:
                members_urls.append((element.attrib['href']))

        for member_url in members_urls:
            self.members.append(Character(member_url))
            print('Found {}'.format(self.members[-1].name))


class Character:
    def __init__(self, url=None):
        self.name = ''
        self.race = ''
        self.clan = ''
        self.gender = ''
        self.nameday = ''
        self.guardian = ''
        self.city_State = ''
        self.game_classes = {}
        if url is not None:
            self.build_character(url)

    def build_character(self, url):
        page = requests.get(ROOT_URL + url)
        tree = html.fromstring(page.content)
        self.name = str(tree.xpath('//p[@class="frame__chara__name"]/text()')[0])

        levels = tree.xpath('//div[@class="character__job__level"]/text()')
        exps = tree.xpath('//div[@class="character__job__exp"]/text()')

        for name, level, exp in zip(ORDERED_CLASS_NAMES, levels, exps):
            current_class = GameClass()
            if level != '-':
                current_class.level = int(level)
                if current_class.level != 70:
                    [current_class.exp_earned, current_class.exp_total] = [int(s) for s in exp.split() if s.isdigit()]
            else:
                pass

            self.game_classes[name] = current_class


class GameClass:
    def __init__(self, level=0, exp_earned=0, exp_total=0):
        self.exp_earned = exp_earned
        self.exp_total = exp_total
        self.level = level


def main():
    with open('config.yaml', 'r') as stream:
        config = yaml.safe_load(stream)

    log = open(config['LOG_FILENAME'], 'w')
    game_class_abbreviations = config['ORDERED_CLASS_ABBR']
    game_classs_names = config['ORDERED_CLASS_NAMES']
    exp_totals_sb = config['LEVEL_EXP_SB']
    exp_totals_hw = config['LEVEL_EXP_HW']
    exp_totals_arr = config['LEVEL_EXP_ARR']
    global ORDERED_CLASS_NAMES
    ORDERED_CLASS_NAMES = config['ORDERED_CLASS_NAMES']

    rows = []
    columns = []
    data = []

    try:
        fc = FreeCompany(config['FC_URL'])
    except IndexError:
        print('Unable to build FC. Likely the Lodestone is down.')
        return

    log.write('{:18}'.format(' '))

    for name in game_class_abbreviations:
        log.write('\t{}'.format(name))
        columns.append(name)
    log.write('\n')

    for member in fc.members:
        character_data = []

        log.write('{:18}'.format(member.name))
        rows.append(member.name)

        for name in game_classs_names:
            log.write('\t{:02d}'.format(member.game_classes[name].level))
            character_data.append(member.game_classes[name].level)
        data.append(character_data)
        log.write('\n')

    # char = Character()
    # char.build_character('/lodestone/character/17689120/')
    # print('Found {}'.format(char.name))
    # for level in char.levels:
    #     log.write('{:02d}\t'.format(level))
    # log.write('\n')
    # pass

    log.close()
    # stream = open('fc_levels.yaml', 'w')
    # yaml.dump(fc, stream)

    colors = []

    for row in data:
        colors_row = []
        for datum in row:
            if datum > 60:
                color_value = (exp_totals_sb[datum - 61] - exp_totals_hw[-1]) / (exp_totals_sb[-1] - exp_totals_hw[-1])
                colors_row.append((color_value, 1-color_value, 0, 0.5))
            elif datum > 50:
                color_value = (exp_totals_hw[datum-51]-exp_totals_arr[-1])/(exp_totals_hw[-1]-exp_totals_arr[-1])
                colors_row.append((0, color_value, 1-color_value, 0.5))
            else:
                color_value = exp_totals_arr[datum]/exp_totals_arr[-1]
                colors_row.append((1-color_value, 1-color_value, 1, 0.5))
        colors.append(colors_row)
"""
    fig, axs = plt.subplots(1, 1)
    axs.axis('tight')
    axs.axis('off')
    axs.table(cellText=data, cellColours=colors, colLabels=columns, rowLabels=rows, loc='center')
    plt.tight_layout()
    #plt.savefig('fc_rosenrot_levels.png')
    #plt.show()
"""

if __name__ == "__main__":
    main()
