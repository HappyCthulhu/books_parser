import sys
from datetime import datetime

from loguru import logger
from openpyxl import load_workbook
import lxml.html
import requests
import re
from urllib3.exceptions import InsecureRequestWarning
from py_files.locators import LabirintLocators, BooksLocators

from py_files.some_functions import set_logger


def get_input_data(row_data):
    number = row_data[0].value
    isbn = row_data[1].value
    photo_link = row_data[2].value
    keeping = row_data[3].value
    lang = row_data[4].value
    barcode = row_data[5].value
    return number, isbn, photo_link, keeping, lang, barcode


def filing_empty_sheet(rows_count, sheet):
    rows_count += 1
    sheet = work_book[sheet]
    cell_range = sheet[f'A{ROWS_COUNT_NO_INFO}':f'F{ROWS_COUNT_NO_INFO}']
    data_list = [NUMBER, ISBN, PHOTO_LINK, KEEPING, LANG, BARCODE]

    x = 0
    for each_row in cell_range:
        for each_cell in each_row:
            text_in_cell = str(data_list[0])
            x += 1
            logger.debug(f'Текст ячейки: {text_in_cell}')
            logger.debug(f'Ячеек заполнено: {x}')
            each_cell.value = text_in_cell
            data_list.pop(0)
            work_book.save('Books_info.xlsx')
    return rows_count


def check_html_element_is_existing(element_list):
    if element_list:
        element_value = element_list[0]
    else:
        element_value = ''
    return element_value


def check_for_book_existing(isbn):
    search_book_by_ISBN_link = f'https://www.labirint.ru/search/{isbn}/?stype=0'
    html_text = requests.get(search_book_by_ISBN_link, verify=False).text
    tree = lxml.html.document_fromstring(html_text)
    book_href = tree.xpath('///a[@class="product-title-link"]/@href')
    if book_href:
        return True
    else:
        full_book_link = f'https://www.books.ru/search.php?s%5Btype_of_addon%5D=all&s%5Bquery%5D={isbn}&s%5Bgo%5D=1'
        book_page_response = requests.get(full_book_link).text
        book_page_tree = lxml.html.document_fromstring(book_page_response)
        filter_button = book_page_tree.xpath('//*[@id="button-filter"]')
        if filter_button:
            return False
    return True


def get_book_link(isbn):
    search_book_by_ISBN_link = f'https://www.labirint.ru/search/{isbn}/?stype=0'
    html_text = requests.get(search_book_by_ISBN_link, verify=False).text
    tree = lxml.html.document_fromstring(html_text)
    book_href = tree.xpath('///a[@class="product-title-link"]/@href')
    if book_href:
        store_locators = LabirintLocators
        book_href = book_href[0]
        full_book_link = 'https://www.labirint.ru' + book_href
    else:
        store_locators = BooksLocators
        full_book_link = f'https://www.books.ru/search.php?s%5Btype_of_addon%5D=all&s%5Bquery%5D={isbn}&s%5Bgo%5D=1'
        # book_page_response = requests.get(full_book_link).text
        # book_page_tree = lxml.html.document_fromstring(book_page_response)
        # filter_button = book_page_tree.xpath('//*[@id="button-filter"]')
    print(f'Ссылка: {full_book_link}')
    return store_locators, full_book_link


def get_years_sequence(start_year, stop_year):
    years_gap_list = []
    for i in range(start_year, stop_year):
        years_gap_list.append(str(i))
    return years_gap_list


def get_site_tree(link):
    html_text = requests.get(link, verify=False).text
    tree = lxml.html.document_fromstring(html_text)
    return tree


def checking_year_exist(tree):
    year_list = tree.xpath(site_locators.year_xpath)
    year = check_html_element_is_existing(year_list)
    if year:
        return True
    else:
        logger.critical('Года нет. Пишем в "Без информации"')
        return False


def define_witch_sheet(years, tree):
    year_list = tree.xpath(site_locators.year_xpath)
    year = check_html_element_is_existing(year_list)
    year = ''.join(re.findall(r'\d', year))
    print(f'Год выпуска: {year}')
    if year in years:
        print('Год входит')
        return 'Second-hand', year
    else:
        print('Год не включен')
        return 'Букинистика', year


