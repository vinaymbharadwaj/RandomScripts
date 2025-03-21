from os import walk
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

toc_file = "C:\\DATA\\Git Clones\\RandomScripts\\E-Book Editor\\HBW\\EPUB\\toc.ncx"
item_content = open(toc_file, "r", encoding="cp437").read()
soup = BeautifulSoup(item_content, features="xml")
for item in soup.find_all('navPoint'):
    id = item.get('id')
    if(id and "chapter" in id):
        chapter_number = item.find('content').get('src').replace("_"," ").replace(".xhtml","").capitalize()
        chapter_name = item.find('text')
        chapter_name.string = chapter_number+": "+chapter_name.text

open(toc_file, "w", encoding="cp437").write(str(soup))