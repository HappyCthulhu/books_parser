from datetime import datetime

from loguru import logger
from openpyxl import load_workbook
import lxml.html
import requests
import re

from openpyxl.styles import PatternFill
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

    if not keeping:
        keeping = 'Отличная'
    elif keeping == 1:
        keeping = 'Хорошая'
    else:
        logger.critical(f'Что-то не так с сохранностью. Значение keeping: {keeping}')

    if not lang:
        lang = 'Русский'
    elif lang == 1:
        lang = 'Английский'
    else:
        logger.critical(f'Что-то не так с языком. Значение lang: {lang}')

    return number, isbn, photo_link, keeping, lang, barcode


def filing_empty_sheet(rows_count, sheet):
    rows_count += 1
    sheet = work_book[sheet]
    cell_range = sheet[f'A{rows_count}':f'F{rows_count}']
    data_list = [NUMBER, ISBN, PHOTO_LINK, KEEPING, LANG, BARCODE]

    for each_row in cell_range:
        for each_cell in each_row:
            text_in_cell = str(data_list[0])
            each_cell.value = text_in_cell
            data_list.pop(0)
    work_book.save('Books_info.xlsx')
    return rows_count


def check_html_element_existing(element_list):
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
    return store_locators, full_book_link


def get_data_from_genres_file(genres_file_name):
    genres_file = load_workbook(genres_file_name)
    sheet_genres = genres_file['Лист1']

    count = 0
    genres_dict = {}
    for cell in sheet_genres['B']:
        count += 1
        if cell.value:
            genres_dict[cell.value] = sheet_genres[f'C{count}'].value
        else:
            break

    return genres_dict


def get_years_sequence(start_year, stop_year):
    years_gap_list = []
    for i in range(start_year, stop_year):
        years_gap_list.append(str(i))
    return years_gap_list


def get_site_tree(link):
    html_text = requests.get(link, verify=False).text
    tree = lxml.html.document_fromstring(html_text)
    return tree


def define_which_sheet(years, tree):
    year_list = tree.xpath(site_locators.year_xpath)

    if year_list:
        year = check_html_element_existing(year_list)
        year = ''.join(re.findall(r'\d', year))

        if year in years:
            return 'Second-hand', year

        else:
            return 'Букинистика', year

    else:
        year = ''
        return 'Без года', year


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
    cover_text = check_html_element_existing(cover_text)

    if 'твердая' in cover_text:
        cover = 'Твердый переплет'
    elif 'мягкий' in cover_text:
        cover = 'Мягкая обложка'
    else:
        cover = ''

    design_list = tree_cover.xpath(LabirintLocators.colored_pics_xpath)
    design_text = ''.join(design_list)

    if design_text:
        if 'Цветные' in design_text:
            colored_pics = 'Да'
        else:
            colored_pics = ''
    else:
        colored_pics = ''

    return cover, colored_pics


