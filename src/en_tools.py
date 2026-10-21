"""Free tools for the English section (/en/tools/...). They run only in the visitor's browser.
Every rule shown by a tool comes from the sources listed on its page (checked dates included)."""

TOOLS = [
    ("php-version-checker", "PHP version checker (CVE-2026-109618/109619)",
     "Paste php -v or an X-Powered-By header. See if your PHP is at or above the 21 October 2026 fixed release for its branch, and which interim settings php.ini has."),
    ("security-headers-checker", "Security headers checker (paste your headers)",
     "Paste response headers from DevTools or curl. See which of the 7 recommended security headers are missing and which 5 old headers to remove."),
    ("set-cookie-builder", "Set-Cookie builder and checker",
     "Build a Set-Cookie header with Secure, HttpOnly, SameSite, Partitioned and prefixes, and see which combinations browsers reject."),
    ("cookie-converter", "Cookie JSON to cookies.txt converter (both ways)",
     "Paste a cookie editor's JSON export and get a Netscape cookies.txt for curl or wget, or turn a cookies.txt back into JSON. Runs only in your browser."),
    ("xpath-tester", "XPath tester (paste HTML, see what matches)",
     "Paste some HTML and an XPath expression. See the match count, the text of each match, and copy the results, one per line."),
]

TOOL_CSS = ('.tool textarea,.tool input[type=text],.tool input[type=number],.tool select{display:block;width:100%;font:15px ui-monospace,Menlo,Consolas,monospace;padding:10px;margin-top:4px;border:1px solid #bbb;border-radius:6px;background:#fff}'
            '.tool textarea{min-height:180px}.tool .row{display:flex;flex-wrap:wrap;gap:8px 16px}.tool .row label{display:flex;align-items:center;gap:6px;font-size:15px;color:#222}'
            '.btn{font:600 15px system-ui,sans-serif;background:#1f4e79;color:#fff;border:0;border-radius:8px;padding:10px 16px;cursor:pointer}.btn.ghost{background:#fff;color:#1f4e79;border:1px solid #1f4e79}'
            '.res{list-style:none;padding:0;margin:8px 0}.res li{background:#fff;border:1px solid #ddd;border-radius:8px;padding:8px 12px;margin:6px 0;font-size:15px}.res li b{display:block}'
            '.res .ok{border-left:5px solid #2e7d4f}.res .ng{border-left:5px solid #b3261e}.res .info{border-left:5px solid #b38600}.score{font-size:18px;font-weight:700;margin:12px 0 4px}'
            'main code{overflow-wrap:anywhere}.res li{overflow-wrap:anywhere}#out{font:15px ui-monospace,Menlo,Consolas,monospace;background:#f1f1ec;padding:12px;border-radius:8px;overflow-wrap:anywhere}')

