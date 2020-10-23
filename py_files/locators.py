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
    annotation_xpath = '//div[@id="product-about"]//p//text()'
    publisher_xpath = '//div[@class="publisher"]/a/text()'
    series_xpath = '//div[@class="series"]/a/text()'
    pages_xpath = '//div[@class="pages2"]/text()'
    orig_name_xpath = '//h2[@class="h2_eng"]/text()'
    editor_xpath = '//a[@data-event-label="editor"]/text()'
    illustrator_xpath = '//*[text()="Художник: "]/text()/following-sibling::a/text()'


class BooksLocators:
    year_xpath = '//table[@class="specifications_table"]//tr[2]/td[2]/text()'
    name_xpath = '//h1/text()'
    no_price_xpath = ''
    price_without_discount_xpath = '//h3[@class="h3 book-price sale"]/text()'
    old_price_xpath = '//p[@class="p book-price-full-sale"]/text()'
    new_price_xpath = '//h3[@class="h3 book-price sale"]/text()[1]'
    weight_xpath = '//td[text()="Масса:"]/following-sibling::td/text()'
    genre_xpath = '//span[@itemtype="http://schema.org/ListItem"]//following::span[@itemprop="name"]/text()'  # нужно взять последний элемент!
    # text_dimensions_xpath = '//tbody/tr[7]/td[1]/text()'
    dimensions_xpath = '//tbody/tr[7]/td[2]/text()'
    author_xpath = '//div[@class="author-link-wrap"]//text()'
    cover_xpath = '//td[text()="Обложка:"]/following-sibling::td/text()'
    annotation_xpath = '//div[@class="note"]/p/text()'
    publisher_xpath = '//ul[@class="isbn-list"]//li[4]/a/text()'
    series_xpath = '//table[@class="specifications_table"]//tr[2]/td[2]/a/text()'
    pages_xpath = '//td[text()="Объём:"]/following-sibling::td/text()'
    circulation = '//td[text()="Тираж:"]/following-sibling::td/text()'
