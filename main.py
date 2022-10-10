from bs4 import BeautifulSoup, NavigableString
import requests
import datetime
from ftplib import FTP
import os
import cred

DEBUG = False
url = 'http://school17vo.narod.ru/food'
urla = '/food'

'''
данные для подключения по ftp в cred.py в переменных, 
тип данных строка - ftphost, ftplogin, ftppass (если нет - создать)


'''


class MySoup(BeautifulSoup):
    '''
    Создаём класс от bs4, конструктор формирует список из двух ResultSet с тегами со указанной страницы.
    В коструктор обязательно нужно передавать url и экземпеляр класса Menus 1 и 2 аргументом
    (перед аргументами родителя)
    испрввление экземпляра вызовом методом makeOutput извне, после можно записывать в выходной файл
    '''

    def __init__(self, pageurl, urla, menusList, listFTPFiles, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._listPageMenus = self._getListMenus()
        self._existingMenusOnSite = self._getAlreadyExistMenu()
        self._url = pageurl
        self._urla = urla
        self._menusList = menusList
        self._ftpfiles = listFTPFiles
        self.actionForMenus = self._makeActionsForMenus()

    def _getListMenus(self):
        '''
        :return: tuple (ResultSet for 1-4 classes, ResultSet for 5-11 classes)
        '''
        q = self.find('div', id='forsoup14')
        q = q.find_all('a')
        q2 = self.find('div', id='forsoup511')
        q2 = q2.find_all('a')
        return [q, q2]

    def _getAlreadyExistMenu(self) -> list:
        # q2[00].attrs['href']
        outputLIst = list()

        for eachResultSet in self._listPageMenus:
            for eachTag in eachResultSet:
                href = eachTag.attrs['href']
                filenameInHref = href[href.rindex('/') + 1:]
                outputLIst.append(filenameInHref)

        return outputLIst

    def _makeActionsForMenus(self) -> dict:
        d = dict()
        for menu in self._menusList.listXlsFiles:
            if menu in self._ftpfiles and menu not in self._existingMenusOnSite:
                d.update({menu: 'just make tag'})
            elif menu not in self._ftpfiles and menu in self._existingMenusOnSite:
                d.update({menu: 'just upload'})
            elif menu in self._ftpfiles and menu in self._existingMenusOnSite:
                d.update({menu: 'ignore menu'})
            elif menu not in self._ftpfiles and menu not in self._existingMenusOnSite:
                d.update({menu: 'default action'})

        return d

    def _makeNewTag(self, i, graduation):
        '''
        make new Tag (object of BS4) <a> with link and text for this link
        '''
        try:
            newTag = self.new_tag('a', href=f'''{self._urla}/{self._menusList.filesMenus[graduation][i]['filename']}''')
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
        change _listPageMenus in instance of this object
        just expand ResultSets
        '''

        graduation = str()
        for i in range(0, len(self._listPageMenus)):
            if i == 0:
                graduation = 'sm'
            elif i == 1:
                graduation = 'not sm'

            for j in range(0, len(self._menusList.filesMenus[graduation])):

                if self.actionForMenus[self._menusList.filesMenus[graduation][j]['filename']] == 'default action':
                    self._listPageMenus[i].append(self._makeNewTag(j, graduation))

    def _replaceContentsAllInONeFunc(self):
        i = 0

        for eachResultSet in self._listPageMenus:
            if i == 0:
                outputList = list()

                for eachTag in eachResultSet:
                    outputList.append(eachTag)
                    outputList.append(self.new_tag('br'))
                    outputList.append(NavigableString('\n'))
                self.find('div', id='forsoup14').contents = outputList

            elif i == 1:
                outputList = list()
                for eachTag in eachResultSet:
                    outputList.append(eachTag)
                    outputList.append(self.new_tag('br'))
                    outputList.append(NavigableString('\n'))
                self.find('div', id='forsoup511').contents = outputList
            i += 1

    def makeOutput(self):

        self.appendResultSet()
        self._replaceContentsAllInONeFunc()


class Menus():

    def __init__(self, directory):
        '''
        формируем список файлов xls/xlsx в директории вызова данного файла;
        *нужно расширить под изменяемую директорию
        '''
        self._listfiles = [file if os.path.isfile(os.path.join(directory, file)) else False for file in
                           os.listdir(directory)]
        self.filesMenus = self.parser()
        self.listXlsFiles = self._listValidFiles()

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
            if file == False or self._checkXls(file) == False:
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

    def _checkXls(self, filename) -> bool:
        if filename:

            if filename[filename.rindex('.') + 1:] == 'xls' or filename[filename.rindex('.') + 1:] == 'xlsx':
                return True
            else:
                return False
        else:
            return False

    def _listValidFiles(self):
        tmpList = [file if self._checkXls(file) else False for file in self._listfiles]
        outlist = list()
        for file in tmpList:
            if file:
                outlist.append(file)

        return outlist


class MyFTP(FTP):
    def __init__(self, *args, **kwargs):
        super(MyFTP, self).__init__(*args, **kwargs)
        self._navigation()

    def _navigation(self):
        self.cwd('food')

    def upload(self, path):
        with open(path, 'rb') as fobj:
            self.storbinary('STOR ' + path, fobj, 1024)

    def dirfiles(self) -> list:
        '''
        list with names of active directory files
        '''
        return self.nlst()


if __name__ == '__main__':
    if DEBUG == True:
        print('DEBUG True')

    html = requests.get(url)
    html = html.text
    parser = 'lxml'
    directory = '.'
    backupfile = f'backup_index_{datetime.datetime.now().day}-{datetime.datetime.now().month}-{datetime.datetime.now().year}.html'
    listOfIgnores = list()
    finalListFiles = list()

    listDictFiles = Menus(directory)
    listDirectoryXlsFiles = listDictFiles.listXlsFiles

    # build instance, login, and move to /food
    ftp = MyFTP(cred.ftphost, cred.ftplogin, cred.ftppass)
    listFTPDirectoryFiles = ftp.dirfiles()

    soup = MySoup(url, urla, listDictFiles, listFTPDirectoryFiles, html, parser)

    soup.makeOutput()
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))

    templistFiles = listDictFiles.listXlsFiles
    for file in templistFiles:
        if soup.actionForMenus[file] == 'ignore menu':
            listOfIgnores.append(templistFiles[templistFiles.index(file)])
        else:
            finalListFiles.append(templistFiles[templistFiles.index(file)])

    finalListFiles.append('index.html')

    if DEBUG == False:  # upload files!

        with open(backupfile, 'wb') as file:
            ftp.retrbinary('RETR ' + 'index.html', file.write)

        # make list of upload files

        # upload each file
        for file in finalListFiles:
            ftp.upload(file)

        print('Загружено на сервер:', finalListFiles)
        print()
        print('Не загружено, дубли:', listOfIgnores)