CHECKER = r'''<h1>Security headers checker</h1>
<div class="answer"><p class="ah">HOW IT WORKS</p><p>Paste the response headers of one page. The checker looks for the 7 headers we recommend adding and the 5 we recommend removing, and says what to change. It runs only in your browser: nothing you paste is sent anywhere.</p></div>
<div class="tool"><label for="h">Response headers (from DevTools or <code>curl -sI https://your-site.example</code>)</label>
<textarea id="h" spellcheck="false" placeholder="HTTP/2 200&#10;content-type: text/html&#10;strict-transport-security: max-age=31536000"></textarea>
<div class="row"><button class="btn" id="go" type="button">Check headers</button><button class="btn ghost" id="ex" type="button">Try an example</button></div></div>
<div id="r" aria-live="polite"></div>
<h2 id="where">Where to copy the headers from</h2>
<ul><li><b>Chrome DevTools:</b> Network panel, reload, click the first (document) request, then in <b>Response Headers</b> turn on <b>Raw</b> and copy.</li>
<li><b>Command line:</b> <code>curl -sI https://your-site.example</code> prints only the headers.</li></ul>
<p>What each header does, and example values: <a href="BASE/security-headers-checklist/">Security headers checklist: the 7 to add and the 5 to remove</a>.</p>
<h2 id="not-for">Who this is not for</h2>
<ul><li>This only looks at whether headers are present and at a few obvious values. It does not judge whether your Content-Security-Policy is strict enough, and it is not a security audit.</li>
<li>If you want a site scanned from the internet by URL, Mozilla's HTTP Observatory does that.</li></ul>
<h2 id="sources">Sources (checked 2026-10-12)</h2>
<ul><li>OWASP HTTP Headers Cheat Sheet: <a href="https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html">https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html</a></li>
<li>MDN, Strict-Transport-Security: <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security">https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security</a></li>
<li>MDN, X-Content-Type-Options: <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Content-Type-Options">https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Content-Type-Options</a></li></ul>
<script>
(function(){
var EX="HTTP/2 200\nserver: nginx/1.24.0\ncontent-type: text/html; charset=utf-8\nx-powered-by: Express\nx-frame-options: SAMEORIGIN\nx-xss-protection: 1; mode=block\nstrict-transport-security: max-age=31536000; includeSubDomains\nreferrer-policy: strict-origin-when-cross-origin";
function parse(t){var h={},L=t.split(/\r?\n/).map(function(s){return s.trim()}).filter(Boolean);
for(var i=0;i<L.length;i++){var m=L[i].match(/^([A-Za-z0-9-]+)\s*:\s*(.*)$/);
if(m){h[m[1].toLowerCase()]=m[2];continue}
if(/^[a-z0-9-]+$/i.test(L[i])&&i+1<L.length&&!/^[A-Za-z0-9-]+\s*:/.test(L[i+1])){h[L[i].toLowerCase()]=L[i+1];i++}}
return h}
function esc(s){return s.replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function li(c,t,d){return '<li class="'+c+'"><b>'+t+'</b>'+d+'</li>'}
function run(){var h=parse(document.getElementById("h").value),add=[],rem=[],n=0,k=0;
if(!Object.keys(h).length){document.getElementById("r").innerHTML='<p class="score">No headers found. Paste lines like <code>name: value</code>.</p>';return}
function want(name,ok,fix,hint){var v=h[name];if(v===undefined){add.push(li("ng","✕ "+name+" is missing",fix));return}
if(ok&&!ok(v)){add.push(li("info","△ "+name+": "+esc(v),hint));return}n++;add.push(li("ok","✓ "+name,esc(v)))}
want("strict-transport-security",function(v){return /max-age=\d+/i.test(v)},"Add it on HTTPS responses, e.g. <code>max-age=31536000; includeSubDomains</code>.","Needs a <code>max-age</code> value.");
want("content-security-policy",null,"Start with <code>frame-ancestors 'self'; object-src 'none'; base-uri 'self'</code> and test before tightening.");
want("x-frame-options",function(v){return /^(deny|sameorigin)$/i.test(v.trim())},"Add <code>DENY</code> or <code>SAMEORIGIN</code> (or use CSP <code>frame-ancestors</code>).","Use <code>DENY</code> or <code>SAMEORIGIN</code>.");
want("x-content-type-options",function(v){return v.trim().toLowerCase()==="nosniff"},"Add <code>nosniff</code>.","The only valid value is <code>nosniff</code>.");
want("referrer-policy",null,"Set it explicitly, e.g. <code>strict-origin-when-cross-origin</code>.");
want("permissions-policy",null,"Turn off features you never use, e.g. <code>geolocation=(), camera=(), microphone=()</code>.");
want("cross-origin-opener-policy",null,"Add <code>same-origin</code> (or <code>same-origin-allow-popups</code> if you use sign-in or payment popups).");
function drop(name,bad,fix){var v=h[name];if(v!==undefined&&bad(v)){k++;rem.push(li("ng","✕ Remove: "+name+": "+esc(v),fix))}}
drop("x-powered-by",function(){return true},"OWASP: remove all X-Powered-By headers. It tells visitors which framework you run."+(/php/i.test(h["x-powered-by"]||"")?' PHP: set <code>expose_php = Off</code>, and <a href="BASE/tools/php-version-checker/">check this PHP version against the October 2026 fixes</a>.':''));
drop("server",function(v){return /\d/.test(v)},"Hide the version number (nginx: <code>server_tokens off;</code>).");
drop("x-xss-protection",function(v){return v.trim()!=="0"},"OWASP: do not set it, or turn it off with <code>0</code>. Use CSP instead.");
drop("public-key-pins",function(){return true},"OWASP: do not use.");
drop("expect-ct",function(){return true},"OWASP: do not use it.");
document.getElementById("r").innerHTML='<p class="score">'+n+' of 7 recommended headers look right. '+(k?k+' header'+(k>1?'s':'')+' to remove.':'Nothing to remove.')+'</p>'+
(rem.length?'<h2>Remove first (usually one-line changes)</h2><ul class="res">'+rem.join("")+'</ul>':'')+'<h2>The 7 to add</h2><ul class="res">'+add.join("")+'</ul>'+
'<p class="note">Add CSP, COOP and HSTS one at a time and test: they can break parts of a site.</p>'}
document.getElementById("go").onclick=run;
document.getElementById("ex").onclick=function(){document.getElementById("h").value=EX;run()};
})();
</script>'''

