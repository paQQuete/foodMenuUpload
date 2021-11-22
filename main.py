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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listMenus = self._getListMenus()

    def _getListMenus(self):
        '''
        :return: tuple (ResultSet for 1-4 classes, ResultSet for 5-11 classes)
        '''
        q = self.find('div', id='forsoup14')
        q = q.find_all('a')
        q2 = self.find('div', id='forsoup511')
        q2 = q2.find_all('a')
        return q, q2



class Menus():
    def __init__(self):
        '''
        формируем список файлов в директории вызова данного файла;
        нужно расширить под изменяемую директорию
        '''
        self._listfiles = [file if os.path.isfile(os.path.join('.', file)) else False for file in os.listdir('.')]
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

        return outlist

    # def filesfunc(path):
    #     for file in os.listdir(path):
    #         if os.path.isfile(os.path.join(path, file)):
    #             yield file

class NewTagsToSoupMixin():
    def newA(self):
        self.listMenus
        pass



if __name__ == '__main__':
    html = requests.get('http://school17vo.narod.ru/food')
    html = html.text
    parser = 'lxml'

    soup = MySoup(html, 'html.parser')

    mix = MyMixin()

    # for root, dirs, files in os.walk('.'):
    #     print(files)


    # for file in files("."):
    #     print(file)

    print(Menus().parser())