def get_data(tree):
    if site_locators == LabirintLocators:

        circulation = ''

        name_list = tree.xpath(site_locators.name_xpath)
        name = check_html_element_existing(name_list)
        if name:
            if ':' in name:
                name = re.findall(r': (.*)', name)[0]

        logger.debug(f'Книга "{name}": {book_link}')

        cover, colored_pics = get_cover_from_labirint(book_link)

        genres_from_html = tree.xpath(LabirintLocators.genres_xpath)
        if genres_from_html:
            genres_from_html.reverse()
            for elem in genres_from_html:
                if elem in GENRES_LIST.keys():
                    genre = GENRES_LIST[elem]
                    break
                else:
                    genre = ''
        else:
            genre = ''

        annotation = tree.xpath(site_locators.annotation_xpath)
        if annotation:
            annotation = ''.join(annotation)
        else:
            annotation = ''

        no_price = tree.xpath(site_locators.no_price_xpath)
        if no_price:

            new_price = ''
            old_price = ''
        else:
            price_without_discount = tree.xpath(site_locators.price_without_discount_xpath)
            if price_without_discount:
                new_price = price_without_discount[0]

                old_price = ''
            else:
                old_price = tree.xpath(site_locators.old_price_xpath)[0]
                new_price = tree.xpath(site_locators.new_price_xpath)[0]

        orig_name_list = tree.xpath(site_locators.orig_name_xpath)
        orig_name = check_html_element_existing(orig_name_list)

        editor_list = tree.xpath(site_locators.editor_xpath)
        editor = check_html_element_existing(editor_list)

        illustrator_list = tree.xpath(site_locators.illustrator_xpath)
        illustrator = check_html_element_existing(illustrator_list)
        if illustrator:
            illustrator = ', '.join(illustrator_list)


    elif site_locators == BooksLocators:
        name = tree.xpath(site_locators.name_xpath)[0]

        logger.debug(f'Книга "{name}": {book_link}')

        editor = ''

        illustrator = ''

        orig_name = ''

        full_annotation = tree.xpath(site_locators.full_annotation_xpath)
        if full_annotation:
            annotation = ''.join(full_annotation)
        else:
            short_annotation = tree.xpath(site_locators.short_annotation_xpath)
            annotation = check_html_element_existing(short_annotation)

        colored_pics = ''

        circulations_list = tree.xpath(site_locators.circulation)
        circulation = check_html_element_existing(circulations_list)
        if circulation:
            circulation = ''.join(re.findall(r'\d', circulation))

        genre_list = tree.xpath(BooksLocators.genre_xpath)
        genre = check_html_element_existing(genre_list)

        old_price = tree.xpath(site_locators.old_price_xpath)
        if not old_price:
            price_without_discount = tree.xpath(site_locators.price_without_discount_xpath)[0]
            new_price = price_without_discount
            new_price = ''.join(re.findall(r'\d', new_price))

            old_price = ''
        else:
            old_price = tree.xpath(site_locators.old_price_xpath)[0]
            new_price = tree.xpath(site_locators.new_price_xpath)[0]
            new_price = ''.join(re.findall(r'\d', new_price))

        cover_list = tree.xpath(BooksLocators.cover_xpath)
        cover = check_html_element_existing(cover_list)

        if 'твердая' in cover:
            cover = 'Твердый переплет'
        elif 'мягкий' in cover:
            cover = 'Мягкая обложка'
        else:
            cover = ''
            # cover = 'Надо пометить ячейку красным'

    weight_list = tree.xpath(site_locators.weight_xpath)
    weight = check_html_element_existing(weight_list)
    if weight:
        weight = ''.join(re.findall(r'\d', weight))

    dimension_list = tree.xpath(site_locators.dimensions_xpath)
    dimensions = check_html_element_existing(dimension_list)
    if dimensions:
        if re.search(r'\d', dimensions):
            dimensions = re.split(r'\D', (''.join(re.sub(r' ', '', dimensions))))
            dimensions = list(filter(None, dimensions))
            if len(dimensions) == 1:
                length = dimensions[0]
                width = ''
                height = ''

            elif len(dimensions) == 2:
                length = dimensions[0]
                width = dimensions[1]
                height = ''

            elif len(dimensions) == 3:
                length = dimensions[0]
                width = dimensions[1]
                height = dimensions[2]




        else:
            width = ''
            height = ''
            length = ''




    else:
        width = ''
        height = ''
        length = ''

    author_code = tree.xpath(site_locators.author_xpath)
    author = ''
    for elem in author_code:
        if re.search('[а-яА-Я]', elem):
            author += elem.strip()
            break

    publisher_list = tree.xpath(site_locators.publisher_xpath)
    publisher = check_html_element_existing(publisher_list)

    series_list = tree.xpath(site_locators.series_xpath)
    series = check_html_element_existing(series_list)

    pages_list = tree.xpath(site_locators.pages_xpath)
    pages = check_html_element_existing(pages_list)
    if pages:
        pages = ''.join(re.findall(r'\d', pages))

    logger.debug(f'ISBN: {ISBN}')

    if name == 'Десять негритят':
        pass


    data_dict = {'number': NUMBER, 'name': name, 'new_price': new_price, 'old_price': old_price, 'barcode': BARCODE,
                 'weight': weight, 'width': width, 'height': height, 'length': length, 'photo_link': PHOTO_LINK,
                 'isbn': ISBN, 'genre': genre, 'author': author, 'annotation': annotation,
                 'publisher': publisher, 'year': YEAR, 'series': series, 'pages': pages,
                 'colored_pics': colored_pics, 'lang': LANG, 'orig_name': orig_name, 'keeping': KEEPING,
                 'editor': editor, 'illustrator': illustrator, 'circulation': circulation, 'cover': cover}

    return data_dict


