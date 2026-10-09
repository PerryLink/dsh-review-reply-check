# dsh-review-reply-check — समीक्षा टिप्पणियों के उत्तर-तालिका की व्याप्ति और अभिलेख की जाँच

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-review-reply-check` समीक्षा टिप्पणियों के उत्तर की एक तालिका पढ़ता है — पांडुलिपि का हेडर और प्रत्येक टिप्पणी की एक पंक्ति — और उसी तालिका की व्याप्ति तथा अभिलेख-निरंतरता की जाँच करता है: क्या प्रत्येक टिप्पणी का पाठ दर्ज है, क्या टिप्पणी लिखी होने पर उस पंक्ति में लेखक का उत्तर भी है, क्या उत्तर में किया गया संशोधन और उसका स्थान लिखा है, क्या प्रत्येक निपटान-स्थिति आपके द्वारा कॉन्फ़िगर शब्दावली से ली गई है, क्या उत्तर की तारीखें तालिका में ही लिखी समीक्षा-सीमा के भीतर हैं, क्या तालिका का हेडर अपनी पांडुलिपि और समीक्षा-चक्र बताता है, और क्या टिप्पणी-क्रमांक दोहराए नहीं गए हैं।

## आउटपुट कैसा दिखता है

![Terminal demo of dsh-review-reply-check: real output over its RR-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-review-reply-check/main/docs/assets/dsh-review-reply-check-demo.png)

इस प्लगइन का अपने ही `RR-001` टेस्ट फ़िक्स्चर पर वास्तविक आउटपुट — कोई नकली चित्र नहीं। नियम-पैक उद्धरण नहीं गढ़ता, इसलिए हर निष्कर्ष लागू किए गए खंड का नाम और यह भी बताता है कि उसका मूल पाठ इस बार प्राप्त नहीं हुआ।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| एक पंक्ति में लेखक का उत्तर है, पर टिप्पणी का पाठ रखने वाली कोशिका खाली है। | `RR-001` हर पंक्ति में टिप्पणी का पाठ चाहता है: उसके बिना उत्तर का कोई विषय नहीं रहता और संपादक यह नहीं देख पाता कि उत्तर किस टिप्पणी का है। नियम केवल यह देखता है कि कोशिका भरी है; यह नहीं आँकता कि टिप्पणी उचित है या वह शैक्षणिक मतभेद की बात है। |
| टिप्पणी दर्ज है, पर लेखक के उत्तर की कोशिका अब भी खाली है — क्या यह दर्ज होता है? | हाँ। `RR-002` हर उस पंक्ति में उत्तर की अपेक्षा करता है जिसमें टिप्पणी लिखी हो, क्योंकि टिप्पणी को चुपचाप छोड़ देना और समीक्षक द्वारा स्वीकार्य असहमति दो अलग बातें हैं। यह केवल देखता है कि उत्तर की कोशिका भरी है, यह नहीं कि उत्तर पर्याप्त है या समीक्षक को संतुष्ट करता है; जिस टिप्पणी पर वास्तव में कोई बदलाव आवश्यक न हो, उसके लिए नियम-संग्रह उस कोशिका में कारण लिखने की सलाह देता है, खाली छोड़ने की नहीं। |
| उत्तर में लिखा है कि पाठ संशोधित कर दिया गया, पर संशोधन विवरण और स्थान का कॉलम खाली है। | `RR-003` हर उस पंक्ति में `revision` और `revisionLocation` दोनों की अपेक्षा करता है जिसमें `response` भरा हो। यह देखता है कि दोनों कोशिकाएँ लिखी गई हैं, यह नहीं कि बदलाव वहीं है जहाँ उनमें लिखा है — प्लगइन पांडुलिपि को कभी नहीं देखता, इसलिए ठीक पृष्ठ-पंक्ति बताने वाला, पर वास्तव में न होने वाला संशोधन विवरण भी पास हो जाता है। |
| हर पंक्ति में निपटान-स्थिति भरी है। मान स्वीकार्य है या नहीं, यह उपकरण कैसे तय करता है? | `RR-004` `status` कॉलम के मान की तुलना उस सूची से करता है जो आप कॉन्फ़िगर करते हैं। यह सूची खाली आती है, अर्थात् कॉन्फ़िगर नहीं है, इसलिए जब तक आप उसे न भरें, यह नियम चुपचाप पास होने के बजाय `skipped` में स्वयं को दर्ज करता है। यह केवल देखता है कि मान आपकी सूची में है; यह नहीं तय करता कि कोई स्थिति यह दर्शाती है कि टिप्पणी ठीक से निपटाई गई। संस्थागत कॉन्फ़िगरेशन वाला नियम होने के कारण इसकी गंभीरता `info` तक सीमित है। |
| उत्तर की तारीख सीमा-कॉलम के बाद की है — क्या इसका अर्थ है कि संशोधन विलंब से आया? | `RR-005` `respondedAt` की तुलना तालिका में ही लिखी `dueAt` से करता है, और मेल न खाने का अर्थ केवल यह है कि दोनों आपके दर्ज की गई सीमा से मेल नहीं खाते, यह नहीं कि संशोधन देर से आया, क्योंकि सीमाएँ जर्नल के अनुसार बदलती हैं और लेखक अवधि-विस्तार माँग सकता है। कोई दिन-संख्या अंदर नहीं बैठाई गई और कोई गणना नहीं होती: `dueAt` खाली होने पर यह नियम कोई सीमा मान लेने के बजाय `skipped` में स्वयं को दर्ज करता है। |
| दो समीक्षकों की टिप्पणियाँ एक साथ दर्ज हुईं और दोनों की गिनती 1 से शुरू होती है, इसलिए एक टिप्पणी-क्रमांक दो बार आता है। | `RR-007` `commentNo` में दोहराया गया मान दर्ज करता है, क्योंकि दोहरी संख्या व्याप्ति की गिनती को गलत बनाती है और समीक्षा-फ़ॉर्म से मेल तोड़ देती है। एक साथ दर्ज करते समय संख्या में समीक्षक जोड़ें — `R1-3`, `R2-1` — जिससे वे अद्वितीय रहें; यह नियम संख्याओं की तुलना वैसे ही करता है जैसे वे लिखी हैं, न मिलाता है न नए सिरे से क्रमांकित करता है। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
|---|---|---|
| 《中国高校科技期刊编排规范》 | 现行版本与条号本次未核实 | RR-001, RR-002, RR-003, RR-006, RR-007 |
| 本期刊同行评议与返修规定（本机构配置） | 无统一标准（本条依据为本机构配置的状态口径） | RR-004 |
| 本期刊同行评议与返修规定（本机构配置） | 无统一标准（本条依据为台账写明的返修期限） | RR-005 |

**Boundary:** this plugin checks a **审稿意见逐条回应表** for coverage and evidence — that every comment is
recorded, that every comment carries an author response, that a response states the revision made and where it was
made, that the handling status comes from your vocabulary, that response dates fall inside the revision deadline
the register states, that the sheet names its manuscript and review round, and that comment numbers are unique. It
does **not** decide whether a response is adequate, whether the revision is sufficient, or whether the manuscript
should be accepted.

> ### ⚠️ What this plugin can and cannot see
>
> **It never sees the manuscript.** It can check that a response says *where* a change was made — never that the
> change is there, and never that it addresses the comment. `RR-003`'s note and the troubleshooting section say
> so: a confident, well-located, entirely fictional revision note passes this plugin.
>
> The relation between "no response" and "disagreement" is the point of `RR-002`: a reviewer can accept an author's
> disagreement but not a comment passed over in silence, so **coverage** is the most direct indicator of revision
> quality. The rule therefore fires on an empty response cell — and its note advises recording the reason rather
> than leaving the cell blank when a comment genuinely needs no change.
>
> **No revision deadline is built in.** Periods differ by journal and authors may ask for extensions, so `RR-005`
> compares the response date against the **deadline written in the register**, and reports itself in `skipped`
> when that column is empty. A finding means "this disagrees with the deadline you recorded", never "you were
> late". The status vocabulary ships **empty** for the same reason.
>
> **Every `excerpt` in the rule pack says, in so many words, that the clause text was not obtained.** The regime
> lives in GB/T 7713.1, the Chinese university journal editing standard, and each journal's peer-review rules. The
> verification pass could not retrieve verbatim clause text, so the pack states the gap in the `excerpt` field
> itself and keeps every rule at `warn` or `info`. **When the texts are in hand, replace each `excerpt` with the
> real clause and raise `kind` to `direct`.**

## Compatibility

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-review-reply-check
dsh --profile <name> --dump-config | grep 'dsh-review-reply-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/review-reply-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-review-reply-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-review-reply-check contributors.