COOKIE = r'''<h1>Set-Cookie builder and checker</h1>
<div class="answer"><p class="ah">HOW IT WORKS</p><p>Fill in the cookie and pick its attributes. You get the <code>Set-Cookie</code> line to copy, and a warning for each combination that browsers reject or that is easy to get wrong. It runs only in your browser.</p></div>
<div class="tool">
<div><label for="cn">Name</label><input type="text" id="cn" value="session" spellcheck="false"></div>
<div><label for="cv">Value</label><input type="text" id="cv" value="abc123" spellcheck="false"></div>
<div><label for="cp">Path</label><input type="text" id="cp" value="/" spellcheck="false"></div>
<div><label for="cd">Domain (leave empty for this host only)</label><input type="text" id="cd" value="" spellcheck="false" placeholder="example.com"></div>
<div><label for="cm">Max-Age in seconds (leave empty for a session cookie)</label><input type="number" id="cm" value="" min="0" placeholder="86400 = 1 day"></div>
<div><label for="cs">SameSite</label><select id="cs"><option value="">(not set)</option><option>Strict</option><option selected>Lax</option><option>None</option></select></div>
<div class="row"><label><input type="checkbox" id="sec" checked> Secure</label><label><input type="checkbox" id="ho" checked> HttpOnly</label><label><input type="checkbox" id="pt"> Partitioned</label></div>
</div>
<p class="score">Your header</p><div id="out"></div><p><button class="btn ghost" id="copy" type="button">Copy</button></p>
<ul class="res" id="warn" aria-live="polite"></ul>
<h2 id="rules">The rules this checks</h2>
<ul><li><code>SameSite=None</code> needs <code>Secure</code>. MDN: "The <code>Secure</code> attribute must also be set when using this value."</li>
<li><code>Partitioned</code> needs <code>Secure</code>.</li>
<li>A name starting with <code>__Secure-</code> needs <code>Secure</code>. A name starting with <code>__Host-</code> needs <code>Secure</code>, <code>Path=/</code> and no <code>Domain</code>.</li>
<li>Without <code>SameSite</code>, Chrome treats the cookie as <code>Lax</code>.</li>
<li>If both <code>Expires</code> and <code>Max-Age</code> are set, <code>Max-Age</code> wins, so this tool only uses <code>Max-Age</code>.</li></ul>
<p>More on the three SameSite values: <a href="BASE/samesite-cookie-attribute/">SameSite cookies explained</a>. To see and edit the cookies a site has already set: <a href="BASE/edit-cookies-in-chrome/">How to view and edit cookies in Chrome</a>.</p>
<h2 id="not-for">Who this is not for</h2>
<ul><li>This builds one header line. It does not check what your server or framework actually sends; look at the real response in DevTools for that.</li>
<li>It does not encode special characters in the value for you. Keep values to letters, numbers and <code>-_.</code>, or encode them in your code.</li></ul>
<h2 id="sources">Sources (checked 2026-10-12)</h2>
<ul><li>MDN, Set-Cookie: <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie">https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie</a></li>
<li>web.dev, SameSite cookies explained: <a href="https://web.dev/articles/samesite-cookies-explained">https://web.dev/articles/samesite-cookies-explained</a></li></ul>
<script>
(function(){
function $(i){return document.getElementById(i)}
function esc(s){return s.replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function li(c,t){return '<li class="'+c+'">'+t+'</li>'}
function run(){var n=$("cn").value.trim(),v=$("cv").value.trim(),p=$("cp").value.trim(),d=$("cd").value.trim(),m=$("cm").value.trim(),s=$("cs").value,sec=$("sec").checked,ho=$("ho").checked,pt=$("pt").checked,w=[];
var a=[n+"="+v];if(p)a.push("Path="+p);if(d)a.push("Domain="+d);if(m!=="")a.push("Max-Age="+m);if(sec)a.push("Secure");if(ho)a.push("HttpOnly");if(s)a.push("SameSite="+s);if(pt)a.push("Partitioned");
var line="Set-Cookie: "+a.join("; ");$("out").textContent=line;
if(!n)w.push(li("ng","✕ The cookie needs a name."));
if(/[\s;,\\"]/.test(v))w.push(li("ng","✕ The value contains a space, comma, semicolon, quote or backslash. Encode it first."));
if(s==="None"&&!sec)w.push(li("ng","✕ SameSite=None without Secure: browsers reject this cookie. Turn on Secure."));
if(pt&&!sec)w.push(li("ng","✕ Partitioned without Secure: turn on Secure."));
if(/^__Secure-/.test(n)&&!sec)w.push(li("ng","✕ A __Secure- name needs Secure."));
if(/^__Host-/.test(n)){if(!sec)w.push(li("ng","✕ A __Host- name needs Secure."));if(d)w.push(li("ng","✕ A __Host- name must not have a Domain."));if(p!=="/")w.push(li("ng","✕ A __Host- name needs Path=/."))}
if(!s)w.push(li("info","△ No SameSite: Chrome treats the cookie as Lax. Set the value you mean."));
if(!ho)w.push(li("info","△ No HttpOnly: page JavaScript can read this cookie through document.cookie. Turn it on unless your scripts need to read it."));
if(!sec&&s!=="None")w.push(li("info","△ No Secure: the cookie is also sent on plain http:// requests."));
if(d)w.push(li("info","△ With Domain set, the cookie is also sent to subdomains. Leave it empty to keep it to this host only."));
if(m==="")w.push(li("info","△ No Max-Age: this is a session cookie."));
if(m!==""&&Number(m)<=0)w.push(li("info","△ Max-Age of 0 or less expires the cookie immediately (this is how you delete one)."));
if(!w.length)w.push(li("ok","✓ No problems found with these attributes."));
$("warn").innerHTML=w.join("")}
["cn","cv","cp","cd","cm","cs","sec","ho","pt"].forEach(function(i){$(i).addEventListener("input",run);$(i).addEventListener("change",run)});
$("copy").onclick=function(){navigator.clipboard.writeText($("out").textContent).then(function(){$("copy").textContent="Copied";setTimeout(function(){$("copy").textContent="Copy"},1500)})};
run()})();
</script>'''

