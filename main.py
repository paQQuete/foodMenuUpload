from bs4 import BeautifulSoup
import requests
# import ftplib
import html.parser
import os


class MySoup(BeautifulSoup):
    '''
    Создаём класс от bs4, метод класса вернёт ResultSet (формат данных bs4);
    экземпляр этого класса можно расширить новыми html тегами
    при вызове конструктора формируется ResultSet listMenus
    '''

    def __init__(self, url, menusList, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._listMenus = self._getListMenus()
        self._url = url
        self._menusList = menusList

    def _getListMenus(self):
        '''
        :return: tuple (ResultSet for 1-4 classes, ResultSet for 5-11 classes)
        '''
        q = self.find('div', id='forsoup14')
        q = q.find_all('a')
        q2 = self.find('div', id='forsoup511')
        q2 = q2.find_all('a')
        return [q, q2]

    def _makeNewTag(self, i, graduation):
        '''
        make new Tag (object of BS4) <a> with link and text for this link
        '''
        try:
            newTag = self.new_tag('a', href=f'''{self._url}'/'{self._menusList.filesMenus[graduation][i]['filename']}''')
        except IndexError:
            print('Скорее всего в папке отсутствуют файлы с шаблонным именем')
            raise IndexError
        classesText = str()
        if self._menusList.filesMenus[graduation][i]['sm'] == 'sm':
            classesText = '1-4'
        elif self._menusList.filesMenus[graduation][i]['sm'] == False:
            classesText = '5-11'
        newTag.string = f'''Ежедневное меню для учащихся {classesText} классов ({self._menusList.filesMenus[graduation][i]['date']})'''
        return newTag

    def appendResultSet(self):
        '''
        change _listMenus in instance of this object
        just expand ResultSets
        '''
        graduation = str()
        for i in (0, len(self._listMenus)):
            if i == 0:
                graduation = 'sm'
            elif i == 1:
                graduation = 'not sm'
            for j in range(0, len(self._listMenus[i])):
                self._listMenus[i].append(self._makeNewTag(j, graduation))
                # поправить этот цикл, должен итерироваться столько раз, сколько НОВЫХ файлов. А сейчас итерируется по кол-ву СТАРЫХ файлов (то есть тех файлов, которые уже размещены на странице)
                self._listMenus[i].append(self.new_tag('br'))

    def getter(self):
        return self._listMenus


class Menus():
    def __init__(self, directory):
        '''
        формируем список файлов в директории вызова данного файла;
        нужно расширить под изменяемую директорию
        '''
        self._listfiles = [file if os.path.isfile(os.path.join(directory, file)) else False for file in
                           os.listdir(directory)]
        self.filesMenus = self.parser()

    def parser(self):
        '''
        парсит только фалйы, названные по жёсткому шаблону. расширение не проверяет
        :return: список со словарями в каждом элементе списка
        date = дата в удобночитаемом формате для записи на html страницу
        sm = False, если старшие классы (5-11), 'sm' если 1-4 классы
        filename = имя файла для записи в <a href=''>, НЕ ЗАБЫВАТЬ ДОПИСЫВАТЬ ПУТЬ К ПАПКЕ НА САЙТЕ
        '''
        outlist = list()
        outdict = {'sm': list(), 'not sm': list()}
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
            outlist.append({"date": dateInViewFormat, "sm": graduation, "filename": file})

        for eachDict in outlist:
            if eachDict['sm'] == 'sm':
                outdict['sm'].append(eachDict)
            elif eachDict['sm'] == False:
                outdict['not sm'].append(eachDict)

        return outdict

    # def filesfunc(path):
    #     for file in os.listdir(path):
    #         if os.path.isfile(os.path.join(path, file)):
    #             yield file


class NewTagsToSoupMixin():
    def newA(self):
        self.listMenus
        pass


if __name__ == '__main__':
    url = 'http://school17vo.narod.ru/food'
    html = requests.get(url)
    html = html.text
    parser = 'lxml'
    directory = '.'

    listDictFiles = Menus(directory)

    soup = MySoup(url, listDictFiles, html, parser)
    soup.appendResultSet()
    print(soup.getter())