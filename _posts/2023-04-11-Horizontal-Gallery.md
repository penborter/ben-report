---
layout: post
title: How to make a horizontal gallery layout with CSS
tags: [site, learning, photography]
photoloc: /assets/posts/horizontal
render_with_liquid: false
toc: true
---

I wanted to put together a quick guide for the horizontal photo gallery layout I use for the galleries on this site (e.g. [Europe 2022](https://ben.report/photos/euro)). It comes baked in to the [Stretch](https://stretch.ben.report/) jekyll theme, too.

I'll split this into two parts:
1. Using a Jekyll template to populate a gallery
2. Using CSS to get the populated gallery to behave the way we want

If you're not using Jekyll then I recommend skipping straight to the [CSS section](/posts/horizontal-gallery#css-layout).


## Jekyll Template

We're using a layout called [`photo.html`](https://github.com/penborter/ben-report/blob/main/_layouts/photo.html), which is a basic liquid template that loops through the photos in the gallery, pulls out the URL, caption, and alt text. It allows you to include an intro paragraph at the start of the gallery, which scrolls the same way. 

First we get the data from `photos.yml` in the site's `_data` folder. This will probably be different depending on how your site's data is structured.

```liquid
{% assign gallery = site.data.photos[page.photo_id] %}
{% assign gallery_size = gallery.images.size %}
```

The whole gallery is then wrapped in a div called `horizontal-gallery-wrapper`. Within that div, there are two parts: the initial "meta" paragraph, and then the liquid loop to generate html tags for each image in the gallery. For each image in the gallery, we can fill out an `image-wrapper` div with the url, title, image caption, and alt text.

```html
<div class="horizontal-gallery-wrapper">

  <div class="gallery-meta">
    <div>
      <h1>{{ page.title }}</h1>
      <p>There are {{ gallery_size }} photos in this set. Photos scroll horizontally (hold Shift and scroll with a mousewheel). 👉</p>
    </div>
  </div>

  {% for image in gallery.images %}
    <div class="image-wrapper">
      <a href="{{ gallery.imagefolder }}/{{ image.name }}"  title="{{ image.text}}">
        <div class="image-caption">{{ image.text }}</div>
        <img class="img-gallery" src="{{ gallery.imagefolder }}/{{ image.thumb }}" alt="{{ image.text }}" loading="lazy">
      </a>
    </div>
  {% endfor %}
</div>
```
## CSS Layout
Fundamentally, we have a wrapper div––which enables the horizontal scroll––containing a set of divs (or other tags) for each of the images or products or projects we want to display.

```html
<div class="horizontal-gallery-wrapper">
  <div class="wrapper" id="img-1">
  <div class="wrapper" id="img-2">
  ...
  <div class="wrapper" id="img-N">
</div>
```

Firstly the main wrapper, where we set the x-axis overflow to scroll, and we force the content inside not to wrap, i.e. extend as far as needed off to the right of the page. We also add a bit of padding, include a large amount of left padding in this case so that the gallery starts to the right of the menu sidebar.

```scss
.horizontal-gallery-wrapper {
  overflow-x: scroll;
  overflow-y: hidden;
  white-space: nowrap;
  padding: 10px 0;
  padding-left: 13em;
}
```

For each image (including the intro paragraph) we have an `image-wrapper` div. The contents of the inner divs is not important, as long as they each have `height: 100%`. Also note that if you're putting an `<img>` tag inside the `div`, you need to set `height:100%` for that element as well. We can add a bit of margin to leave a gap between each of the images; this is also where we could add rounded borders or a box shadow to each of the images, if we wanted to.

I've also included a `gallery-meta` div, which contains the intro paragraph gallery title. Otherwise, it behaves behave basically the same as the `image-wrapper` divs. It does need some additional formatting to constrain its size, and to allow the text to display and wrap correctly. Width and padding are flexible, but `vertical-align: top` and `white-space: normal` are required. 

```scss
.image-wrapper, .gallery-meta {
  display: inline-block;
  height: 100%;
  margin: 0 4px;
}

.gallery-meta {
  width: 500px;
  vertical-align: top;
  white-space: normal;
  padding: 4rem;
}
```

If we want to include a caption for each image (which we did in the HTML in [section 1](/posts/horizontal-gallery#jekyll-template)), we will need to format that too. The below css rules hide the caption by default, revealing it whenever the image itself is hovered over. In this arrangement, captions will always appear in the bottom left of the screen, and aren't tied to the location of the associated image. If you want them to move with the image, you can add `position: relative` to their parent element, in this case the `<a>` tag actually linking to the image.

```scss
.image-caption {
  position: absolute;
  left: 2em;
  bottom: 1.5em;
  display: none;

  backdrop-filter: blur(5px);
  color: #fff;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 3px;
  padding: 0.3em;
}

.image-wrapper:hover .image-caption {
  display: block;
}
```

## Narrow Screens

For narrow screen widths or vertically oriented screens, obviously the horizontal scroll doesn't make sense. In those circumstances I just revert `horizontal-gallery-wrapper` to a column-direction flex box. 

```css
@media screen and (max-width: 1000px)
.horizontal-gallery-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  row-gap: 1em;
}
```

## Wrapping Up

That's all there is to it! No JS required, just forcing the page contents to extend off to the right and telling the page to scroll in that direction. This effect works well with a static sidebar, where the photos can scroll under the sidebar and off the screen to the left. 

Other finishing touches could include: adding a page footer into the `gallery-meta` div, and including a liquid content tag in that same div to allow for a custom blurb for each gallery. 

See some live examples [here](https://ben.report/photos), or at the **PHOTOS** link in the navbar <span class="narrow-remove">on the left.</span><span class="narrow-show">up top.</span>