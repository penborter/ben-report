---
layout: post
title: Liquid tags and Jekyll - Reading list 2
description: Using Jekyll to create a reading list page
summary: Using Jekyll to create a reading list page
tags: [site, jekyll, reading, tutorial]
photoloc: /assets/posts/readingList
blurb: Part 2 of creating a Reading List - How to use Jekyll and CSS to create a template page, then populate it with book info using Liquid tags. 
---

This is the second part of our two ([Part 1](/posts/reading-list-1)) to auto-generate a reading list page using scraped data, liquid tags, and some CSS. Now we have our book data, we can create a frame using Jekyll, Liquid tags and CSS, and populate it with our book info. 

## Accessing the data

[Liquid](https://shopify.github.io/liquid/) is a template language created by Shopify that is [incorporated into Jekyll](https://jekyllrb.com/docs/liquid/). It allows us perform logic statements and output content using curly braces. The YAML file from the data we scraped in [Part 1](/posts/reading-list-1) will serve as the content for the reading page. We're going to  use Liquid to loop through the data stored in reading.yml and generate a reading page using a Jekyll template. The full Jekyll template and CSS is available on [GitHub](). 

First we want to loop through each of the years in our reading data and create a div for metadata, and a container for the books read that year. Liquid allows us to create a for loop in the Jekyll HTML template, looping through entries in our YAML file, stored in the site's ```_data``` folder. 

```html
{{ "{%" }} for entry in site.data.reading.list %}
   <div class="year-meta">
     <h3 class="year">{{ "{{" }}  entry.year }}</h3>
     <span class="number">{{ "{{" }}  entry.books | size }} books</span>
   </div>

   <div class="year-container">
```
## Arranging our bookshelf

Without any styling, our populated template is a mess. The book covers are different sizes. 

We're going to use CSS Grid to arrange the information in a more function and beautiful way. CSS Grid allows you to define a grid template. In our case, we only need to define the columns as the rows will auto-generate based on their contents. The grid template is defined in the parent container - the one that will hold each of the elements arranged in the grid. ```1fr``` means a column (or row) with width one equal part of the total element width - three columns with width ```1fr``` means our parent element will be split into three equal-width columns.

```scss
.year-container {
   display: grid;
   // Three equal-width columns with a gap in between
   grid-template-columns: 1fr 1fr 1fr;
   grid-gap: 3em;
 }
```

As this is a fairly simple grid structure, we don't need to define any grid behaviour for the child elements - we want them to just fill in the grid, one element at a time. We can also add some formatting for the book title and author, and we end up with something like this.

## Finishing touches

Finally, some finishing touches to make the book covers a bit more dynamic. These changes won't affect the functionality of the page, but in my opinion they add interest and make the covers better match other site elements like code blocks and the nav bar. 

```scss
 .book-box figure {
   margin: 0;
   transition: all 0.3s cubic-bezier(0.25, 0.45, 0.45, 0.95);
 }   
 .book-box figure:hover {
   transform: scale(1.02);
 }

 .book-box img {
   border-radius: 4px;
   box-shadow: 0px 3px 8px #aaa;
 }
```

We're going to add a shadow to the covers, and a subtle animation on mouse-over to add some motion. I found that rounding the corners of the books also makes them look more like actual book covers - I guess they're not perfectly cut corners in real life either.

With these touches in place, our reading page looks a lot better. It's nice to see the covers arranged in front out, side by side, in this time where [book covers are dying](https://craigmod.com/journal/hack_the_cover/). Even a packed bookshelf doesn't have the same effect. Now all that's left is to keep reading and add to it. See my complete reading list [here](/books).

{% include picture.html
   file="final_list.png"
   class="wide"
%}
