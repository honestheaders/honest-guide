"""手続きの期限計算ツール(無料版)。build.py から使う。
データは公開済みの記事で出典を確認した期限だけを載せる。新しい手続きを足すときは、公的な出典を2か所以上で確認してから。"""
import json, html

TOOLS = [
    {
        "slug": "hikkoshi-kigen",
        "title": "引っ越しの手続き 期限計算ツール",
        "seo": "引っ越しの手続き期限を日付で計算|転入届・マイナンバーカード・車の住所変更",
        "desc": "引っ越しの日を入れると、転出届・転入届・マイナンバーカード・車の住所変更の期限日と残り日数が出ます。カレンダーへの追加、家族へのLINE共有もできます。",
        "lead": "引っ越しの日(新しい家に住み始めた日)を入れると、役所の手続きの期限日と、あと何日あるかが出ます。",
        "label": "引っ越しの日(住み始めた日)",
        "label2": "転入届を出した日(出したあとに入れる。空でもよい)",
        "article": "hikkoshi-tetsuzuki-kigen",
        "items": [
            {"n": "転出届(別の市区町村へ引っ越す場合)", "off": -1, "rule": "引っ越す前に出すのが原則", "where": "今の住所の市区町村", "warn": ""},
            {"n": "転入届・転居届", "off": 14, "rule": "住み始めた日から14日以内", "where": "新しい住所の市区町村", "warn": "14日以内に手続きをしないと、マイナンバーカードが失効します(マイナポータルの案内)。"},
            {"n": "マイナンバーカードの継続利用の手続き", "off": 90, "base2": True, "rule": "転入届を出した日から90日以内", "where": "新しい住所の市区町村", "warn": ""},
            {"n": "車の住所変更(変更登録・登録自動車)", "off": 15, "rule": "住所が変わった日から15日以内", "where": "運輸支局・自動車検査登録事務所(平日のみ)", "warn": ""},
        ],
        "sources": [
            ("総務省「住民基本台帳制度に基づく各種届出」", "https://www.soumu.go.jp/main_content/000753608.pdf"),
            ("マイナポータル「引越し関連手続一覧」", "https://myna.go.jp/html/moving_oss_procedure_list.html"),
            ("国土交通省 近畿運輸局 和歌山運輸支局「登録自動車の変更登録手続きについて」(道路運送車両法第12条第1項)", "https://wwwtb.mlit.go.jp/kinki/wakayama/R20515henkotetsuzuki.pdf"),
            ("国土交通省 自動車検査登録総合ポータルサイト「Q&A」", "https://www.jidoushatouroku-portal.mlit.go.jp/jidousha/kensatoroku/faq/index.html"),
        ],
        "checked": "2026年10月3日",
        "excel": "Excel版は、電気・ガス・水道、郵便の転送、運転免許、児童手当など、23の手続きをまとめて管理できます。",
        "goods": [("引っ越し 段ボール", "引っ越し用の段ボールを探す"), ("クリアファイル A4", "書類をまとめるクリアファイルを探す")],
    },
    {
        "slug": "taishoku-kigen",
        "title": "退職後の手続き 期限計算ツール",
        "seo": "退職後の手続き期限を日付で計算|任意継続20日・国保と国民年金14日",
        "desc": "退職日を入れると、任意継続・国民健康保険・国民年金・失業給付の受給期間の期限日と残り日数が出ます。カレンダーへの追加、家族へのLINE共有もできます。",
        "lead": "退職日(最後に在籍した日)を入れると、健康保険・年金・雇用保険の期限日と、あと何日あるかが出ます。",
        "label": "退職日(最後に在籍した日)",
        "label2": "",
        "article": "taishoku-tetsuzuki-kigen",
        "items": [
            {"n": "任意継続(前の健康保険を続ける場合)", "off": 20, "rule": "退職日の翌日から20日以内(20日目が土日・祝日なら翌営業日)", "where": "加入していた健康保険(協会けんぽなど)", "warn": ""},
            {"n": "国民健康保険への加入(国保を選ぶ場合)", "off": 14, "rule": "資格を失った日から14日以内(自治体の案内による)", "where": "住所地の市区町村", "warn": ""},
            {"n": "国民年金への切り替え", "off": 14, "rule": "退職日の翌日から14日以内", "where": "住所地の市区町村", "warn": ""},
            {"n": "失業給付(基本手当)の受給期間の終わり", "year": 1, "rule": "原則、離職日の翌日から1年", "where": "ハローワーク", "warn": "受給期間は原則1年です。いつまでに何をするかは、早めにハローワークで確認してください。"},
        ],
        "sources": [
            ("日本年金機構「国民年金に加入するための手続き」", "https://www.nenkin.go.jp/service/kokunen/kanyu/20140710-04.html"),
            ("全国健康保険協会(協会けんぽ)「任意継続」", "https://www.kyoukaikenpo.or.jp/benefit/voluntary_continuation/index.html"),
            ("大阪市「就職・退職に伴う国民健康保険の手続き」", "https://www.city.osaka.lg.jp/fukushi/page/0000369739.html"),
            ("ハローワークインターネットサービス「基本手当」", "https://www.hellowork.mhlw.go.jp/insurance/insurance_basicbenefit.html"),
        ],
        "checked": "2026年10月1日",
        "excel": "Excel版は、住民税、保険証の返却、確定申告など、17の手続きをまとめて管理できます。",
        "goods": [("書類ファイル", "書類ファイルを探す"), ("クリアファイル A4", "書類をまとめるクリアファイルを探す")],
    },
]

