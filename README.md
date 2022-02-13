# Tocer

Create nested documents based on item list.

From this `README.md`:

````md
# Legendary Gods

These bullet list won't be rendered into TOC:

* Sliffer The Sky Dragon
* Obelisk The Tormentor
* Winged Dragon of Ra

# Pokemons

These bullet list will be rendered into TOC:

<!--startToc-->
* Pokemon
   * Kanto
     * Starter
       * Bulbasaur
       * Squirtle
       * Charmender
   * Johto
* Digimon
  * Agumon
  * Gabumon
<!--endToc-->


# Code Example

After running `python ~/tocer/tocer.py`, several sub-documents will be created:

<!--startCode-->
```bash
echo "🐶 Show directory structure"
tree

echo "🐶 Content of pokemon/kanto/README.md"
cat pokemon/kanto/README.md
```
<!--endCode-->

> Note: Currently only support bash
````

<details>
<summary>
<b>Into Nested Documents</b>
</summary>

`````md
# Legendary Gods

These bullet list won't be rendered into TOC:

* Sliffer The Sky Dragon
* Obelisk The Tormentor
* Winged Dragon of Ra

# Pokemons

These bullet list will be rendered into TOC:

<!--startToc-->
* [Pokemon](pokemon/README.md)
   * [Kanto](pokemon/kanto/README.md)
     * [Starter](pokemon/kanto/starter/README.md)
       * [Bulbasaur](pokemon/kanto/starter/bulbasaur.md)
       * [Squirtle](pokemon/kanto/starter/squirtle.md)
       * [Charmender](pokemon/kanto/starter/charmender.md)
   * [Johto](pokemon/johto.md)
* [Digimon](digimon/README.md)
  * [Agumon](digimon/agumon.md)
  * [Gabumon](digimon/gabumon.md)
<!--endToc-->


# Code Example

After running `python ~/tocer/tocer.py`, several sub-documents will be created:

<!--startCode-->
```bash
echo "🐶 Show directory structure"
tree

echo "🐶 Content of pokemon/kanto/README.md"
cat pokemon/kanto/README.md
```

````
🐶 Show directory structure
.
├── README.md
├── digimon
│   ├── README.md
│   ├── agumon.md
│   └── gabumon.md
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

4 directories, 11 files
🐶 Content of pokemon/kanto/README.md
<!--startTocheader-->
[🏠](../../README.md) > [Pokemon](../README.md)
# Kanto
<!--endTocheader-->

TODO: Write about `Kanto`

<!--startTocsubtopic-->
# Sub-topics
* [Starter](starter/README.md)
  * [Bulbasaur](starter/bulbasaur.md)
  * [Squirtle](starter/squirtle.md)
  * [Charmender](starter/charmender.md)
<!--endTocsubtopic-->
````
<!--endCode-->

> Note: Currently only support bash
`````
</details>


# Try It Yourself

```bash
echo "🐶 Preparing Demo"
mkdir -p ~/testTocerPlayground
cd ~/testTocerPlayground
cp ~/tocer/sample-template.md README.md

echo "🐶 Original README.md content:"
cat README.md

echo "🐶 Running Tocer"
python ~/tocer/tocer.py

echo "🐶 New README.md content:"
cat README.md
```

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