import re
import requests
from bs4 import BeautifulSoup as bs

raw_file = 'raw-high-scores.txt'
ehb_url = 'https://templeosrs.com/efficiency/pvm.php'

# example for no kills boss     'abyssal_sire': {'rank': '-1', 'kills': '-1'}
# example for normal boss       'alchemical_hydra': {'rank': '27632', 'kills': '496'}
# example for boss with '       "kree'arra": {'rank': '11282', 'kills': '399'}

var_delim = r'(\'|\")'  # necessary because osrs hiscores surrounds some bosses in ' and others (like kree'arra) with "

re_str = ''.join([r'\W', var_delim, r"([\w\'-]+)", var_delim, r": \{\'rank\': \'(-1|\d+)\', \'kills\': \'(-1|\d+)\'\}"])
re_pat = re.compile(re_str, re.I)


def read_high_scores(s: str):
    high_scores = re_pat.findall(s)
    high_scores_dict = {}

    for t in high_scores:
        boss_name = t[1].replace("\'", '')
        high_scores_dict[boss_name] = {}

        if t[3] == '-1' and t[4] == '-1':   # no registered kc gives -1 for rank and kills
            high_scores_dict[boss_name]['kills'] = 0
            continue

        high_scores_dict[boss_name] = {'rank': int(t[3]), 'kills': int(t[4])}

    return high_scores_dict


def read_ehb_rates(my_url: str):
    r = requests.get(my_url)
    soup = bs(r.text, 'html.parser')

    td_list = soup.find_all('td')
    ehb_dict = {}

    for i, td in enumerate(td_list):

        if td.img:                                              # td tags containing an img tag contain the boss name
            boss = td.img['title'].replace(' ', '_').lower()    # under the title attribute, the next td tag is the
            kills_per_hour = float(td_list[i+1].contents[0])    # kills/hr. We replace space with underscore and convert
            ehb_dict[boss] = kills_per_hour                     # to lowercase for consistency

    return ehb_dict


def main():

    with open(raw_file, mode='r') as f:

        for line in f:
            high_scores_dict = read_high_scores(line)
            ehb_dict = read_ehb_rates(ehb_url)

            for key, val in ehb_dict.items():

                try:
                    boss_dict = high_scores_dict[key]
                    boss_dict['ehb'] = boss_dict['kills'] / val

                except KeyError as E:
                    high_scores_dict[key] = {}

                except ZeroDivisionError as E:
                    boss_dict['ehb'] = 0


            for key, val in high_scores_dict.items():
                print(key, val)


if __name__ == '__main__':
    main()