JS = r"""
(function(){
const C=window.KIGEN, $=id=>document.getElementById(id);
const S={get:k=>{try{return localStorage.getItem(k)}catch(e){return null}},set:(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}}};
const W='日月火水木金土';
const p2=n=>String(n).padStart(2,'0');
const ymd=d=>d.getFullYear()+'-'+p2(d.getMonth()+1)+'-'+p2(d.getDate());
const jp=d=>d.getFullYear()+'年'+(d.getMonth()+1)+'月'+d.getDate()+'日('+W[d.getDay()]+')';
const parse=s=>{const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(s||'');return m?new Date(+m[1],+m[2]-1,+m[3]):null};
const add=(d,n)=>{const x=new Date(d);x.setDate(x.getDate()+n);return x};
const addY=(d,n)=>{const x=new Date(d);x.setFullYear(x.getFullYear()+n);return x};
const today=()=>{const t=new Date();return new Date(t.getFullYear(),t.getMonth(),t.getDate())};
const q=new URLSearchParams(location.search);
const d1=$('d1'), d2=$('d2');
d1.value=q.get('d')||S.get(C.slug+':d')||'';
if(d2) d2.value=q.get('t')||S.get(C.slug+':t')||'';
function rows(){
  const b=parse(d1.value); if(!b) return [];
  const b2=d2?parse(d2.value):null;
  return C.items.map((it,i)=>{
    let due, est='';
    if(it.year) due=addY(b,it.year);
    else if(it.base2){ due=add(b2||b,it.off); if(!b2) est='(転入届を引っ越しの日に出した場合。出した日を入れると正確になります)'; }
    else due=add(b,it.off);
    return {i,it,due,est};
  }).sort((a,b)=>a.due-b.due);
}
function gcal(r){
  const s=ymd(r.due).replace(/-/g,''), e=ymd(add(r.due,1)).replace(/-/g,'');
  const det=r.it.rule+'\n窓口: '+r.it.where+'\n期限は目安です。正確な日付は窓口で確認してください。\n'+link();
  return 'https://calendar.google.com/calendar/render?action=TEMPLATE&text='+encodeURIComponent('【期限】'+r.it.n)+'&dates='+s+'/'+e+'&details='+encodeURIComponent(det);
}
function link(){let u=location.origin+location.pathname+'?d='+d1.value; if(d2&&d2.value) u+='&t='+d2.value; return u;}
function render(){
  S.set(C.slug+':d',d1.value); if(d2) S.set(C.slug+':t',d2.value);
  const R=rows(), out=$('out'), t=today();
  if(!R.length){out.innerHTML='<p class="note">日付を入れると、ここに期限が出ます。</p>';$('share').hidden=true;return;}
  let done=0, next=null, h='';
  R.forEach(r=>{
    const k=C.slug+':c:'+d1.value+':'+r.i, ok=S.get(k)==='1'; if(ok) done++;
    const left=Math.round((r.due-t)/864e5);
    if(!ok&&left>=0&&!next) next={r,left};
    const cls=ok?'ok':left<0?'over':left<=7?'soon':'';
    const lt=ok?'済み':left<0?(-left)+'日過ぎています':left===0?'今日まで':'あと'+left+'日';
    const wk=(r.due.getDay()===0||r.due.getDay()===6)?'<span class="wk">土日です。窓口が開いているか確認を</span>':'';
    h+='<div class="kg '+cls+'"><label class="kc"><input type="checkbox" data-k="'+k+'"'+(ok?' checked':'')+'> 済</label>'+
       '<p class="kn">'+r.it.n+'</p><p class="kd"><b>'+jp(r.due)+'</b> <span class="kl">'+lt+'</span>'+wk+'</p>'+
       '<p class="kr">'+r.it.rule+r.est+'<br>窓口:'+r.it.where+'</p>'+(r.it.warn?'<p class="kw">'+r.it.warn+'</p>':'')+
       '<a class="kcal" href="'+gcal(r)+'" target="_blank" rel="noopener">Googleカレンダーに入れる</a></div>';
  });
  const head=next?'<p class="kh">いちばん近い期限は<b>'+next.r.it.n+'</b>。<br>'+(next.left===0?'<b>今日まで</b>です。':'あと<b>'+next.left+'日</b>です。')+'</p>':'';
  out.innerHTML=head+'<p class="kp">'+done+' / '+R.length+' 件 済み</p><div class="kbar"><i style="width:'+Math.round(done/R.length*100)+'%"></i></div>'+h;
  out.querySelectorAll('input[type=checkbox]').forEach(c=>c.addEventListener('change',()=>{S.set(c.dataset.k,c.checked?'1':'0');render();}));
  $('share').hidden=false;
}
function ics(){
  const R=rows(); if(!R.length) return;
  const esc=s=>s.replace(/\\/g,'\\\\').replace(/,/g,'\\,').replace(/;/g,'\\;').replace(/\n/g,'\\n');
  let s='BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Honest Guide//kigen//JA\r\nCALSCALE:GREGORIAN\r\n';
  const st=new Date().toISOString().replace(/[-:]/g,'').replace(/\.\d+/,'');
  R.forEach(r=>{
    s+='BEGIN:VEVENT\r\nUID:'+C.slug+'-'+r.i+'-'+ymd(r.due)+'@honest-guide\r\nDTSTAMP:'+st+'\r\nDTSTART;VALUE=DATE:'+ymd(r.due).replace(/-/g,'')+
       '\r\nDTEND;VALUE=DATE:'+ymd(add(r.due,1)).replace(/-/g,'')+'\r\nSUMMARY:'+esc('【期限】'+r.it.n)+
       '\r\nDESCRIPTION:'+esc(r.it.rule+'\n窓口: '+r.it.where+'\n期限は目安です。正確な日付は窓口で確認してください。\n'+link())+
       '\r\nBEGIN:VALARM\r\nACTION:DISPLAY\r\nDESCRIPTION:'+esc('3日後が期限: '+r.it.n)+'\r\nTRIGGER:-P3D\r\nEND:VALARM\r\nEND:VEVENT\r\n';
  });
  s+='END:VCALENDAR\r\n';
  const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([s],{type:'text/calendar'})); a.download=C.slug+'.ics'; document.body.appendChild(a); a.click(); a.remove();
}
function msg(){const R=rows();return C.title+'\n'+R.map(r=>'・'+r.it.n+':'+jp(r.due)).join('\n')+'\n'+link();}
$('ics').addEventListener('click',ics);
$('line').addEventListener('click',()=>{location.href='https://line.me/R/share?text='+encodeURIComponent(msg());});
$('copy').addEventListener('click',()=>{const m=msg();(navigator.share?navigator.share({text:m}):navigator.clipboard.writeText(m).then(()=>alert('コピーしました'))).catch(()=>{});});
d1.addEventListener('input',render); if(d2) d2.addEventListener('input',render);
render();
})();
"""

