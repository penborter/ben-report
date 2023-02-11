---
layout: post
title: Why are lower jersey numbers more common?
description: Why are lower jersey numbers more common?
summary: Trends in NBA jersey numbers over time
tags: [nba, data]
photoloc: /assets/posts/jerseys/
blurb: NBA Jersey numbers go through 20-year cycles of popularity. Currently we're in a "low" cycle and I'm not sure why.
---

Before we get too far, be warned that I don't actually have the answer to the title question. If I figure it out, though, I'll be sure to write about it.

Basketball Reference has a season-by-season [uniform number index](https://www.basketball-reference.com/leagues/NBA_2020_numbers.html), and I found [this data set](https://www.kaggle.com/kaushikrv/nbajerseynumbers) that collected the totals for each jersey number since 1950. Based on the data, I wanted to see if: (1) jersey number trends have changed over time, and (2) if I could figure out the reasons why.
1. They have.
2. I haven't so far.

I'll dive into more analysis in a later post, but for now here's a graph of the most popular jersey number each year:

{% include picture.html
   file="numbershistory.png"
   class="wide"
%}

Uniform numbers in sports are important - they either represent a player's personal identity and branding (e.g in the NBA), or they represent the player's position (e.g. in Rugby, and sort of in Football). NBA players have often built their personal brand around their jersey number. Quick - what number is Michael Jordan? Chris Paul? [Andrei Kirilenko](https://athletenicknames.club/andrei-kirilenko-ak-47/)?

My initial guess was that popular jerseys would lag behind star players of a given era as younger players choose a number to match their idol. Number 23 jerseys would pick up toward the end of Jordan's career. Number 32 and 33 would increase as Magic and Bird retire. Number 6 would take off after Bill Russell bowed out. But this isn't really the case - the effect, if any, is too small to make out.

It looks like there are ~20-year cycles that uniform numbers go through, where the most popular numbers are clustered in a relatively tight 10-digit range. The effect is much stronger than I was expecting - almost within 2 years in the mid-90s higher numbers went out of style and were replaced with numbers 5 and below.

All of this leaves us with a few questions:  
*Why are low jersey numbers now more common?*  
*Why did they become so popular at the turn of the millennium?*  
*What happened in the 80s and 90s?*  
*What explains the three clear periods of jersey number trends?*

I'm still not sure. I'll write up a more in-depth post about data prep and detailed analysis relating to college restrictions, retired numbers, etc, and hopefully we can come up with more answers. In the meantime, here are a few player logos that include jersey numbers below - bonus points if you can guess all of them. Names are listed below[^1].

{% include picture.html
   file="logos.png"
   caption="Player logos that include numbers. Weirdly, they're mostly point guards."
%}

[^1]: Clockwise from top left: Damian Lillard, Penny Hardaway, Tracy McGrady, Kyrie Irving, Stephen Curry, Chris Paul, Allen Iverson, and Kawhi Leonard.
