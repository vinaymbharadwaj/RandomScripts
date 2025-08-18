#!/usr/bin/python
# coding: latin-1
from bs4 import BeautifulSoup
from ebooklib import epub
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import textwrap
import cfscrape
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from deep_translator import GoogleTranslator
import time
import os

class ChapterTitle(object):
    def parse(self,sitename,soup_obj):
        method_name='parse_'+str(sitename)
        self.soup = soup_obj
        method=getattr(self,method_name,lambda :"invalid")
        return method()
    def parse_readnovelfull(self):
        chapterTitle = self.soup.select_one('a[class="chr-title"]').get('title')
        if not chapterTitle:
            chapterTitle = "invalid"
        return chapterTitle
    def parse_royalroad(self):
        chapterTitle = self.soup.title.string
        if not chapterTitle:
            chapterTitle = "invalid"
        return chapterTitle
    def parse_scribblehub(self):
        chapterTitle = self.soup.title.string
        if not chapterTitle:
            chapterTitle = "invalid"
        return chapterTitle
    def parse_boxnovel(self):
        chapterTitle = self.soup.title.string
        if not chapterTitle:
            chapterTitle = "invalid"
        return chapterTitle
    def parse_readwebnovels(self):
        chapterTitle = self.soup.title.string
        if not chapterTitle:
            chapterTitle = "invalid"
        return chapterTitle
    def parse_instadoses(self):
        chapterTitle = self.soup.select_one('h1[id="chapter-heading"]')
        if not chapterTitle:
            chapterTitle = self.soup.title.string if self.soup.title.string else "invalid"        
        return chapterTitle
    def parse_novelfun(self):
        chapterTitle = self.soup.select_one('h1[class="css-1ch487y"]')
        if not chapterTitle:
            chapterTitle = self.soup.title.string if self.soup.title.string else "invalid"        
        return chapterTitle
    def parse_ranobes(self):
        chapterTitle = self.soup.title.string if self.soup.title.string else "invalid"        
        return chapterTitle
    def parse_tracan(self):
        chapterTitle = self.soup.title.string if self.soup.title.string else "invalid"        
        return chapterTitle
    def parse_shuhaige(self):
        chapterTitle = self.soup.title.string if self.soup.title.string else "invalid"  
        return chapterTitle
    def parse_tomatomtl(self):
        chapterTitle = self.soup.select_one('h1[class="chapter_title"]')
        if not chapterTitle:
            chapterTitle = self.soup.title.string if self.soup.title.string else "invalid"        
        return chapterTitle
    def parse_biquge(self):
        chapterTitle = self.soup.select_one('div[class="book"] h1')
        if not chapterTitle:
            chapterTitle = self.soup.title.string if self.soup.title.string else "invalid"
        return chapterTitle
    def parse_xszj(self):
        chapterTitle = self.soup.select_one('h1[class="bookname"]').text
        if not chapterTitle:
            chapterTitle = self.soup.title.string if self.soup.title.string else "invalid"        
        return chapterTitle
    def parse_dxs(self):
        chapterTitle = self.soup.select_one('h1[class="chaptername"]').text
        if not chapterTitle:
            chapterTitle = self.soup.title.string if self.soup.title.string else "invalid"        
        return chapterTitle
    def parse_tongrenquan(self):
        chapterTitle = self.soup.select_one('h1').text
        if not chapterTitle:
            chapterTitle = self.soup.title.string if self.soup.title.string else "invalid"        
        return chapterTitle