CSS = """
.kg{background:#fff;border:1px solid var(--l);border-left:6px solid #1f4e79;border-radius:10px;padding:12px 14px;margin:10px 0;position:relative}
.kg.soon{border-left-color:#e67e22}.kg.over{border-left-color:#c0392b;background:#fff5f5}.kg.ok{opacity:.55;border-left-color:#999}
.kn{font-weight:bold;margin:0 70px 4px 0}.kd{margin:0 0 4px}.kd b{font-size:20px}.kl{font-weight:bold;color:#c0392b;margin-left:6px}.kg.ok .kl{color:#666}
.wk{display:block;font-size:13px;color:#a0522d}.kr{font-size:13px;color:var(--m);margin:4px 0}.kw{font-size:13px;background:#fff3cd;border-radius:6px;padding:6px 8px;margin:6px 0}
.kc{position:absolute;top:10px;right:12px;font-size:15px}.kc input{width:22px;height:22px;vertical-align:middle}
.kcal{font-size:13px}.kh{background:#fff8dc;border:1px solid #ecd98a;border-radius:10px;padding:12px 14px;font-size:17px}.kh b{color:#c0392b}
.kp{margin:12px 0 4px;font-size:14px}.kbar{height:10px;background:#e5e5e0;border-radius:5px;overflow:hidden}.kbar i{display:block;height:100%;background:#2e8b57}
.kbtn{display:grid;gap:10px;margin:16px 0}.kbtn button{font-size:17px;padding:12px;border-radius:8px;border:1px solid #1f4e79;background:#fff;color:#1f4e79}
.kbtn button.line{background:#06c755;border-color:#06c755;color:#fff}.upsell{background:#eef5fb;border:1px solid #b9d3ea;border-radius:10px;padding:14px 16px;margin:20px 0}
"""

