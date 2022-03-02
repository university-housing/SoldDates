import mysql
import mysql.connector
import pandas as pd
from datetime import datetime
from dateutil import parser
import matplotlib.pyplot as plt
query = '''
SELECT Url, Verkoopdatum 
FROM funda
where Sold = "True" ;
'''

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='root',
    database='funda_database')
cursor = conn.cursor()
cursor.execute(query)
dates = []
for row in cursor.fetchall():
    try:
        r = parser.parse(row[1])
        dates.append(r.date())
    except:
        pass
conn.close()
data = {"Dates": dates}
df = pd.DataFrame(data)

df["Dates"] = df["Dates"].astype("datetime64")
#df.groupby(df["Dates"].dt.month).count().plot(kind="bar")
i = 0
print(df.groupby([df["Dates"].dt.year, df["Dates"].dt.month]).size())



plt.show()