def save_to_table(row_count, sheet, data_dict):

    if data_dict['name'] == 'Десять негритят':
        pass
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
    sheet[f'AR{row_count}'].value = data_dict['circulation']
    sheet[f'AS{row_count}'].value = data_dict['lang']
    sheet[f'AT{row_count}'].value = data_dict['orig_name']
    sheet[f'AW{row_count}'].value = data_dict['keeping']
    sheet[f'CX{row_count}'].value = data_dict['editor']
    sheet[f'DA{row_count}'].value = data_dict['illustrator']
    if site_locators == BooksLocators:
        cells = sheet[row_count]
        for cell in cells:
            cell.fill = PatternFill(fill_type='solid', start_color='ff0000')
    work_book.save('Books_info.xlsx')


set_logger()
first_row_check = 1
COUNT = 0

COUNT_OF_BOOKS = 0

COUNT_LABIRINT_BOOKS = 0
COUNT_BOOKS_RU_BOOKS = 0

COUNT_ROW_BUKINISTICA_SHEET = 1
COUNT_ROW_SECOND_HAND_SHEET = 1
ROWS_COUNT_NO_YEAR = 1
ROWS_COUNT_NO_INFO = 1

start_time = datetime.now()
requests.urllib3.disable_warnings(category=InsecureRequestWarning)

work_book = load_workbook('Books_info.xlsx')
sheet_ranges = work_book['Входные данные']

GENRES_LIST = get_data_from_genres_file('Genres.xlsx')

for row in sheet_ranges.rows:
    COUNT += 1
    if first_row_check == 1:
        first_row_check += 1
        continue
    COUNT_OF_BOOKS += 1
    NUMBER, ISBN, PHOTO_LINK, KEEPING, LANG, BARCODE = get_input_data(row)

    site_locators, book_link = get_book_link(ISBN)

    if site_locators == LabirintLocators:
        COUNT_LABIRINT_BOOKS += 1
    elif site_locators == BooksLocators:
        COUNT_BOOKS_RU_BOOKS += 1

    TREE = get_site_tree(book_link)
    time_interval_list = get_years_sequence(2011, 2025)

    if not check_for_book_existing(ISBN):
        ROWS_COUNT_NO_INFO = filing_empty_sheet(ROWS_COUNT_NO_INFO, 'Без информации')
        logger.critical('Книги нет на сайтах')
        continue

    sheet_name, YEAR = define_which_sheet(time_interval_list, TREE)

    if sheet_name == 'Букинистика':
        COUNT_ROW_BUKINISTICA_SHEET += 1
        COUNT = COUNT_ROW_BUKINISTICA_SHEET

    elif sheet_name == 'Second-hand':
        COUNT_ROW_SECOND_HAND_SHEET += 1
        COUNT = COUNT_ROW_SECOND_HAND_SHEET

    elif sheet_name == 'Без года':
        ROWS_COUNT_NO_YEAR += 1
        COUNT = ROWS_COUNT_NO_YEAR

    DATA_DICT = get_data(TREE)

    if site_locators == LabirintLocators:
        site = 'Лабиринт'
    else:
        site = 'Books.ru'

    save_to_table(COUNT, sheet_name, DATA_DICT)
    end_time = datetime.now()
    wasted_time = end_time - start_time
    logger.debug(f'Потрачено времени: {wasted_time}')
    logger.info(f'Книг обработано: {COUNT_OF_BOOKS}')

logger.info('Скрипт завершил работу!')