XPATH = r'''<h1>XPath tester</h1>
<div class="answer"><p class="ah">HOW IT WORKS</p><p>Paste HTML (for example, copied with <b>Copy outerHTML</b> in Chrome DevTools) and type an XPath. You see how many nodes match and the text of each one. It runs only in your browser: the HTML is parsed with <code>DOMParser</code>, which does not run its scripts, and nothing is sent anywhere.</p></div>
<div class="tool">
<label for="src">HTML</label><textarea id="src" spellcheck="false"></textarea>
<label for="xp">XPath</label><input type="text" id="xp" spellcheck="false" value="//li/a">
<div class="row"><button class="btn" id="go" type="button">Test</button><button class="btn ghost" id="ex" type="button">Try an example</button><button class="btn ghost" id="cp" type="button">Copy results</button></div>
</div>
<p class="score" id="cnt" aria-live="polite"></p><ul class="res" id="list"></ul>
<h2 id="examples">XPath you will use most</h2>
<ul><li><code>//li</code>: every <code>li</code> element in the page.</li>
<li><code>//ul[@id='news']/li</code>: the <code>li</code> children of the list whose id is <code>news</code>.</li>
<li><code>//a/@href</code>: the <code>href</code> value of every link (an attribute, not the element).</li>
<li><code>//table//tr[td]</code>: table rows that have data cells, which skips a header row made of <code>th</code>.</li>
<li><code>(//li)[1]</code>: the first <code>li</code> in the whole page. <code>//li[1]</code> is different: the first <code>li</code> inside each parent.</li>
<li><code>//h3[contains(., 'Price')]</code>: <code>h3</code> elements whose text contains "Price".</li>
<li><code>count(//li)</code>: a number instead of nodes.</li></ul>
<h2 id="in-chrome">Testing on a live page instead</h2>
<p>In Chrome DevTools, open the Console and type <code>$x("//li/a")</code>. Chrome's documentation says <code>$x(path)</code> "returns an array of DOM elements that match the given XPath expression". To pick an element and get every similar one as a table, our free extension Honest Scraper does that on the page itself.</p>
<h2 id="not-for">Who this is not for</h2>
<ul><li>The HTML you paste is a snapshot. Content that a page adds later with JavaScript is only there if it was in the DOM when you copied it.</li>
<li>Browsers support XPath 1.0 through <code>document.evaluate</code>. XPath 2.0 and 3.1 functions such as <code>matches()</code> or <code>lower-case()</code> are not available here, and will not work in the browser either.</li></ul>
<h2 id="sources">Sources (checked 2026-10-14)</h2>
<ul><li>MDN, Document: evaluate() method: <a href="https://developer.mozilla.org/en-US/docs/Web/API/Document/evaluate">https://developer.mozilla.org/en-US/docs/Web/API/Document/evaluate</a></li>
<li>MDN, DOMParser: parseFromString() method: <a href="https://developer.mozilla.org/en-US/docs/Web/API/DOMParser/parseFromString">https://developer.mozilla.org/en-US/docs/Web/API/DOMParser/parseFromString</a></li>
<li>Chrome for Developers, Console Utilities API reference ($x): <a href="https://developer.chrome.com/docs/devtools/console/utilities">https://developer.chrome.com/docs/devtools/console/utilities</a></li></ul>
<script>
(function(){
function $(i){return document.getElementById(i)}
var EX='<ul id="news">\n  <li><a href="/post/1">First post</a> <span class="date">2026-10-01</span></li>\n  <li><a href="/post/2">Second post</a> <span class="date">2026-10-05</span></li>\n  <li><a href="/post/3">Third post</a> <span class="date">2026-10-09</span></li>\n</ul>';
var last=[];
function txt(n){if(n.nodeType===2)return n.value;return (n.textContent||"").replace(/\s+/g," ").trim()}
function label(n){if(n.nodeType===2)return "@"+n.name;if(n.nodeType===1)return "<"+n.localName+">";if(n.nodeType===3)return "text";return "node"}
function add(cls,head,body){var li=document.createElement("li");li.className=cls;var b=document.createElement("b");b.textContent=head;li.appendChild(b);if(body!==undefined){var s=document.createElement("span");s.textContent=body;li.appendChild(s)}$("list").appendChild(li)}
function run(){$("list").textContent="";last=[];
var doc=new DOMParser().parseFromString($("src").value,"text/html"),r;
try{r=doc.evaluate($("xp").value,doc,null,XPathResult.ANY_TYPE,null)}catch(e){$("cnt").textContent="This XPath has an error.";add("ng","✕ "+e.message);return}
if(r.resultType===XPathResult.NUMBER_TYPE){$("cnt").textContent="Number: "+r.numberValue;last=[String(r.numberValue)];return}
if(r.resultType===XPathResult.STRING_TYPE){$("cnt").textContent="Text result";add("ok",JSON.stringify(r.stringValue));last=[r.stringValue];return}
if(r.resultType===XPathResult.BOOLEAN_TYPE){$("cnt").textContent="True/false: "+r.booleanValue;last=[String(r.booleanValue)];return}
var nodes=[],n;while((n=r.iterateNext()))nodes.push(n);
$("cnt").textContent=nodes.length+(nodes.length===1?" match":" matches");
if(!nodes.length){add("info","△ Nothing matched. Check the spelling of element names and attribute values; HTML element names are lower case here.");return}
nodes.slice(0,500).forEach(function(x,i){var t=txt(x);last.push(t);add("ok",(i+1)+". "+label(x),t||"(empty)")});
if(nodes.length>500)add("info","△ Showing the first 500.")}
$("go").onclick=run;
$("xp").addEventListener("keydown",function(e){if(e.key==="Enter")run()});
$("ex").onclick=function(){$("src").value=EX;$("xp").value="//ul[@id='news']/li/a/@href";run()};
$("cp").onclick=function(){navigator.clipboard.writeText(last.join("\n")).then(function(){$("cp").textContent="Copied";setTimeout(function(){$("cp").textContent="Copy results"},1500)})};
})();
</script>'''