def build(page, rakuten_link, search_url, BASE, CFG):
    """各ツールのページを作り、(path, title, 説明) のリストを返す。"""
    made = []
    for t in TOOLS:
        data = {"slug": t["slug"], "title": t["title"], "items": t["items"]}
        d2 = f'<label>{t["label2"]}<input id="d2" type="date"></label>' if t["label2"] else ""
        src = "".join(f'<li>{html.escape(n)} <a href="{u}" rel="noopener" target="_blank">{html.escape(u)}</a></li>' for n, u in t["sources"])
        goods = "".join(rakuten_link(search_url(w), l) for w, l in t["goods"])
        ld = json.dumps({"@context": "https://schema.org", "@type": "WebApplication", "name": t["title"], "applicationCategory": "UtilitiesApplication",
                         "operatingSystem": "All", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
                         "url": f'{CFG["base_url"]}/tools/{t["slug"]}/', "description": t["desc"]}, ensure_ascii=False)
        body = f'''<nav class="crumb"><a href="{BASE}/">ホーム</a> › <a href="{BASE}/tools/">計算ツール</a> › {html.escape(t["title"])}</nav>
<h1>{html.escape(t["title"])}</h1>
<p class="pr">※このページにはプロモーション(広告)が含まれます。</p>
<p>{html.escape(t["lead"])}無料で、登録もいりません。入れた日付は、この端末の中だけに保存されます。</p>
<p class="note">※ 一般的な制度の説明で、個別の相談に代わるものではありません。期限は「翌日から数えて〇日目」で出した目安です。正確な締め切りや個別の事情は、各窓口でご確認ください。</p>
<div class="tool"><label>{t["label"]}<input id="d1" type="date"></label>{d2}</div>
<div id="out"></div>
<div id="share" class="kbtn" hidden>
<button id="ics" type="button">全部の期限をカレンダーに入れる(3日前にお知らせ)</button>
<button id="line" class="line" type="button">家族にLINEで送る</button>
<button id="copy" type="button">期限の一覧を送る・コピーする</button>
<p class="note">カレンダーに入れると、期限の3日前にお知らせが出ます(お使いのカレンダーの設定によります)。Androidで一括登録がうまくいかないときは、各手続きの「Googleカレンダーに入れる」を使ってください。送ったリンクを開くと、同じ日付で期限が表示されます。</p></div>
<div class="upsell"><p><b>手続きをまとめて管理したい人へ</b></p><p>{html.escape(t["excel"])}日付を入れるだけで期限日が自動で出ます(500円・Excel/Googleスプレッドシート)。</p><p><a href="{BASE}/templates/">期限チェック表(Excel)を見る</a></p></div>
<h2>くわしい説明</h2><p>それぞれの手続きの中身や必要な書類は、<a href="{BASE}/guides/{t["article"]}/">こちらの記事</a>で、公的な情報をもとに説明しています。</p>
<h2>手続きで使う物</h2>{goods}
<h2>出典と確認日</h2><ul class="src">{src}</ul><p class="note">確認日:{t["checked"]}</p>
<style>{CSS}</style><script>window.KIGEN={json.dumps(data, ensure_ascii=False)};</script><script>{JS}</script>'''
        p = page(f'/tools/{t["slug"]}/', f'{t["seo"]}|Honest Guide', t["desc"], body, extra_head=f'<script type="application/ld+json">{ld}</script>')
        made.append((p, t["title"], t["desc"]))
    return made
