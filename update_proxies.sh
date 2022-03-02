#!/usr/bin/zsh
#curl https://api.proxyscrape.com/\?request\=getproxies\&proxytype\=socks4\&timeout\=800 -o /home/john/huispedia_scraper/src/proxylists/socks4list.txt

while true
do
   curl https://api.proxyscrape.com/\?request\=getproxies\&proxytype\=socks5\&timeout\=800 -o /home/hiba/PycharmProjects/SoldDates/FundaSold/socks5list.txt
  sleep 300
done