CONVERTER = r'''<h1>Cookie JSON to cookies.txt converter</h1>
<div class="answer"><p class="ah">HOW IT WORKS</p><p>Paste a JSON list of cookies (the property names Chrome's <code>chrome.cookies</code> API uses, which many cookie editors export) to get a cookies.txt file with the seven TAB-separated fields curl expects. Or paste a cookies.txt to get JSON back. It runs only in your browser: nothing you paste is sent anywhere.</p></div>
<div class="tool">
<div class="row"><label><input type="radio" name="dir" id="d1" checked> JSON to cookies.txt</label><label><input type="radio" name="dir" id="d2"> cookies.txt to JSON</label></div>
<label for="in">Input</label><textarea id="in" spellcheck="false"></textarea>
<div class="row"><button class="btn" id="go" type="button">Convert</button><button class="btn ghost" id="ex" type="button">Try an example</button><button class="btn ghost" id="cp" type="button">Copy result</button><button class="btn ghost" id="dl" type="button">Save as file</button></div>
</div>
<ul class="res" id="msg" aria-live="polite"></ul>
<label for="out">Result</label><textarea id="out" spellcheck="false" readonly></textarea>
<h2 id="mapping">The mapping it uses</h2>
<table><tr><th>cookies.txt field</th><th>JSON property</th></tr>
<tr><td>Domain (with <code>#HttpOnly_</code> in front when HttpOnly)</td><td><code>domain</code>, <code>httpOnly</code></td></tr>
<tr><td>Include subdomains (TRUE/FALSE)</td><td>the opposite of <code>hostOnly</code> (our reading)</td></tr>
<tr><td>Path</td><td><code>path</code></td></tr>
<tr><td>HTTPS only (TRUE/FALSE)</td><td><code>secure</code></td></tr>
<tr><td>Expiry (seconds since 1970, or 0)</td><td><code>expirationDate</code>; 0 when it is missing (session cookie)</td></tr>
<tr><td>Name, value</td><td><code>name</code>, <code>value</code></td></tr></table>
<p>The reasons, and a Python version of the same converter: <a href="BASE/cookie-editor-json-to-cookies-txt-for-curl/">Cookie editor export to cookies.txt: the 7 fields curl expects</a>. Try the result with <code>curl -v -b cookies.txt https://your-test-site.example/</code>.</p>
<h2 id="not-for">Who this is not for</h2>
<ul><li>cookies.txt has no place for <code>SameSite</code> or partition keys, so converting to cookies.txt drops them, and converting back cannot restore them.</li>
<li>If your export uses other property names, the converter tells you which are missing instead of guessing.</li>
<li>The files hold live session values. Keep them out of Git and bug reports, and delete them after testing. Only use cookies for sites you are allowed to test.</li></ul>
<h2 id="sources">Sources (checked 2026-10-22)</h2>
<ul><li>curl, HTTP cookies (file structure and the seven fields): <a href="https://curl.se/docs/http-cookies.html">https://curl.se/docs/http-cookies.html</a></li>
<li>Chrome for Developers, chrome.cookies (cookie properties): <a href="https://developer.chrome.com/docs/extensions/reference/api/cookies">https://developer.chrome.com/docs/extensions/reference/api/cookies</a></li></ul>
<script>
(function(){
function $(i){return document.getElementById(i)}
var EXJ='[\n  {"domain": ".example.com", "hostOnly": false, "path": "/", "secure": true, "httpOnly": true, "expirationDate": 1798761600, "name": "session", "value": "abc123", "sameSite": "lax"},\n  {"domain": "app.example.com", "hostOnly": true, "path": "/", "secure": true, "httpOnly": false, "session": true, "name": "theme", "value": "dark"}\n]';
function li(c,t){var e=document.createElement("li");e.className=c;e.textContent=t;$("msg").appendChild(e)}
function toTxt(text){var a;try{a=JSON.parse(text)}catch(e){li("ng","✕ This is not valid JSON: "+e.message);return ""}
if(!Array.isArray(a)){if(a&&Array.isArray(a.cookies))a=a.cookies;else{li("ng","✕ Expected a JSON list of cookies ([ ... ]).");return ""}}
var out=["# Netscape HTTP Cookie File"],skip=0,drop=0;
a.forEach(function(c,i){var miss=["domain","name","path"].filter(function(k){return typeof(c&&c[k])!=="string"});
if(miss.length||c.value===undefined){skip++;li("ng","✕ Cookie "+(i+1)+" skipped: missing "+(miss.concat(c&&c.value!==undefined?[]:["value"]).join(", ")));return}
if(/[\t\r\n]/.test(c.name+c.value+c.domain+c.path)){skip++;li("ng","✕ Cookie "+(i+1)+" skipped: a field contains a TAB or line break.");return}
if(c.sameSite||c.partitionKey)drop++;
var d=(c.httpOnly?"#HttpOnly_":"")+c.domain,sub=c.hostOnly?"FALSE":"TRUE",sec=c.secure?"TRUE":"FALSE",exp=(typeof c.expirationDate==="number"&&!c.session)?String(Math.floor(c.expirationDate)):"0";
out.push([d,sub,c.path,sec,exp,c.name,String(c.value)].join("\t"))});
li(skip?"info":"ok",(skip?"△ ":"✓ ")+(out.length-1)+" cookie"+(out.length===2?"":"s")+" converted"+(skip?", "+skip+" skipped.":"."));
if(drop)li("info","△ SameSite and partition keys have no place in cookies.txt and were left out.");
return out.join("\n")+"\n"}
function toJson(text){var out=[],bad=0;
text.split(/\r?\n/).forEach(function(line,i){if(!line.trim())return;var ho=false;
if(line.indexOf("#HttpOnly_")===0){ho=true;line=line.slice(10)}else if(line.charAt(0)==="#")return;
var f=line.split("\t");if(f.length!==7){bad++;li("ng","✕ Line "+(i+1)+" skipped: it has "+f.length+" TAB-separated fields, not 7.");return}
var c={domain:f[0],hostOnly:f[1]!=="TRUE",path:f[2],secure:f[3]==="TRUE",httpOnly:ho,name:f[5],value:f[6]};
var e=Number(f[4]);if(e>0)c.expirationDate=e;else c.session=true;out.push(c)});
li(bad?"info":"ok",(bad?"△ ":"✓ ")+out.length+" cookie"+(out.length===1?"":"s")+" read"+(bad?", "+bad+(bad===1?" line":" lines")+" skipped.":"."));
return JSON.stringify(out,null,2)}
function run(){$("msg").textContent="";var t=$("in").value;if(!t.trim()){li("info","△ Paste something first.");$("out").value="";return}
$("out").value=$("d1").checked?toTxt(t):toJson(t)}
$("go").onclick=run;
$("ex").onclick=function(){$("d1").checked=true;$("in").value=EXJ;run()};
$("cp").onclick=function(){navigator.clipboard.writeText($("out").value).then(function(){$("cp").textContent="Copied";setTimeout(function(){$("cp").textContent="Copy result"},1500)})};
$("dl").onclick=function(){if(!$("out").value)return;var a=document.createElement("a");a.href=URL.createObjectURL(new Blob([$("out").value],{type:"text/plain"}));a.download=$("d1").checked?"cookies.txt":"cookies.json";a.click();setTimeout(function(){URL.revokeObjectURL(a.href)},5000)};
})();
</script>'''

