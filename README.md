# tocer.py

Scaffold nested documents based on TOC

# How to use

* Create a TOC file (e.g: `README.md`) containing nested bullets (use asterisk and 2 spaces)
* Run `python tocer.py <toc-file>` (e.g: `python tocer.py README.md`).

# Expected result

* Every bullet item in your TOC file will turn into link, unless it is already a link.
* If the documents refered by the links are not exist, they will be created.