# 拡張機能の「出す前チェック」

Honest Headers / Honest Cookies を Chrome ウェブストアに出す前に、必ずこれを通す。
合格(PASS)したものだけをオーナーに渡す。FAIL なら、出た項目を直してもう一度。

## 使い方

```
# 出す前(新しい版): バージョンが前回提出より大きいことも見る。合格したときだけ提出用zipを作る
python3 ext-check/check_ext.py <拡張のフォルダ> --baseline ext-check/baseline-headers.json --zip dist

# 今の版の点検だけ(バージョンの増加は見ない)
python3 ext-check/check_ext.py <拡張のフォルダ> --baseline ext-check/baseline-cookies.json --audit
```

- Honest Headers のソース: 拡張の本家リポジトリには Claude が書き込めないため、控えを honest-guide の `honest-headers-1.x` ブランチに置く。最新版(提出した版)をここに入れてからチェックする。
- Honest Cookies のソース: https://github.com/honestheaders/honest-cookies

## 何を見るか

| 見るもの | 落とす条件 |
|---|---|
| バージョン | MV3でない / 前回提出以下 |
| 権限 | baseline に無い権限が増えた。`webRequest` `scripting` `tabs` など「広く覗ける権限」と `content_scripts` は、baselineに書いても通さない |
| 通信・外部コード | `fetch` `XMLHttpRequest` `WebSocket` `sendBeacon` `eval` 外部script。コード内のURLは baseline の `allowed_url_prefixes` だけ |
| ファイル | manifest やHTMLが読むファイルが無い |
| 表示文 | 英語と日本語のキーが食い違う / コードが使うキーが無い |
| 文法・テスト | JavaScriptの文法エラー / `test/*.test.mjs` が通らない |
| 説明文 | README の権限の説明が manifest とずれる / 古い案内(BOOTHなど)が残る |
| zip | 直下に manifest が無い / 秘密や不要ファイルが入る |

「通信しない」「広く覗ける権限を使わない」は、うちの約束(Honest)そのもの。ModHeader の件(2026-07)のように、あとから更新で中身が変わっても、この関所で止まる。

## 権限を増やしたいとき

1. 本当に必要か、`declarativeNetRequest` など狭い方法でできないかを先に考える。
2. 増やすと決めたら、オーナーの決定を `/areas/new-business.md` に書き、baseline を直す(`ALWAYS_FORBIDDEN_PERMS` の権限は `check_ext.py` 自体を直す必要があり、必ず人の目に入る)。
3. ストアの説明文とプライバシーポリシーにも、増やした理由を書く。

## 次の版(Honest Headers 1.1.2 / Honest Cookies 1.0.1)でやること

どちらも「検索で見つけてもらう」ための小さな直し(調査の結果は `/areas/new-business.md` の 2026-10-10 を参照)。

1. **ストアの短い説明(132文字まで)から、他社名を外す。** Chrome公式の掲載ガイドは「競合の拡張への言及は避ける」としている。いまの Headers は `Imports ModHeader profiles.` が入っている。短い説明は機能だけにし、「ModHeaderのJSONを読み込める」は詳しい説明(本文)の1行に移す。
2. **最初のレビューを集める。** 設定画面に「ストアで評価する」リンクを1つ置く(静かなリンクだけ。見返りを出さない・押しつけるポップアップは出さない=ストアの規則)。ストアの順位は評価とインストール/アンインストールの比で決まるため、評価0件は不利。
3. **Headers のREADME・コードの案内をGumroadに直す**(出す前チェックが BOOTH の残りを見つける)。
4. 説明の1行目を「権限が少ないこと」にする(`declarativeNetRequest` と `storage` が中心、ページを読まない、通信しない)。
