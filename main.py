from bs4 import BeautifulSoup
import requests
# import ftplib
import html.parser
import os

class mySoup(BeautifulSoup):
    def getListMenus(self):
        q = self.find('div', id='forsoup14')
        q = q.find_all('a')
        q2 = self.find('div', id='forsoup511')
        q2 = q2.find_all('a')
        return q, q2

class Menus():
    def __init__(self):
        self._listfiles = [file if os.path.isfile(os.path.join('.', file)) else False for file in os.listdir('.')]

    def parser(self):
        outlist = list()
        for file in self._listfiles:
            if file == False:
                continue


            year = file[0:4]
            month = file[5:7]
            day = file[8:10]

            if 'sm' in file:
                graduation = 'sm'
            else:
                graduation = False

            dateInViewFormat = f'{day}.{month}.{year}'
            outlist.append({"dateM": dateInViewFormat, "sm": graduation, "filename": file})

        return outlist

    def filesfunc(path):
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                yield file

class MyMixin(mySoup, Menus):
    def makeMySoup(self):
        



if __name__ == '__main__':
    html = requests.get('http://school17vo.narod.ru/food')
    html = html.text
    parser = 'html.parser'

    # soup = mySoup(html, 'html.parser')
    # print(soup.getListMenus())

    # for root, dirs, files in os.walk('.'):
    #     print(files)


    # for file in files("."):
    #     print(file)

    print(Menus().parser())