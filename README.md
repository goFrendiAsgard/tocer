# tocer.py

Create nested documents based on item list.

From this `README.md`:

```bash
❯ mkdir testDir
❯ cd testDir

# Create a README.md
❯ cat <<EOF > README.md
# Non TOC
* First item
* Second item
# TOC
<!--startToc-->
* Pokemon
   * Kanto
     * Starter
       * Bulbasaur
       * Squirtle
       * Charmender
   * Johto
<!--endToc-->
EOF

# Run tocer.py
❯ python tocer.py
```

Into this directory structure:

```bash
# Get directory structure
❯ tree
.
├── README.md
└── pokemon
    ├── README.md
    ├── johto.md
    └── kanto
        ├── README.md
        └── starter
            ├── README.md
            ├── bulbasaur.md
            ├── charmender.md
            └── squirtle.md

3 directories, 8 files
```

Here is your new `README.md`:

```bash
❯ cat README.md
# Non TOC
* First item
* Second item
# TOC
<!--startToc-->
* [Pokemon](pokemon/README.md)
   * [Kanto](pokemon/kanto/README.md)
     * [Starter](pokemon/kanto/starter/README.md)
       * [Bulbasaur](pokemon/kanto/starter/bulbasaur.md)
       * [Squirtle](pokemon/kanto/starter/squirtle.md)
       * [Charmender](pokemon/kanto/starter/charmender.md)
   * [Johto](pokemon/johto.md)
<!--endToc-->
```

And other documents:

```bash
❯ cat pokemon/kanto/starter/bulbasaur.md
<!--startTocHeader-->
[⬅ Table of Content](../../../README.md)
# Bulbasaur
<!--endTocHeader-->
<!--startTocSubtopic-->
<!--endTocSubtopic-->%
```


# Why

Because any good documentation started with a TOC (or at least I think so).

# Prerequisites

* Python
* just that, nothing else

# How to use

* Create a TOC file (e.g: `README.md`) containing nested bullets (use asterisk and 2 spaces)
* Run `python tocer.py <toc-file>` (e.g: `python tocer.py README.md`).

# Expected result

* Every bullet item in your TOC file will turn into link, unless it is already a link.
* If the documents refered by the links are not exist, they will be created.

# Testing

* Run `test.sh`

# FAQ

## I have run tocer.py. Can I update the TOC and re run tocer.py?

Yes you can.