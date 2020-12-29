class LabirintLocators:
    year_xpath = '//div[@class="publisher"]/text()[2]'
    name_xpath = '//div[@id="product-title"]/h1/text()'
    no_price_xpath = '//span[@class="buying-priceold-val"]'
    price_without_discount_xpath = '//span[@class="buying-price-val-number"]/text()'
    old_price_xpath = '//span[@class="buying-priceold-val-number"]/text()'
    new_price_xpath = '//span[@class="buying-pricenew-val-number"]/text()'
    weight_xpath = '//div[@class="weight"]/text()'
    dimensions_xpath = '//div[@class="dimensions"]/text()'
    cover_xpath = '//div[@class="popup-middle"]/div[1]/text()'
    author_xpath = '//div[@class="authors"]/a/text()'
    colored_pics_xpath = '//div[@class="popup-middle"]//text()'
    annotation_xpath = '//div[@id="product-about"]//p//text()'
    publisher_xpath = '//div[@class="publisher"]/a/text()'
    series_xpath = '//div[@class="series"]/a/text()'
    pages_xpath = '//div[@class="pages2"]/text()'
    orig_name_xpath = '//h2[@class="h2_eng"]/text()'
    editor_xpath = '//a[@data-event-label="editor"]/text()'
    illustrator_xpath = '//*[text()="Художник: "]/text()/following-sibling::a/text()'
    genres_xpath = '//div[@id="thermometer-books"]//a/span/text()'
    product_cover = '//a[@class="product-title-link"]/@href'


class BooksLocators:
    year_xpath = '//td[text()="Дата выхода:"]/following::td[1]/text()'
    # year_xpath = '//table[@class="specifications_table"]//tr[2]/td[2]/text()'
    name_xpath = '//h1/text()'
    no_price_xpath = ''
    # price_without_discount_xpath = '//h3[@class="h3 book-price sale"]/text()'
    # old_price_from_labirint_xpath = '//p[@class="p book-price-full-sale"]/text()'
    # new_price_xpath = '//h3[@class="h3 book-price sale"]/text()[1]'
    weight_xpath = '//td[text()="Масса:"]/following-sibling::td/text()'
    # genres_xpath = '//div[@class="route-wrap"]/span/a/span/text()'  # все жанры берет
    genres_xpath = '//div[@class="route-wrap"]/span[3]/a/span/text()'  # третий элемент
    # text_dimensions_xpath = '//tbody/tr[7]/td[1]/text()'
    dimensions_xpath = '//tbody/tr[7]/td[2]/text()'
    author_xpath = '//div[@class="author-link-wrap"]//text()'
    cover_xpath = '//td[text()="Обложка:"]/following-sibling::td/text()'
    full_annotation_xpath = '//div[@class="all_note"]/*//text()'
    short_annotation_xpath = '//div[@class="note"]/p/span/text()'
    publisher_xpath = '//ul[@class="isbn-list"]//li[4]/a/text()'
    series_xpath = '//table[@class="specifications_table"]//tr[2]/td[2]/a/text()'
    pages_xpath = '//td[text()="Объём:"]/following-sibling::td/text()'
    circulation = '//td[text()="Тираж:"]/following-sibling::td/text()'


class OzonLocators:
    exist_text = '//div[@class="b6r7"]/strong/text()'
    product_page_link = '//div[@class="container b6e3"]//a[2]'
    cheapest_book_page_link = '//span[text()="Лучшая цена на Ozon"]/following-sibling::a'
    photo_link = '//div[@class="a8n3"]/div/img'
    # found_items = '//div[@class="ui-a1j5 ui-a1h"]' # хуевая проверка, срабатывает тут: https://www.ozon.ru/search/?text=5-18-000702-%D0%A5&from_global=true&brand=87317976
    # found_items_1 = '//div[contains(text(), "По запросу")]' # проверка наличия книги видимо
    isbn_exist = '//div[@class="b6r7"]/strong/text()' # проверка наличия книги видимо

    price = '//div[@class="client-state"]/div[@id="state-addToFavorite-347772-default-1"]/@data-state'
    # price_ozon_premium = '//div[@class="c8x9"]/span[@class="b0r3"]/span[contains(text(), "Цена с")]'