from os import walk
import re
import htmlmin

directory = "C:\\DATA\\Git Clones\\RandomScripts\\E-Book Editor\\DDW\\1\\EPUB"
filenames = next(walk(directory), (None, None, []))[2]  # [] if no file
for item_name in filenames:
    if("chapter" in item_name):
        print(str(item_name).capitalize())
        item_content = open(directory+"\\"+item_name, "r", encoding="cp437").read()
        item_content=htmlmin.minify(item_content, remove_comments=True, remove_empty_space=True)        
        regular_expression = "(<p>-----)[\s\S]*?(----</p></body>)"
        x = re.sub(regular_expression, "</body>", item_content)
        #print(str(x))     
        open(directory+"\\"+item_name, "w", encoding="cp437").write(item_content)