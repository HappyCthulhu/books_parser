import json
from datetime import datetime

from loguru import logger
from openpyxl import load_workbook
import lxml.html
import requests
import re

from urllib3.exceptions import InsecureRequestWarning

from py_files.locators import LabirintLocators, BooksLocators, OzonLocators

from py_files.some_functions import set_logger


def get_data_from_task_one_file(table):
    sheet_genres = table['База ISBN']

    count = 0
    genres_dict = {}
    for cell in sheet_genres['B']:
        count += 1
        if cell.value:
            genres_dict[cell.value] = sheet_genres[f'C{count}'].value
        else:
            break
    logger.debug('Распаковали документ с ISBN')
    return genres_dict


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


def get_site_tree(link):
    html_text = requests.get(link, verify=False).text
    tree = lxml.html.document_fromstring(html_text)
    return tree


def check_html_element_existing(element_list):
    if element_list:
        element_value = element_list[0]
    else:
        element_value = ''
    return element_value

def get_cover_from_books():
    cover_list = TREE.xpath(BooksLocators.cover_xpath)
    cover = check_html_element_existing(cover_list)

    return cover

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
    if 'Тип обложки' in cover_text:
        cover_text = re.findall(r'Тип обложки:\s?(.*)$', cover_text)[0]

    design_list = tree_cover.xpath(LabirintLocators.colored_pics_xpath)
    design_text = ''.join(design_list)
    if 'Иллюстрации' in design_text:
        design_text = re.findall(r'Иллюстрации:\s?(.*)$', design_text)[0]


    return cover_text, design_text

def save_to_table(row_count, sheet):

    sheet = task_zero_file[sheet]

    if site_locators == LabirintLocators:
        sheet[f'A{row_count}'].value = data_dict['number']
        sheet[f'B{row_count}'].value = data_dict['isbn_code']
        sheet[f'C{row_count}'].value = data_dict['cover']
        sheet[f'D{row_count}'].value = data_dict['design_text']

    if site_locators == BooksLocators:
        sheet[f'A{row_count}'].value = data_dict['number']
        sheet[f'B{row_count}'].value = data_dict['isbn_code']
        sheet[f'C{row_count}'].value = data_dict['cover']

    task_zero_file.save('task_zero.xlsx')
    logger.debug(f'Обработано книг: {ROWS_COUNT_ISBN_SHEET}/{len(dict_of_ISBN)}')

set_logger()

requests.urllib3.disable_warnings(category=InsecureRequestWarning)

task_zero_file = load_workbook('task_zero.xlsx')
dict_of_ISBN = get_data_from_task_one_file(task_zero_file)
# print(json.dumps(dict_of_ISBN, indent=2))

COUNT_ROW_LABIRINT_SHEET = 1
COUNT_ROW_BOOKS_HAND_SHEET = 1

ROWS_COUNT_ISBN_SHEET = 0
for number, isbn in dict_of_ISBN.items():

    ROWS_COUNT_ISBN_SHEET += 1

    if not check_for_book_existing(isbn):
        logger.info(f'Книга не существует. Порядковый номер: {number}, ISBN: {isbn}')
        continue

    site_locators, book_link = get_book_link(isbn)

    TREE = get_site_tree(book_link)

    if site_locators == LabirintLocators:
        logger.debug(f'Книга есть в Лабиринте. Линк: {book_link}, ISBN: {isbn}')
        sheet = 'Лабиринт'
        cover, design_text = get_cover_from_labirint(book_link)
        COUNT_ROW_LABIRINT_SHEET += 1
        COUNT_ROW_THIS_BOOK = COUNT_ROW_LABIRINT_SHEET
    else:
        logger.debug(f'Книга есть в Books.ru. Линк: {book_link}, ISBN: {isbn}')
        sheet = 'Букс.ру'
        cover = get_cover_from_books()
        COUNT_ROW_BOOKS_HAND_SHEET += 1
        COUNT_ROW_THIS_BOOK = COUNT_ROW_BOOKS_HAND_SHEET


    data_dict = {'isbn_code':isbn, 'number':number, 'cover': cover, 'design_text': design_text}

    save_to_table(COUNT_ROW_THIS_BOOK, sheet)