# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector
import logging


class FundasoldPipeline:
    def __init__(self):
        self.create_connection()

    def create_connection(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='root',
            database='funda_database')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()
        logging.info("Closing mysql connection")

    def close_spider(self, spider):
        self.conn.close()
        logging.info("Closing mysql connection")

    def process_item(self, item, spider):
        self.update_db(item)
        return item

    def update_db(self, item):

        query = "UPDATE funda SET "

        for i in item.keys():
            if i != 'Url':
                if item[i] != None:
                    query = query + i + " = '" + \
                            item[i].strip().replace("\n", "").replace(
                                "\t", "").replace("'", '"').strip() + "'" + ","
                else:
                    query = query + "'',"
        query = query[0:-1] + " WHERE Url='" + item['Url'] + "';"

        print("WEEEEEEEEEEELLL")
        print(query)
        result = self.cursor.execute(query)
        if result == None:
            item["Wonen"] = "0"
            query = "INSERT INTO funda ( " + ', '.join(item.keys()) + " ) values ( " + ", ".join(
                "'" + element.strip().replace("\n", "").replace(
                    "\t", "").replace("'", '"').strip() + "'" for element in item.values()) + " );"
            print(query)
            try:
                self.cursor.execute(query, multi=True)
            except:
                pass
        self.conn.commit()
        #self.conn.close()
