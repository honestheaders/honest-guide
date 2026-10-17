---
title: Copy a web page table into a spreadsheet with XPath and the Console, no scraper needed
description: A short DevTools snippet that turns table rows into tab-separated text you can paste into a spreadsheet, how relative XPath per column works, and when you should not collect data from a page at all.
updated: 2026-10-18
---

Chrome's Console can do this for you: find the rows with one XPath, read each column with a short XPath that starts from that row, join the cells with tab characters, and send the result to your clipboard with `copy()`. About ten lines of JavaScript, no extension and no library. Paste the text into a spreadsheet and the columns line up.

## The snippet

This version assumes an HTML `<table>` whose body rows hold `<td>` cells. Change the three column paths to fit your page.

```js
const rows = document.evaluate(
  "//table//tr[td]", document, null,
  XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null
);
const cols = ["./td[1]", "./td[2]", ".//a/@href"];
const out = [];
for (let i = 0; i < rows.snapshotLength; i++) {
  const row = rows.snapshotItem(i);
  const cells = cols.map(c =>
    document.evaluate("string(" + c + ")", row, null,
      XPathResult.STRING_TYPE, null)
      .stringValue.trim().replace(/\s+/g, " ")
  );
  out.push(cells.join("\t"));
}
copy(out.join("\n"));
```

Run it in the Console, then paste into a cell in your spreadsheet app. If the paste lands in one column, check that the tabs survived: run `console.log(out[0])` and look for the gaps between cells.

## Why each column path starts with a dot

The first XPath finds the rows. Each column path is then evaluated with one row as the context node, and the leading dot says "start from here". MDN's `document.evaluate()` page makes the same point with its `.//h2` example: with the dot, the query starts from the context node you passed, and without it (`//h2`) the query "would start from the root node (`html`)". For a table, that is the difference between "the first cell of this row" and "the first cell on the whole page", repeated for every row.

Here is how the three paths in the snippet read:

| Path | Meaning |
|---|---|
| `./td[1]` | The first `td` child of the current row |
| `./td[2]` | The second `td` child of the current row |
| `.//a/@href` | The `href` attribute of any link inside the current row |

## Why each path is wrapped in `string()`

MDN's page on the XPath `string()` function says that for a node-set, the string value of the first node in the set is returned. So `string(./td[2])` gives you the text of the cell, and `string(.//a/@href)` gives you the first link's address, or an empty string if the row has no link. The snippet asks for `XPathResult.STRING_TYPE` and reads `stringValue`, which is how MDN's XPath guide says to read a string result.

The `.trim().replace(/\s+/g, " ")` part is plain JavaScript housekeeping. It strips line breaks and runs of spaces so a cell cannot break the one-row-per-line layout.

## When the rows are not in a `<table>`

Many pages build lists out of `<div>` or `<li>` elements. The idea is the same: write one XPath that matches exactly one node per record, then write relative paths for the fields. For example:

```js
// rows:   //ul[@class="results"]/li
// fields: ./h3        ./span[@class="price"]        .//a/@href
```

Count your rows first with `$x('//ul[@class="results"]/li').length`. Chrome's Console Utilities reference says `$x(path)` returns an array of the DOM elements that match, so the length is your record count. If the number is not what you see on the screen, fix the row path before touching the columns. Our guide to [testing an XPath in Chrome DevTools](/honest-guide/en/test-xpath-in-chrome-devtools/) covers the `//li[1]` trap that often causes a wrong count.

## Check the snapshot when the page changes

The snippet uses a snapshot result. MDN notes that snapshots do not change with document mutations, so a snapshot "may not correspond to the current document". If the page loads more rows as you scroll, run the snippet again after they appear, and do not reuse an old snapshot.

## Before you collect data from a page

Being able to read a page with XPath does not mean you may copy it in bulk. Check the site's terms of use first. Also look at its `robots.txt`, but know what that file is: Google's documentation says it tells crawlers which URLs they can access, and that it is "not a mechanism for keeping a web page out of Google". It is not access control either, because crawlers have to choose to follow it. So a missing `Disallow` line is not permission by itself; the site's terms still apply, and a `Disallow` line for the pages you want is a reason to stop and ask.

If you want to try the paths without touching a live page, paste a saved snippet of HTML into our free [XPath tester](/honest-guide/en/tools/xpath-tester/). To pick one element and get every similar one as a table without writing code, our free Honest Scraper extension does that on the page:

{{product:scraper}}

## Who this is not for

Skip this snippet if the page shows its data in a canvas, an image or a PDF viewer, because there is no DOM text to read. If the rows load only when you scroll or after you sign in, the Console will only see what is on the screen at that moment, so you will need to expand the page first. And if the site forbids copying its data, or the data is personal information about other people, do not collect it.

## Sources (checked 2026-10-18)

- MDN, `Document.evaluate()` (signature, result type constants, `.//h2` relative-path note): <https://developer.mozilla.org/docs/Web/API/Document/evaluate>
- MDN, Introduction to using XPath in JavaScript (snapshots, `snapshotItem`, `stringValue` for `STRING_TYPE`): <https://developer.mozilla.org/en-US/docs/Web/XML/XPath/Guides/Introduction_to_using_XPath_in_JavaScript>
- MDN, XPath `string()` (node-set returns the first node's string value; French version of the page): <https://developer.mozilla.org/fr/docs/Web/XML/XPath/Reference/Functions/string>
- Chrome for Developers, Console Utilities API reference (`$x(path [, startNode])`, `copy(object)`): <https://developer.chrome.com/docs/devtools/console/utilities>
- Google Search Central, Introduction to robots.txt (what it is for, and that it is not a way to keep a page out of Google or an access control): <https://developers.google.com/search/docs/crawling-indexing/robots/intro>
