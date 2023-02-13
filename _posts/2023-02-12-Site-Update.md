---
layout: post
title: New Site Layout
tags: [site]
photoloc: /assets/posts/layout/
---

## New URL
Firstly, you might note that the url of this website has changed, from `penborter.com` to `ben.report`. Fewer characters, maybe a bit more anonymous, definitely more fun. The old url will redirect to here from now on. All of the content is the same as before, and the source of the website itself is still available on [github](https://github.com/penborter/ben_report). The RSS feed is now available [here](/feed.xml).

## Redesign
I spent the summer break working on a Jekyll theme to eventually convert my website to. The theme is called Stretch - an example is [available online](https://stretch.ben.report). I've finally gotten around to moving the existing site over to the new theme. I'll make the old theme available at a subdomain when I have the time. Below are some before and after screenshots.

**Before:**
{% include picture.html
   class="wide"
   file="before.png"
%}

**After:**
{% include picture.html
   class="wide"
   file="after.png"
%}

It includes a couple of fun features, like a `list.html` layout that allows you to easily create landing pages for the [collections](https://jekyllrb.com/docs/collections/) in your site, or a two-colour scheme that automatically generates all of the site colours from two hex codes. I might update the colours I've chosen from time to time, probably moving back towards more neutral choices. For now we're pairing a very light orange `#FFF3EC` with a deep teal `#237A82`. 

At the moment, the only Javascript in action on the site is used to swap between dark and light mode. 
The sidebar is there (instead of nav in the header) because I thought it was more fun for it to be parallel to the main scroll direction. There's more space for nav elements with this orientation, so you can quickly point visitors to the more interesting parts of the site in the secondary nav, rather than just the main categories. The sidebar also interacts in a more interesting way with the [photo galleries](/photos), which scroll horizontally. 