def get_cover_from_labirint(link_book):
    book_id = link_book.split("/")[-2]

    design_link = f'https://www.labirint.ru/ajax/design/{book_id}/'

    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': link_book

    }

    response_for_cover_html = requests.get(design_link, headers=headers).text
    tree_cover = lxml.html.document_fromstring(response_for_cover_html)

    cover_text = tree_cover.xpath(LabirintLocators.cover_xpath)
    if cover_text:
        if 'твердая' in cover_text:
            cover = 'Твердая'
            return cover
        elif 'мягкая' in cover_text:
            cover = 'Мягкая'
            return cover
    else:
        cover = ''
        return cover


def get_data(tree):
    if site_locators == LabirintLocators:
        name_list = tree.xpath(site_locators.name_xpath)
        name = check_html_element_is_existing(name_list)
        if name:
            if ':' in name:
                name = re.findall(r': (.*)', name)[0]
        print(f'Название книги: {name}')

        no_price = tree.xpath(site_locators.no_price_xpath)
        if no_price:
            print('Цены нет')
            new_price = ''
            old_price = ''
        else:
            price_without_discount = tree.xpath(site_locators.price_without_discount_xpath)
            if price_without_discount:
                new_price = price_without_discount[0]
                print(f'Скидки нет. Цена: {new_price}')
                old_price = ''
            else:
                old_price = tree.xpath(site_locators.old_price_xpath)[0]
                new_price = tree.xpath(site_locators.new_price_xpath)[0]
                print(f'Цена без скидки: {old_price}')
                print(f'Цена со скидкой: {new_price}')

        orig_name = tree.xpath(site_locators.orig_name_xpath)
        if orig_name:
            orig_name = orig_name[0]
        else:
            orig_name = ''
        print(f'Оригинальное название: {orig_name}')

        editor_list = tree.xpath(site_locators.editor_xpath)
        editor = check_html_element_is_existing(editor_list)
        print(f'Редактор: {editor}')

        illustrator = ', '.join(tree.xpath(site_locators.illustrator_xpath))
        print(f'Иллюстратор: {illustrator}')


    elif site_locators == BooksLocators:
        name = tree.xpath(site_locators.name_xpath)[0]
        print(f'Название книги: {name}')

        editor = ''
        print(f'Редактор: {editor}')

        illustrator = ''
        print(f'Иллюстратор: {illustrator}')

        orig_name = ''
        print(f'Оригинальное название: {orig_name}')

        old_price = tree.xpath(site_locators.old_price_xpath)
        if not old_price:
            price_without_discount = tree.xpath(site_locators.price_without_discount_xpath)[0]
            new_price = price_without_discount
            new_price = ''.join(re.findall(r'\d', new_price))
            print(f'Скидки нет. Цена: {new_price}')
            old_price = ''
        else:
            old_price = tree.xpath(site_locators.old_price_xpath)[0]
            new_price = tree.xpath(site_locators.new_price_xpath)[0]
            new_price = ''.join(re.findall(r'\d', new_price))
            print(f'Цена без скидки: {old_price}')
            print(f'Цена со скидкой: {new_price}')

        cover = tree.xpath(BooksLocators.cover_xpath)

    weight_list = tree.xpath(site_locators.weight_xpath)
    weight = check_html_element_is_existing(weight_list)
    if weight:
        weight = ''.join(re.findall(r'\d', weight))
    print(f'Вес книги: {weight}')

    # dimension_text_list = tree.xpath()
    dimension_list = tree.xpath(site_locators.dimensions_xpath)
    dimensions = check_html_element_is_existing(dimension_list)
    if dimensions:
        if re.search(r'\d', dimensions):
            dimensions = re.split(r'\D', (''.join(re.sub(r' ', '', dimensions))))
            dimensions = list(filter(None, dimensions))
            # dimensions = (tree.xpath(site_locators.dimensions_xpath)[0]).split(' ')[1].split('x')
            if len(dimensions) == 1:
                width = dimensions[0]
                print(f'Ширина: {width}')
            elif len(dimensions) == 2:
                height = dimensions[0]
                width = dimensions[1]
                print(f'Высота: {height}')
                print(f'Ширина: {width}')
            elif len(dimensions) == 3:
                width = dimensions[2]
                height = dimensions[0]
                length = dimensions[1]
                print(f'Ширина: {width}')
                print(f'Высота: {height}')
                print(f'Длина: {length}')

        else:
            width = ''
            height = ''
            length = ''
            print(f'Ширина: {width}')
            print(f'Высота: {height}')
            print(f'Длина: {length}')

    else:
        width = ''
        height = ''
        length = ''
        print(f'Ширина: {width}')
        print(f'Высота: {height}')
        print(f'Длина: {length}')

    author_code = tree.xpath(site_locators.author_xpath)
    author = ''
    for elem in author_code:
        if re.search('[а-яА-Я]', elem):
            author += elem.strip()
            break
    print(f'Автор: {author}')

    # cover_from_xpath = tree.xpath('//div[@class="popup-middle"]/div/text()')[0]
    # if 'мягкая' in cover_from_xpath:
    #     cover = 'Мягкие переплет'
    # elif 'твердая' in cover_from_xpath:
    #     cover = 'Твердый переплет'
    # else:
    #     cover = 'Надо пометить ячейку красным'
    # print(f'Тип переплета: {cover}')

    # доделать
    annotation_list = tree.xpath(site_locators.annotation_xpath)
    annotation = check_html_element_is_existing(annotation_list)
    if annotation:
        annotation = ''.join(annotation)
    print(f'Аннотация: {annotation}')

    publisher_list = tree.xpath(site_locators.publisher_xpath)
    publisher = check_html_element_is_existing(publisher_list)
    print(f'Издательство: {publisher}')

    series = tree.xpath(site_locators.series_xpath)
    if not series:
        series = ''
    else:
        series = str(series[0])
    print(f'Серия: {series}')

    pages_list = tree.xpath(site_locators.pages_xpath)
    pages = check_html_element_is_existing(pages_list)
    if pages:
        pages = ''.join(re.findall(r'\d', pages))
    print(f'Количество страниц: {pages}')

    # data_list = [NUMBER, '', name, new_price, old_price, '', '', '', '', BARCODE, weight, width, height,
    #              length, PHOTO_LINK, '', '', '', '', ISBN, 'здесь будет жанр', '', author, '', COVER, '', '',
    #              '', annotation, publisher, '', YEAR, series, '', '', '', '', '', '', '', '', pages, '', '', '',
    #              'цветные иллюстрации', '', '',
    #              LANG, orig_name, '', '', KEEPING, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    #              '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    #              '', '', '', '', '', '', '', '', '', '', '', editor, '', '', illustrator]

    data_dict = {'number': NUMBER, 'name': name, 'new_price': new_price, 'old_price': old_price, 'barcode': BARCODE,
                 'weight': weight, 'width': width, 'height': height, 'length': length, 'photo_link': PHOTO_LINK,
                 'isbn': ISBN, 'genre': 'здесь будет жанр', 'author': author, 'cover': COVER, 'annotation': annotation,
                 'publisher': publisher, 'year': YEAR, 'series': series, 'pages': pages,
                 'colored_pics': 'цветные иллюстрации', 'lang': LANG, 'orig_name': orig_name, 'keeping': KEEPING,
                 'editor': editor, 'illustrator': illustrator}

    return data_dict
    # return data_list


