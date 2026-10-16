---
title: Test an XPath in Chrome DevTools: $x(), Elements search and document.evaluate
description: Three ways to try an XPath on a live page in Chrome, with copy-paste examples for text, attributes and the nth item, plus the one mistake that makes //li[1] return many nodes.
updated: 2026-10-17
---

Open DevTools, switch to Console, and type `$x("//h2")`. You get an array of every `<h2>` on the page, and if the array is empty, your XPath matched nothing. That one call is the fastest way to test an XPath in Chrome. Two other routes exist: the search bar in the Elements panel, and `document.evaluate()` in your own script.

## Route 1: `$x()` in the Console

Chrome's Console Utilities reference defines it as `$x(path [, startNode])`. It "returns an array of DOM elements that match the given XPath expression." The reference's own examples are `$x("//p")`, which returns all `<p>` elements, and `$x("//p[a]")`, which returns the `<p>` elements that contain `<a>` elements.

The optional second argument, `startNode`, is the element or node to search from. Pass one when you want to test an expression relative to a single block of the page.

## Route 2: the search bar in the Elements panel

Focus the Elements panel and press Ctrl+F (Cmd+F on macOS). Chrome's DevTools documentation says you can search the DOM tree by string, CSS selector, or XPath selector. Type an XPath such as `//h2` into that bar, and the search runs against the tree, so you stay in the Elements panel instead of reading an array.

## Route 3: `document.evaluate()`

This is the call your own code will use. Its signature on MDN is `evaluate(xpathExpression, contextNode, namespaceResolver, resultType, result)`. For an HTML page, pass `document` as the context node and `null` as the resolver. MDN says `null` is common for HTML documents or when no namespace prefixes are used.

```js
const snap = document.evaluate(
  "//h2", document, null,
  XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null
);
for (let i = 0; i < snap.snapshotLength; i++) {
  console.log(snap.snapshotItem(i).textContent);
}
```

`ORDERED_NODE_SNAPSHOT_TYPE` returns a list of matched nodes in document order, read with `snapshotLength` and `snapshotItem(i)`. MDN notes that a snapshot stays valid if the document changes, though it may then no longer match the current page. If you only need the first match, `XPathResult.FIRST_ORDERED_NODE_TYPE` gives you `singleNodeValue`, which is `null` when nothing matches.

MDN also advises starting from a context node with a leading dot, as in `document.evaluate(".//h2", document.body, ...)`. Without the dot, `//h2` starts from the root and is more wasteful.

## Examples you can paste into `$x()`

| You want | XPath |
|---|---|
| Every link | `//a` |
| Links with a given attribute value | `//a[@rel="next"]` |
| Elements whose text contains a word | `//li[contains(., "Sale")]` |
| The first item of each list | `//ul/li[1]` |
| The third item of the whole page | `(//li)[3]` |
| The text itself, not the element | `//h2/text()` |

A few notes on reading these:

- The W3C XPath 1.0 spec gives `para[@type="warning"]` as "all `para` children of the context node that have a `type` attribute with value `warning`". Attribute tests in square brackets work the same way on any tag.
- `contains()` is defined in the spec as returning true "if the first argument string contains the second argument string". A dot as the first argument means the element's own text. The spec defines string equality as the same sequence of characters, and the MDN page for `contains` does not mention case, so test your capitalization on the real page.
- `text()` selects text nodes, per the spec, so you get the text itself rather than the element around it.
- Positions start at 1: the spec says "The first position is 1."

## The `//li[1]` mistake

The spec has a note on this: `//para[1]` "does not mean the same as" `/descendant::para[1]`, and it selects "all descendant `para` elements that are the first `para` children of their parents". So on a page with five lists, `//li[1]` returns five elements, one per list. If you wanted exactly one, wrap the path in parentheses first: `(//li)[1]`. The table above uses that form for `(//li)[3]`.

When an XPath works in the Console but fails in your script, check these two things first:

1. You passed a context node and forgot the leading dot, so a path meant to be relative started from the root.
2. The script ran before the element was in the page. Run the test again once the page has finished rendering.

## Skip the Console

If you would rather type an XPath and see matches highlighted, we built a free [XPath tester](/honest-guide/en/tools/xpath-tester/) that runs in your browser. If you also work with request headers in DevTools, see [how to change HTTP headers in Chrome](/honest-guide/en/modify-http-headers-in-chrome/).

{{product:scraper}}

## Who this is not for

If you need to scrape pages that load their content late or sit behind a login, a one-line query will not be enough on its own. And if the page you are testing belongs to someone else, check its terms of use and robots.txt before you collect data from it.

## Sources (checked 2026-10-17)

- Chrome for Developers, Console Utilities API reference (`$x(path [, startNode])`): <https://developer.chrome.com/docs/devtools/console/utilities>
- Chrome for Developers, DOM (searching the DOM tree by string, CSS selector, or XPath): <https://developer.chrome.com/docs/devtools/dom/>
- MDN, `Document.evaluate()` (signature, `null` resolver for HTML, result types, leading-dot example): <https://developer.mozilla.org/en-US/docs/Web/API/Document/evaluate>
- MDN, Introduction to using XPath in JavaScript (result types and how to read them): <https://developer.mozilla.org/en-US/docs/Web/XML/XPath/Guides/Introduction_to_using_XPath_in_JavaScript>
- MDN, XPath `contains()`: <https://developer.mozilla.org/en-US/docs/Web/XML/XPath/Reference/Functions/contains>
- W3C, XML Path Language (XPath) Version 1.0 (abbreviated syntax, `[1]` position, `contains`): <https://www.w3.org/TR/1999/REC-xpath-19991116/>