PHPCHECK = r'''<h1>PHP version checker for CVE-2026-109618 and CVE-2026-109619</h1>
<div class="answer"><p class="ah">SHORT ANSWER</p><p>On 21 October 2026 php.net released PHP 8.5.12, 8.4.27, 8.3.36 and 8.2.35 to fix two critical remote code execution bugs (CVSS v4.0 9.2). Paste your <code>php -v</code> output, a <code>X-Powered-By</code> header, or <code>php -i</code> lines below to see whether your version is at or above the fixed release for its branch. It runs only in your browser: nothing you paste is sent anywhere.</p></div>
<div class="tool"><label for="h">Paste <code>php -v</code>, response headers, or <code>php -i</code> output</label>
<textarea id="h" spellcheck="false" placeholder="PHP 8.3.30 (cli) (built: ...)&#10;or&#10;X-Powered-By: PHP/8.3.30"></textarea>
<div class="row"><button class="btn" id="go" type="button">Check</button><button class="btn ghost" id="ex" type="button">Try an example</button></div></div>
<div id="r" aria-live="polite"></div>
<h2 id="fixed">Fixed versions by branch</h2>
<table><tr><th>Branch</th><th>Fixed in</th></tr>
<tr><td>8.5</td><td>8.5.12</td></tr><tr><td>8.4</td><td>8.4.27</td></tr><tr><td>8.3</td><td>8.3.36</td></tr><tr><td>8.2</td><td>8.2.35</td></tr>
<tr><td>7.4, 8.0, 8.1</td><td>No php.net release. Source backports only; ask your vendor or upgrade.</td></tr>
<tr><td>Older</td><td>No fix from php.net. Upgrade to a supported branch.</td></tr></table>
<h2 id="where">Where to get the version</h2>
<ul><li><b>On the server:</b> <code>php -v</code>. The web server can run a different PHP than the command line, so also check the version your site reports (for example a <code>phpinfo()</code> page you then delete).</li>
<li><b>From outside:</b> <code>curl -sI https://your-site.example</code> shows <code>X-Powered-By: PHP/…</code> only while <code>expose_php</code> is on.</li>
<li><b>Settings:</b> <code>php -i | grep -E "memory_limit|post_max_size|upload_progress.enabled|fatal_error_backtraces"</code></li></ul>
<h2 id="interim">If you cannot update today</h2>
<p>php.net says only an update is a complete fix. These settings reduce some attack paths but "do not make an installation safe":</p>
<ul><li><code>session.upload_progress.enabled=0</code> in php.ini, an FPM pool or server config (not <code>ini_set()</code> or <code>.user.ini</code>), then restart every worker.</li>
<li>PHP 8.5 only: <code>fatal_error_backtraces=0</code>, then restart every worker.</li>
<li><code>memory_limit=-1</code>, set where applications cannot override it (for example <code>php_admin_value</code>), and a low <code>post_max_size</code> (8M without uploads, 32M with uploads).</li>
<li>Hiding errors with <code>display_errors</code> or <code>@</code> does not help.</li></ul>
<h2 id="not-for">Who this is not for</h2>
<ul><li>Linux distribution packages (Debian, Ubuntu, Red Hat and others) often fix bugs without changing the upstream version number. If your version has a suffix like <code>-1ubuntu</code> or <code>deb12</code>, the number alone cannot tell you; check your distribution's security notice.</li>
<li>This tool does not scan a site, test for the bug, or tell you whether you were attacked. For a hosted site, ask your host which PHP build they run.</li></ul>
<h2 id="sources">Sources (checked 2026-10-22)</h2>
<ul><li>php.net, Security advisory, 21 Oct 2026: <a href="https://www.php.net/archive/2026.php#2026-10-21-5">https://www.php.net/archive/2026.php#2026-10-21-5</a></li>
<li>PHP security advisory GHSA-w8hw-w9fx-j79w (CVE-2026-109618): <a href="https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w">https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w</a></li>
<li>PHP security advisory GHSA-6wmf-4rv5-p3rp (CVE-2026-109619): <a href="https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp">https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp</a></li>
<li>PHP manual, expose_php: <a href="https://www.php.net/manual/en/ini.core.php">https://www.php.net/manual/en/ini.core.php</a></li></ul>
<script>
(function(){
var FIX={"8.5":12,"8.4":27,"8.3":36,"8.2":35},EX="X-Powered-By: PHP/8.3.30\nmemory_limit => 128M => 128M\npost_max_size => 64M => 64M\nsession.upload_progress.enabled => On => On";
function esc(s){return s.replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function li(c,t,d){return '<li class="'+c+'"><b>'+t+'</b>'+(d||"")+'</li>'}
function ini(t,k){var m=t.match(new RegExp("^\\s*"+k.replace(/\./g,"\\.")+"\\s*(?:=>|=)\\s*([^\\n]*)$","mi"));if(!m)return null;var v=m[1].split("=>").pop().trim().replace(/^"|"$/g,"");return v}
function off(v){return /^(0|off|false|no|)$/i.test(v)}
function mb(v){var m=String(v).trim().match(/^(-?\d+)\s*([kmg]?)/i);if(!m)return null;var n=+m[1],u=m[2].toLowerCase();return u==="g"?n*1024:u==="m"?n:u==="k"?n/1024:n/1048576}
function run(){var t=document.getElementById("h").value,out=[],head="";
var m=t.match(/PHP[\/ ](\d+)\.(\d+)\.(\d+)([^\s;,)]*)/i);
if(m){var br=m[1]+"."+m[2],p=+m[3],full=m[1]+"."+m[2]+"."+m[3]+m[4],v=esc(full),dist=/ubuntu|deb|el\d|\+|~|-\d/i.test(m[4]);
if(FIX[br]!==undefined){if(p>=FIX[br]){head="PHP "+v+": at or above the fixed release "+br+"."+FIX[br]+".";out.push(li("ok","✓ "+head,"Restart PHP-FPM or the web server so the running workers use it."))}
else{head="PHP "+v+": "+(dist?"the number is below "+br+"."+FIX[br]+"; check your distribution.":"update to "+br+"."+FIX[br]+" or later.");out.push(li("ng","✕ "+head,dist?"Your version has a distribution suffix. The package may already carry the fix; check your distribution's security notice before deciding.":"php.net calls this the only complete fix. See the interim settings below if you cannot update today."))}}
else if(/^(7\.4|8\.0|8\.1)$/.test(br)){head="PHP "+v+": no php.net release for this branch.";out.push(li("ng","✕ "+head,"php.net published source backports for 7.4, 8.0 and 8.1 only. Ask your vendor or host for a patched build, or upgrade to 8.2 or later."))}
else if(+m[1]<8||(+m[1]===8&&+m[2]<2)){head="PHP "+v+": end of life, no fix from php.net.";out.push(li("ng","✕ "+head,"Upgrade to a supported branch (8.2 or later)."))}
else{head="PHP "+v+": this branch is not in the 21 October 2026 advisory.";out.push(li("info","△ "+head,"Check php.net for the current release of this branch."))}
if(/x-powered-by\s*:/i.test(t))out.push(li("info","△ Your PHP version is visible in X-Powered-By","Set <code>expose_php = Off</code> in php.ini to stop sending it. This hides the number; it does not fix anything."))}
else out.push(li("info","△ No PHP version found","Paste a line like <code>PHP 8.3.30 (cli)</code> or <code>X-Powered-By: PHP/8.3.30</code>."));
var up=ini(t,"session.upload_progress.enabled"),fb=ini(t,"fatal_error_backtraces"),ml=ini(t,"memory_limit"),pm=ini(t,"post_max_size");
if(up!==null)out.push(off(up)?li("ok","✓ session.upload_progress.enabled is off"):li("info","△ session.upload_progress.enabled is "+esc(up),"php.net suggests 0 if you do not use the feature, even after updating."));
if(fb!==null&&m&&m[1]+"."+m[2]==="8.5")out.push(off(fb)?li("ok","✓ fatal_error_backtraces is off"):li("info","△ fatal_error_backtraces is "+esc(fb),"Interim setting on 8.5: 0, then restart every worker."));
if(ml!==null)out.push(String(ml).trim()==="-1"?li("ok","✓ memory_limit is -1"):li("info","△ memory_limit is "+esc(ml),"Interim setting for CVE-2026-109618 is -1, set where apps cannot override it. Not needed once you are on a fixed release."));
if(pm!==null){var n=mb(pm);out.push(n!==null&&n<=32?li("ok","✓ post_max_size is "+esc(pm)):li("info","△ post_max_size is "+esc(pm),"php.net suggests 8M without file uploads, 32M with uploads, while you wait to update."))}
document.getElementById("r").innerHTML=(head?'<p class="score">'+head+'</p>':'')+'<ul class="res">'+out.join("")+'</ul>'}
document.getElementById("go").onclick=run;
document.getElementById("ex").onclick=function(){document.getElementById("h").value=EX;run()};
})();
</script>'''

BODIES = {"php-version-checker": PHPCHECK, "security-headers-checker": CHECKER, "set-cookie-builder": COOKIE, "xpath-tester": XPATH, "cookie-converter": CONVERTER}
