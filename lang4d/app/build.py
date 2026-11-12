#!/usr/bin/env python3
"""Build the KANON course page: template.html + kanon.js + course/course.json -> index.html (course/NN.mp3 published beside it)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); L = os.path.dirname(HERE)
js = open(os.path.join(L, "kanon.js"), encoding="utf-8").read()
course = json.dumps(json.load(open(os.path.join(L, "course", "course.json"), encoding="utf-8")), ensure_ascii=False).replace("</", "<\\/")
html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read().replace("/*__KANONJS__*/", js).replace("/*__COURSE__*/null", course)
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(html); print("index.html", len(html) // 1024, "KB")
