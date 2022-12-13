#!/usr/bin/python3
import re
import sys
import requests
import argparse
import random
import string
import threading
import time
import urllib.parse
from bs4 import BeautifulSoup
import json

tlock = threading.Lock()

threads = 10
freq_threshold = 3
max_len = 10
min_len = 4
tor = 0
debug = 0

parser = argparse.ArgumentParser()
parser.add_argument('sites')
parser.add_argument('-t', '--threads')
parser.add_argument('-z', '--tor', action="store_true")
parser.add_argument('-m', '--max-len')
parser.add_argument('-n', '--min-len')
parser.add_argument('-s', '--freq-threshold')
args = parser.parse_args()

words_located = []

sites = []
try:
 with open(args.sites, "rb") as file:
  sites = file.read().decode().splitlines()
except:
 sites = [args.sites]

if args.tor:
 tor = 1

if args.freq_threshold:
 freq_threshold = int(args.freq_threshold)

if args.min_len:
 min_len = int(args.min_len)

if args.max_len:
 max_len = int(args.max_len)

def scrape(url):
 global words_located
 proxies = {}
 if tor == 1:
  proxies["http"] = "socks5h://127.0.0.1:9050"
  proxies["https"] = "socks5h://127.0.0.1:9050"
 headers = {
  "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0"
 }
 r = requests.get(url=url, headers=headers, proxies=proxies)
 datas = re.sub(r'[\W]', " ", r.text).split()
 dict_curr = {}
 for word in datas:
  word = word.lower()
  word = re.sub(r'\d+', "", word)
  word = word.replace("_", "")
  if word.isdigit(): continue
  if len(word) < min_len or len(word) > max_len: continue
  with tlock:
   if word in words_located: continue
  if not word in dict_curr:
   dict_curr[word] = 1
  else:
   dict_curr[word] += 1   
 for word in dict_curr.keys():
  if dict_curr[word] >= freq_threshold:
   print(word)
   with tlock: 
    if not word in words_located: words_located.append(word)

def _start():
 global sites
 while len(sites):
  with tlock: site = sites.pop(0)
  try:
   scrape(site)
  except Exception as error:
   if debug == 1: print(error)

def main():
 for i in range(threads):
  t=threading.Thread(target=_start)
  t.start()

if __name__ == "__main__":
 main()
