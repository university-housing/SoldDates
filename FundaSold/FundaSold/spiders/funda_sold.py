import scrapy
import re
import os
import json
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()


def produce_links(link, start_page):
    '''
    This function gets all items listed on one page
    The items are found inside a javascript div called application/ld+json
    :param link: The url we want to get the items from
    :param start_page: Page number
    :return: All listed items inside of the JS script
    '''
    url = link + "p" + str(start_page)
    content = os.popen("links2 -source " + url)
    soup = BeautifulSoup(content, "lxml")
    soup = soup.find_all("div", {'class', 'search-content-output'})[0]
    res = soup.find_all("script", {"type": "application/ld+json"})
    for js in res:
        json_element = json.loads(js.contents[0])
        if "itemListElement" in json_element:
            res_script = json_element
            result = []
            for element in res_script["itemListElement"]:
                message = element["url"]
                message += "\n"
                result.append(message)
            return result


class Info(scrapy.Field):
    Id = scrapy.Field()
    ######UNNECESSARY DEFINING OF FIELDS#############
    Aangebodensinds = scrapy.Field()
    Status = scrapy.Field()
    Verkoopdatum = scrapy.Field()
    Looptijd = scrapy.Field()
    Url = scrapy.Field()
    Updated_sold = scrapy.Field()


class FundaSold(scrapy.Spider):
    name = "funda_sold"

    handle_httpstatus_list = [404, 500, 401]

    def start_requests(self):
        f = open("/home/hiba/PycharmProjects/SoldDates/FundaSold/FundaSold/spiders/house_element.html", "r+")
        # Generate a random User agent
        headers = {'User-Agent': ua.random}

        # Go through all funda sold pages (retrieved from funda website)
        for page in range(6414, 12920):
            print('\033[92m' + "PAGE: " + str(page) + '\033[0m')
            f2 = open("lastpage.txt", "w")
            f2.write(str(page) + "\n")
            f2.close()

            one_page_elements = produce_links(
                "https://www.funda.nl/koop/heel-nederland/verkocht/sorteer-afmelddatum-af/", page)

            # Save all items as a Html file and parse that file, then save to a database
            for element in one_page_elements:
                print("ELEMENT! ", element)
                content = os.popen("links2 -source " + element)
                html_content = BeautifulSoup(content, features="lxml")
                f.seek(0)
                f.write(str(html_content))
                f.truncate()
                yield scrapy.Request(
                    "file:///home/hiba/PycharmProjects/SoldDates/FundaSold/FundaSold/spiders/house_element.html",
                    callback=self.parse, dont_filter=True)



    def parse(self, response):
        res = response.xpath(
            "//div[@class='object-kenmerken-body']//text()[not(ancestor::h3)][not(ancestor::div[@class='' or @class='kadaster-title'])][not(ancestor::a)]").getall()
        res = [re.sub(r"\r\n", "", str) for str in res]
        res = [str.strip() for str in res]
        res = list(filter(None, res))

        res[0::2] = [re.sub(r" |-", "", str) for str in res[0::2]]
        res[1::2] = [re.sub(r" januari ", "-01-", str) for str in res[1::2]]
        res[1::2] = [re.sub(r" februari ", "-02-", str) for str in res[1::2]]
        res[1::2] = [re.sub(r" maart ", "-03-", str) for str in res[1::2]]
        res[1::2] = [re.sub(r" april ", "-04-", str) for str in res[1::2]]
        res[1::2] = [re.sub(r" mei ", "-05-", str) for str in res[1::2]]
        res[1::2] = [re.sub(r" juni ", "-06-", str) for str in res[1::2]]
        res[1::2] = [re.sub(r" juli ", "-07-", str) for str in res[1::2]]
        res[1::2] = [re.sub(r" augustus ", "-08-", str) for str in res[1::2]]
        res[1::2] = [re.sub(r" september ", "-09-", str) for str in res[1::2]]
        res[1::2] = [re.sub(r" oktober ", "-10-", str) for str in res[1::2]]
        res[1::2] = [re.sub(r" november ", "-11-", str) for str in res[1::2]]
        res[1::2] = [re.sub(r" december ", "-12-", str) for str in res[1::2]]
        info = Info()
        # added 12/07/2019
        # status = response.xpath('//*[@id="content"]/div/div/div[1]/header/div/div/div[1]/ul/li//text()')[0].get()
        status = ""
        info['Aangebodensinds'] = ""
        info['Status'] = status
        info['Verkoopdatum'] = ""
        info['Looptijd'] = ""
        info['Sold'] = "True"
        info["Updated_sold"] = "True"
        info['Url'] = response.xpath("//link[@rel='canonical']/@href").get().replace('verkocht/', '')
        for dt_name, dd_value in zip(res[0::2], res[1::2]):
            dt_name = dt_name.translate(
                {ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).replace("\n", "").strip(
                "\t").strip().capitalize()
            if dt_name in info.keys():
                info[dt_name] = dd_value.replace(" m²", "")

        yield info


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    # Update settings every time to get the new updated proxy list
    FundaSold.custom_settings = {'RETRY_TIMES': 10}
    process = CrawlerProcess(get_project_settings())
    process.crawl(FundaSold)
    process.start()