def save_to_table(row_count, sheet, data_dict):
    sheet = work_book[sheet]
    sheet[f'A{row_count}'].value = data_dict['number']
    sheet[f'C{row_count}'].value = data_dict['name']
    sheet[f'D{row_count}'].value = data_dict['new_price']
    sheet[f'E{row_count}'].value = data_dict['old_price']
    sheet[f'J{row_count}'].value = data_dict['barcode']
    sheet[f'K{row_count}'].value = data_dict['weight']
    sheet[f'L{row_count}'].value = data_dict['width']
    sheet[f'M{row_count}'].value = data_dict['height']
    sheet[f'N{row_count}'].value = data_dict['length']
    sheet[f'O{row_count}'].value = data_dict['photo_link']
    sheet[f'T{row_count}'].value = data_dict['isbn']
    sheet[f'U{row_count}'].value = data_dict['genre']
    sheet[f'W{row_count}'].value = data_dict['author']
    sheet[f'Y{row_count}'].value = data_dict['cover']
    sheet[f'AA{row_count}'].value = data_dict['annotation']
    sheet[f'AD{row_count}'].value = data_dict['publisher']
    sheet[f'AF{row_count}'].value = data_dict['year']
    sheet[f'AG{row_count}'].value = data_dict['series']
    sheet[f'AL{row_count}'].value = data_dict['pages']
    sheet[f'AP{row_count}'].value = data_dict['colored_pics']
    sheet[f'AS{row_count}'].value = data_dict['lang']
    sheet[f'AT{row_count}'].value = data_dict['orig_name']
    sheet[f'AW{row_count}'].value = data_dict['keeping']
    sheet[f'CX{row_count}'].value = data_dict['editor']
    sheet[f'DA{row_count}'].value = data_dict['illustrator']
    work_book.save('Books_info.xlsx')