class ChapterContent(object):
    def parse(self,sitename,soup_obj,chapterTitle):
        method_name='parse_'+str(sitename)
        self.soup = soup_obj
        self.chapterTitle = chapterTitle
        method=getattr(self,method_name,lambda :"invalid")
        return method()
    def parse_readnovelfull(self):
        div = self.soup.select_one('div[id="chr-content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_royalroad(self):
        div = self.soup.select_one('div[class="chapter-inner chapter-content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_scribblehub(self):
        div = self.soup.select_one('div[class="chp_raw"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_boxnovel(self):
        div = self.soup.select_one('div[class="entry-content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_readwebnovels(self):
        div = self.soup.select_one('div[class="reading-content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_instadoses(self):
        div = self.soup.select_one('div[class="reading-content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_novelfun(self):
        div = self.soup.select_one('div[class="fontSize-2 css-p8fe3q-Content e1ktwp231"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_ranobes(self):
        #print(str(self.soup))
        div = self.soup.select_one('div[id="arrticle"]')
        #print("Div: "+str(div))
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_tracan(self):
        div = self.soup.select_one('div[class="entry-content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+str(div).split("Partager")[0].encode('utf-8')
        return chapter_content
    def parse_shuhaige(self):
        div = self.soup.select_one('div[id="content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_tomatomtl(self):
        article = self.soup.select_one('article[id="chapter_content"]')
        for a in article.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+article.encode('utf-8')
        return chapter_content
    def parse_biquge(self):
        div = self.soup.select_one('div[id="chaptercontent"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_xszj(self):
        div = self.soup.select_one('div[id="booktxt"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_dxs(self):
        div = self.soup.select_one('div[id="txt"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_tongrenquan(self):
        div = self.soup.select_one('div[class="read_chapterDetail"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1>"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content

class NextChapterLink(object):
    def parse(self,sitename,soup_obj,website_url):
        method_name='parse_'+str(sitename)
        self.soup = soup_obj
        self.website_url = website_url
        method=getattr(self,method_name,lambda :"invalid")
        return method()
    def parse_readnovelfull(self):
        anchor = self.soup.select_one('a[id="next_chap"]')
        if anchor.get('href'):
            page_url = self.website_url + str(anchor.get('href'))
        else:
            page_url = "invalid"
        return page_url
    def parse_royalroad(self):
        page_url = "invalid"
        anchor_all = self.soup.findAll("a", {"class": "btn btn-primary col-xs-12"})
        for anchor in anchor_all:
            if "Next" in str(anchor.text):
                if anchor.get('href'):
                    page_url = self.website_url + str(anchor.get('href'))
                    break
        return page_url
    def parse_scribblehub(self):
        page_url = "invalid"
        anchor_all = self.soup.findAll("a", {"class": "btn-wi btn-next"})
        for anchor in anchor_all:
            if "Next" in str(anchor.text):
                if anchor.get('href'):
                    page_url = str(anchor.get('href'))
                    break
        return page_url
    def parse_boxnovel(self):
        page_url = "invalid"
        anchor_all = self.soup.findAll("a", {"class": "btn next_page"})
        for anchor in anchor_all:
            if "Next" in str(anchor.text):
                if anchor.get('href'):
                    page_url = str(anchor.get('href'))
                    break
        return page_url
    def parse_readwebnovels(self):
        page_url = "invalid"
        anchor_all = self.soup.findAll("a", {"class": "btn next_page"})
        for anchor in anchor_all:
            if "Next" in str(anchor.text):
                if anchor.get('href'):
                    page_url = str(anchor.get('href'))
                    break
        return page_url
    def parse_instadoses(self):
        page_url = "invalid"
        anchor_all = self.soup.findAll("a", {"class": "btn next_page"})
        for anchor in anchor_all:
            if "Next" in str(anchor.text):
                if anchor.get('href'):
                    page_url = str(anchor.get('href'))
                    break
        return page_url
    def parse_novelfun(self):
        page_url = "invalid"
        anchor_all = self.soup.findAll("a", {"class": "css-122d1rp"})
        for anchor in anchor_all:
            if "Next" in str(anchor.text):
                if anchor.get('href'):
                    page_url = self.website_url + str(anchor.get('href'))
                    break
        return page_url
    def parse_ranobes(self):
        page_url = "invalid"
        anchor = self.soup.select_one('a[id="next"]')
        if anchor and anchor.get('href'):
            if str(anchor.get('href')) != "./":
                page_url = str(anchor.get('href'))
        return page_url
    def parse_tracan(self):
        page_url = "invalid"
        div = self.soup.select_one('div[class="entry-content"]')
        anchor_all = div.select('a')
        for anchor in anchor_all:
            if "Next" in str(anchor.text):
                if anchor.get('href'):
                    page_url = str(anchor.get('href'))
                    break
        return page_url
    def parse_shuhaige(self):
        page_url = "invalid"
        anchor = self.soup.select_one('a[id="pager_next"]')
        if anchor and anchor.get('href'):
            if not "shu_" in str(anchor.get('href')):
                page_url = self.website_url + str(anchor.get('href'))
        return page_url
    def parse_tomatomtl(self):
        page_url = "invalid"
        anchor = self.soup.select_one('a[id="next-chap2"]')
        if anchor and anchor.get('href'):
            if not "undefined" in str(anchor.get('href')):
                page_url = self.website_url + str(anchor.get('href'))
        print("Page URL: "+str(page_url))
        return page_url
    def parse_biquge(self):
        page_url = "invalid"
        anchor = self.soup.select_one('a[id="next_url"]')
        if anchor and anchor.get('href'):
            if str(anchor.get('href')).count("/") == 3:
                page_url = self.website_url + str(anchor.get('href'))
        return page_url
    def parse_xszj(self):
        time.sleep(1)
        page_url = "invalid"
        anchor_next = self.soup.select('a[rel="next"]')
        if(not anchor_next):
            anchor_next = self.soup.select('a[rel="prev"]')[1]
        else:
            anchor_next = self.soup.select('a[rel="next"]')[0]
        if anchor_next.get('href') and "/b/" in str(anchor_next.get('href')):
            page_url = self.website_url + str(anchor_next.get('href'))
        return page_url
    def parse_dxs(self):
        page_url = "invalid"
        anchor = self.soup.select_one('a[class="url_next"]')
        if anchor and anchor.get('href'):
            if ".html" in str(anchor.get('href')):
                page_url = str(anchor.get('href'))
        print("Page URL: "+str(page_url))
        return page_url
    def parse_tongrenquan(self):
        page_url = "invalid"
        #div = self.soup.select_one('div[class="pageNav"]')
        anchor_all = self.soup.select('a') #div.select('a')
        for anchor in anchor_all:
            to_translate = str(anchor.text)
            translated_text = GoogleTranslator(source='zh-CN', target='en').translate(to_translate)
            if "next" in str(translated_text).lower():
                if anchor.get('href'):
                    page_url = self.website_url + str(anchor.get('href'))
                    break
        return page_url

def generate_cover(title, author=None, output_path='cover.jpg'):
    # Image size (standard 6x9 inches at 300 DPI)
    width, height = 1800, 2700
    background_color = (0, 0, 0)      # Black
    title_color = (255, 255, 255)     # White
    author_color = (173, 216, 230)    # Light Blue

    # Create the image
    img = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        title_font = ImageFont.truetype(script_dir+"\\Fonts\\trebuc.ttf", 100)
        author_font = ImageFont.truetype(script_dir+"\\Fonts\\msjh.ttc", 50)
    except IOError:
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Wrap title text
    wrapped_title = textwrap.fill(title.upper(), width=15)

    # Calculate text bounding box for title
    title_bbox = draw.textbbox((0, 0), wrapped_title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]

    title_x = (width - title_width) / 2
    title_y = height * 0.3
    draw.text((title_x, title_y), wrapped_title, font=title_font, fill=title_color)

    # Draw author name
    if author:
        author_text = f"by {author}"
        author_bbox = draw.textbbox((0, 0), author_text, font=author_font)
        author_width = author_bbox[2] - author_bbox[0]
        author_height = author_bbox[3] - author_bbox[1]

        author_x = (width - author_width) / 2
        author_y = title_y + title_height + 100
        draw.text((author_x, author_y), author_text, font=author_font, fill=author_color)

    # Save the image
    img.save(output_path)
    print(f"Cover saved to {output_path}")

class EbookCreator(object):
    def __init__(self, input_file="parser_inputs.json"):
        super().__init__()
        self.input_json = json.load(open(input_file,"r", encoding='utf-8'))

    def start_parsing(self):

        # Get the text at the set URL
        #scraper = cfscrape.create_scraper()
        scraper = cloudscraper.create_scraper()

        # Create the epub file
        book = epub.EpubBook()

        # The title you want to give to the book
        title = str(self.input_json["novel_name"])

        # Set the author of the book
        author = "Unknown"
        if(not self.input_json["author"] == ""):
            author = str(self.input_json["author"])

        # Set cover image if available - JPEG only
        cover_image_name = "cover.jpg"
        add_image = True
        image_url = self.input_json["novel_cover_image"]
        if(image_url == ""):
            add_image = False
        if(add_image):
            response_image = requests.get(image_url).content
            f = open(cover_image_name,'wb')
            f.write(response_image)
            f.close()
        else:
            # Cover image not specified, so I will create one
            add_image = True
            generate_cover(title, author, cover_image_name)
        
        # Set cover image
        book.set_cover(cover_image_name, open(cover_image_name, 'rb').read())
        
        # Get website details
        website_name = str(self.input_json["website_name"])
        website_url = str(self.input_json["website_root"])
        start_chapter = str(self.input_json["start_chapter_url"])
        page_url = website_url+start_chapter

        tableOfContents = ()
        book.set_title(title)
        book.set_language('en')
        book.add_author(author)

        # Add cover image to the beginning of the book
        image_html = '<html><body><div class="fullscreenimage"><img src="cover.jpg" alt="cover_image" /></div></body></html>'
        image_css = "div.fullscreenimage , div.fullscreenimage img {page-break-before: always; height: 100%;}"
        cover_chapter = epub.EpubHtml(title='Cover Image', file_name='cover_chapter.xhtml', lang='hr')
        cover_chapter.set_content(image_html)
        book.add_item(cover_chapter)

        # Creating table of content and book spine
        book.toc.append(cover_chapter) 
        book.spine = ['nav', cover_chapter]

        status = True
        i = self.input_json["start_chapter_number"] if self.input_json["start_chapter_number"] else 1

        # Setup Selenium ChromeDriver
        use_selenium = str(self.input_json["use_selenium"])
        if(use_selenium == "true"):
            # Set up Chrome options for headless browsing
            # For Edge use: chrome_options = EdgeOptions() and driver = webdriver.Edge(options=chrome_options) at the end...
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run without opening browser window
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument("--log-level=1")
            chrome_options.add_argument('--enable-unsafe-swiftshader')
            # Initialize the WebDriver (assuming Chrome)
            driver = webdriver.Chrome(options=chrome_options)

        while status:
            
            if(use_selenium == "true"):
                if(website_name == "tomatomtl"):
                    id_name = "chapter_content"
                elif(website_name == "biquge"):
                    id_name = "chaptercontent"
                # Navigate to the URL
                driver.get(page_url)
                # time.sleep(300)
                # Wait for the content to load
                # Wait up to 10 seconds for the chapter content to appear
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, id_name))
                )
                # Give extra time for all content to render
                time.sleep(2)
                # Find the chapter content
                content_div = driver.find_element(By.ID, id_name)
                if not content_div:
                    return "Could not find chapter content on the page"
                page_content = driver.page_source #driver.find_elements(By.TAG_NAME, 'html')
            else:
                #First timeout is for session and second is for page wait
                #page_content = requests.get(page_url, timeout=(10, 10)).content 
                page_content = scraper.get(page_url).content
            
            #print(page_content)
            soup = BeautifulSoup(page_content, "lxml")
                        
            chapterTitle = ChapterTitle().parse(website_name,soup)
            if(chapterTitle=="invalid"):
                chapterTitle = "Chapter "+str(i)
            chapter_content = ChapterContent().parse(website_name,soup,chapterTitle)

            # Creates a chapter
            c1 = epub.EpubHtml(title=chapterTitle, file_name='chap_'+str(i)+'.xhtml', lang='hr')
            c1.content = chapter_content
            book.add_item(c1)

            # Add to table of contents
            book.toc.append(c1)    

            # Add to book ordering            
            book.spine.append(c1)

            print("Parsed " + str(i) + " - " + chapterTitle)
            page_url = NextChapterLink().parse(website_name,soup,website_url) #self.get_next_chapter_link()
            if(page_url=="invalid"):
                status = False

            i = i + 1
            #time.sleep(3)

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Defines CSS style
        style = 'p {text-align: left;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

        # Adds CSS file
        book.add_item(nav_css)

        epub.write_epub(title + '.epub', book, {})

        return

def main():
    ep = EbookCreator()
    ep.start_parsing()

if __name__ == "__main__":
    main()
