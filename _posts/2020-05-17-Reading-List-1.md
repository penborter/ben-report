---
layout: post
title: Scraping Goodreads - Reading list 1
description: Scraping book info from Goodreads using Python
summary: Scraping book info from Goodreads using Python
tags: [site, python, reading, tutorial]
photoloc: /assets/posts/readingList
blurb: Part 1 of creating a Reading List - How to use BeautifulSoup and ISBNs to scrape and collate book information from Goodreads. 
---

This is first part of two ([Part 2](/posts/reading-list-2)) outlining how I created and populated my [Reading List](/books) page. The final product is mostly automated, requiring only ISBNs and the reading year for each book to generate a page with the cover art and relevant details for each book. 

Here is an overview of the process:
1. Scraping Goodreads with Python using books' ISBNs, collecting book data and a folder full of book cover images.
2. Generating a Reading List page like [mine](/books) using Liquid tags, and arranging the page using CSS Grid.

## Scraping the web
There are heaps of *web scraping with Python* tutorials online. I won't go into too much detail here - writing this tutorial is probably more for me to lock in the process than to break new ground in the web scraping space, but hopefully it can provide some value. 

HTML forms the basis of all web pages. At the most basic level, it's essentially just a bunch of containers. Web scraping is the process of looking through these containers to find and retrieve the information inside them. We can use purpose-built Python libraries to automate and simplify this process, so that we can retreive information from a large number of websites. 

[Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) is one of those Python libraries for reading HTML files, like websites. The BeautifulSoup `find` method allows us to find and return the specific HTML element we're looking for, and the `contents` method returns the contents of that element, as you'd expect. Before we can start writing code, we need to make a manual inspection of the website we're going to be scraping. 

## Inspecting the scraping site

{% include picture.html
   file="goodreads_base.png"
   class="wide"
%}

Above is the goodreads website for the next book on my reading list: [The Anarchy](https://www.goodreads.com/book/show/42972023-the-anarchy), by William Dalrymple. The Goodreads website is well structured for web scraping - every container has a clearly named `id` or `itemprop` attribute. If you want to pull extra info for each book, you just have to inspect any book's page to find the relevant tag. If we inspect the heading element for the book title, we can see the relevant heading tag has an ID of `bookTitle`. Makes sense. We can use the same idea to find attributes for the all of the other pieces of information that we want. 

{% include picture.html
   file="goodreads_highlight.png"
   class="wide"
%}

## Looping through elements

Now that we've inspected the Goodreads book page, we can use BeatifulSoup and Python do the work of inspecting and reading for us. In this case, we can use the `id` and `itemprop` attributes we found earlier to specify the elements we want to return. As you'd expect, the `contents` method returns the contents of the specified element. 


Putting it all together, here's our Goodreads scraping function:
```python
# Function that takes the book ISBN and returns key info
def goodreadsInfo(isbn):
    
    goodreadsURL = "https://www.goodreads.com/book/isbn/"
    r = get(goodreadsURL + isbn)
    
    if r:
        soup = BeautifulSoup(r.content, 'html.parser')

        title = soup.find(id="bookTitle")
        title = title.contents[0].strip()

        author = soup.find("span",itemprop="name")
        author = author.contents[0]
        
        rating = soup.find(itemprop="ratingValue")
        rating = float(rating.contents[0].strip())
        
        pagenums = soup.find(itemprop="numberOfPages")
        pagenums = int(pagenums.contents[0].split()[0])
        
        # Gets the url of the cover photo and saves it to disk in coverPath directory
        cover = soup.find(id="coverImage")["src"] 
        coverPath = f"/Users/BenPorter/website/assets/books/{title}.jpg"
        urllib.request.urlretrieve(cover,coverPath)
        print("Saved cover photo")

        bookInfo = [title, author, rating, pagenums]
        return bookInfo
    
    else:
        print("Error: Book not found")
```

## Next steps
We can use this function to generate a YAML file that contains our book info. YAML is the data structure used for Jekyll, to be stored in our site's `/_data` directory. It will power the reading list page we generate in [Part 2](/posts/reading-list-2). We can also run this script when new books' ISBNs are added to our master list, and it will add to our database. The full script is on [Github]().

I think the next evolution of this process will be to use the [Goodreads API](https://www.goodreads.com/api/index), which should make things a bit more intuitive - requiring a book title rather than an ISBN. It's also worth considering the limitations of ISBNs - there are different ISBNs for different editions of a book, and some very new eBooks and very old books don't have ISBNs for us to use at all. Some more interesting discussion can be found about it [here](https://en.wikipedia.org/wiki/Wikipedia:ISBN#Uses_and_limitations_of_ISBNs) and [here](https://macwright.org/2017/12/11/indieweb-reading.html).
