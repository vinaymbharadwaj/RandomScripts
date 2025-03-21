from os import walk

directory = "D:\\DATA\\Git Projects\\RandomScripts\\E-Book Editor\\Angel\\OEBPS\\Text"
filenames = next(walk(directory), (None, None, []))[2]  # [] if no file
for item_name in filenames:
    if(not "Cover.xhtml" in item_name):
        chapter_title = item_name.split("_",1)[1].replace("_"," ").replace(".xhtml","")
        print(chapter_title)
        item_content = open(directory+"\\"+item_name, "r", encoding="utf-8").read().replace("<body>","<body><h1>"+chapter_title+"</h1>")
        open(directory+"\\"+item_name, "w", encoding="utf-8").write(item_content)