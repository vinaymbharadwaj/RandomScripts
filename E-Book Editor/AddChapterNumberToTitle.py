from os import walk

directory = "C:\\DATA\\Git Clones\\RandomScripts\\E-Book Editor\\DDW\\1\\EPUB"
filenames = next(walk(directory), (None, None, []))[2]  # [] if no file
for item_name in filenames:
    if("chapter" in item_name):
        chapter_title = item_name.replace(".xhtml","").replace("_"," ")
        chapter_title = str(chapter_title).capitalize()
        print(str(chapter_title).capitalize())
        # encoding="utf-8", errors="ignore"
        item_content = open(directory+"\\"+item_name, "r", encoding="cp437").read().replace("<title>","<title>"+chapter_title+": ").replace("<body>\n    <h1>","<body><h1>"+chapter_title+": ")
        open(directory+"\\"+item_name, "w", encoding="cp437").write(item_content)