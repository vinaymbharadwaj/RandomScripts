from os import walk
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

nav_file = "C:\\DATA\\Git Clones\\RandomScripts\\E-Book Editor\\HBW\\EPUB\\nav.xhtml"
item_content = open(nav_file, "r", encoding="cp437").read()
soup = BeautifulSoup(item_content, features="xml")
for item in soup.find_all('a'):
    id = item.get('href')
    if(id and "chapter" in id):
        chapter_number = str(id).replace("_"," ").replace(".xhtml","").capitalize()
        changed_name = chapter_number+" - "+str(item.text)
        print(str(id)+" : "+changed_name)
        item.string = changed_name

open(nav_file, "w", encoding="cp437").write(str(soup))