set_logger()
first_row_check = 1
COUNT = 0

COUNT_OF_BOOKS = 0

COUNT_LABIRINT_BOOKS = 0
COUNT_BOOKS_RU_BOOKS = 0

COUNT_ROW_BUKINISTICA_SHEET = 1
COUNT_ROW_SECOND_HAND_SHEET = 1
ROWS_COUNT_NO_INFO = 1


start_time = datetime.now()
requests.urllib3.disable_warnings(category=InsecureRequestWarning)

work_book = load_workbook('Books_info.xlsx')
sheet_ranges = work_book['Входные данные']
for row in sheet_ranges.rows:
    COUNT += 1
    if first_row_check == 1:
        first_row_check += 1
        continue
    COUNT_OF_BOOKS += 1
    NUMBER, ISBN, PHOTO_LINK, KEEPING, LANG, BARCODE = get_input_data(row)
    # ISBN = '978-5-9986-0119-4'
    # ISBN = '9785171212902'
    # ISBN = '978-5-17-117034-9'
    # ISBN = '978-5-389-07791-1'
    # ISBN = '978-5-9922-2592-1'
    # ISBN = '978-5-00117-631-2'
    # ISBN = '978-5-00117-631-2'
    if not check_for_book_existing(ISBN):
        ROWS_COUNT_NO_INFO = filing_empty_sheet(ROWS_COUNT_NO_INFO, 'Без информации')
        logger.info('Книги нет на сайтах')
        continue
    site_locators, book_link = get_book_link(ISBN)

    # if site_locators == LabirintLocators:
    #     COUNT_LABIRINT_BOOKS += 1
    #     COUNT = COUNT_ROW_LABIRINT_BOOKS
    # elif site_locators == BooksLocators:
    #     COUNT_BOOKS_RU_BOOKS +=1
    #     COUNT = COUNT_ROW_BOOKS_RU_BOOKS

    # site_locators = BooksLocators
    # book_link = f'https://www.books.ru/search.php?s%5Btype_of_addon%5D=all&s%5Bquery%5D={ISBN}&s%5Bgo%5D=1'
    TREE = get_site_tree(book_link)
    time_interval_list = get_years_sequence(2011, 2020)

    if not checking_year_exist(TREE):
        ROWS_COUNT_NO_INFO = filing_empty_sheet(ROWS_COUNT_NO_INFO, 'Без информации')
        logger.info('Книги нет на сайтах')
        continue
    sheet_name, YEAR = define_witch_sheet(time_interval_list, TREE)

    if sheet_name == 'Букинистика':
        COUNT_ROW_BUKINISTICA_SHEET += 1
        COUNT = COUNT_ROW_BUKINISTICA_SHEET
    elif sheet_name == 'Second-hand':
        COUNT_ROW_SECOND_HAND_SHEET += 1
        COUNT = COUNT_ROW_SECOND_HAND_SHEET

    COVER = get_cover_from_labirint(book_link)
    DATA_DICT = get_data(TREE)
    save_to_table(COUNT, sheet_name, DATA_DICT)
    end_time = datetime.now()
    wasted_time = end_time - start_time
    logger.debug(f'Потребовалось секунд: {wasted_time}')
    if site_locators == LabirintLocators:
        logger.debug(f'Лабиринт')
    else:
        logger.debug(f'Books.ru')
    logger.info(f'Книг обработано: {COUNT_OF_BOOKS}')
