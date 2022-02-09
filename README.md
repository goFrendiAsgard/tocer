# Tocer

Create nested documents based on item list.

From this `README.md`:

```bash
mkdir testDir
cd testDir

# Create a README.md
cat <<EOF > README.md
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
python ~/tocer/tocer.py
```

Into this directory structure:

```
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

<details>
<summary>
with new <code>README.md</code>:
</summary>

```
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
</details>

<details>
<summary>
and respective sub documents:
</summary>

```
❯ cat pokemon/kanto/starter/README.md
<!--startTocHeader-->
[🏠](../../../README.md) > [Pokemon](../../README.md) > [Kanto](../README.md)
# Starter
<!--endTocHeader-->
TODO: Write about `Starter`
<!--startTocSubtopic-->
# Sub-topics
* [Bulbasaur](bulbasaur.md)
* [Squirtle](squirtle.md)
* [Charmender](charmender.md)
<!--endTocSubtopic-->
```
</details>


# Why

Because any good documentation started with a TOC (or at least I think so).

# Prerequisites

* Python
* just that, nothing else

# How to install

```bash
git clone git@github.com:state-alchemists/tocer.git ${HOME}/tocer
```

# How to use

* Create a TOC file (e.g: `README.md`) containing nested bullets flanked by two HTML tags: `<!--startToc>` and `<!--endToc>`
* Run `python tocer.py <toc-file>` (e.g: `python tocer.py README.md`).

# Expected result

* Every bullet item between `<!--startToc>` and `<!--endToc>` in your TOC file will be turned into link, unless it already is.
* If the documents refered by the links are not exist, they will be created.

# Testing

* Run `test.sh`

# FAQ

## I have run tocer. Can I add some items to the TOC and re run it?

Yes you can. `tocer` will turn your new items into links and create respective documents.

## I modify existing item's position and caption and re run tocer. Is that okay?

Yes it is okay. `tocer` will update all `title`, `breadcrumbs`, and `subtopics` to match your new structure.

## Great job. Can I contribute?

Sure you can do:

* Create pull request
* Open issue
* [Donate](https://www.paypal.com/paypalme/gofrendi). Please let me know a few things if you donate:
  * How do you find this project useful?
  * Can I put your username/identity in this README file as contributor?
  * Is there any feature you want?
  * Leave me your email address, so that I can reply to you.