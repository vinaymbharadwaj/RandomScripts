#!/usr/bin/python
# coding: latin-1
import cfscrape
from bs4 import BeautifulSoup
from ebooklib import epub
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import cfscrape
import cloudscraper

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
    def parse_wuxiaworldco(self):
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
        add_title = "<h1>"+self.chapterTitle+"</h1><br /><br />"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_royalroad(self):
        div = self.soup.select_one('div[class="chapter-inner chapter-content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1><br /><br />"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_scribblehub(self):
        div = self.soup.select_one('div[class="chp_raw"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1><br /><br />"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_boxnovel(self):
        div = self.soup.select_one('div[class="entry-content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1><br /><br />"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_wuxiaworldco(self):
        div = self.soup.select_one('div[id="content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1><br /><br />"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_readwebnovels(self):
        div = self.soup.select_one('div[class="reading-content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1><br /><br />"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_instadoses(self):
        div = self.soup.select_one('div[class="reading-content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1><br /><br />"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_novelfun(self):
        div = self.soup.select_one('div[class="fontSize-2 css-p8fe3q-Content e1ktwp231"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1><br /><br />"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_ranobes(self):
        #print(str(self.soup))
        div = self.soup.select_one('div[id="arrticle"]')
        #print("Div: "+str(div))
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1><br /><br />"
        chapter_content = add_title.encode('utf-8')+div.encode('utf-8')
        return chapter_content
    def parse_tracan(self):
        div = self.soup.select_one('div[class="entry-content"]')
        for a in div.select("a"):
            a.decompose()
        add_title = "<h1>"+self.chapterTitle+"</h1><br /><br />"
        chapter_content = add_title.encode('utf-8')+str(div).split("Partager")[0].encode('utf-8')
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
    def parse_wuxiaworldco(self):
        page_url = "invalid"
        anchor = self.soup.select_one('a[id="pager_next"]')
        if anchor.get('href'):
            if str(anchor.get('href')) != "./":
                page_url = self.website_url + "/" + str(anchor.get('href'))
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
    

class EbookCreator(object):
    def __init__(self, input_file="parser_inputs.json"):
        super().__init__()
        self.input_json = json.load(open(input_file,"r"))

    def start_parsing(self):

        # Get the text at the set URL
        #scraper = cfscrape.create_scraper()
        scraper = cloudscraper.create_scraper()

        # Create the epub file
        book = epub.EpubBook()

        # The title you want to give to the book
        title = str(self.input_json["novel_name"])

        # Set cover image if available - JPEG only
        add_image = False
        if(not self.input_json["novel_cover_image"] == ""):
            f = open('cover.jpg','wb')
            f.write(requests.get(self.input_json["novel_cover_image"]).content)
            f.close()
        else:
            # Cover image not specified, so I will create one
            image = Image.new('RGB', (600, 800), color = (0, 0, 0))
            draw = ImageDraw.Draw(image)
            a = self.input_json["novel_name"].split()
            message = ''
            for i in range(0, len(a), 4):
                message += ' '.join(a[i:i+4]) + '\n'
            font = ImageFont.truetype('trebuc.ttf', size=20)
            bounding_box = [60, 80, 540, 720]
            x1, y1, x2, y2 = bounding_box  
            w, h = draw.textsize(message, font=font)
            x = (x2 - x1 - w)/2 + x1
            y = (y2 - y1 - h)/2 + y1
            draw.text((x, y), message, align='center', font=font)
            draw.rectangle([x1, y1, x2, y2])
            image.save('cover.jpg')
        
        # Set cover image
        book.set_cover("cover.jpg", open('cover.jpg', 'rb').read())
        add_image = True

        # Get website details
        website_name = str(self.input_json["website_name"])
        website_url = str(self.input_json["website_root"])
        start_chapter = str(self.input_json["start_chapter_url"])
        page_url = website_url+start_chapter

        tableOfContents = ()
        book.set_title(title)
        book.set_language('en')

        # Add cover image to the beginning of the book
        image_html = '<html><body><div class="fullscreenimage"><img src="cover.jpg" alt="cover_image" /></div></body></html>'
        image_css = "div.fullscreenimage , div.fullscreenimage img {page-break-before: always; height: 100%;}"
        cover_chapter = epub.EpubHtml(title='Cover Imge', file_name='cover_chapter.xhtml', lang='hr')
        cover_chapter.set_content(image_html)
        book.add_item(cover_chapter)

        # Creating table of content and book spine
        book.toc.append(cover_chapter) 
        book.spine = ['nav', cover_chapter]

        status = True
        i = self.input_json["start_chapter_number"] if self.input_json["start_chapter_number"] else 1
        while status:

            #page_content = requests.get(page_url).content
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
