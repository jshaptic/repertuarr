"""
Per-language phrase overlays for non-English catalogs.

Supplies style-specific thinking variants and shared webhook/UI strings
(recommend_button, download_ready, play_button) used when generating
bot/phrases/data/{lang}.yaml files. English (en) is the canonical base
catalog and is not included here.
"""

from __future__ import annotations

from typing import Any, Dict

LANG_OVERLAYS: Dict[str, Dict[str, Any]] = {
    "es": {
        "styles": {
            "default": {"thinking": [
                "Déjame pensar en algo bueno...",
                "Hmm, voy a buscar algo que valga la pena...",
                "Un momento — elijo algo especial...",
            ]},
            "casual": {"thinking": [
                "Espera, voy a encontrar algo genial...",
                "Dame un segundo — viene algo bueno...",
                "Vale, déjame buscarte un acierto...",
            ]},
            "warm": {"thinking": [
                "Déjame encontrar algo que de verdad disfrutes...",
                "Voy a elegir algo acogedor y bueno para ti...",
                "Un momento — quiero que sea una gran elección...",
            ]},
            "witty": {"thinking": [
                "Consultando mi algoritmo científico del gusto...",
                "Tirando los dados de recomendaciones — en sentido figurado...",
                "Voy a saquear el cofre de lo bueno...",
            ]},
            "cinephile": {"thinking": [
                "Curando una lista corta de los buenos estantes...",
                "Déjame hojear el catálogo en busca de algo digno...",
                "Un momento — seleccionando entre lo mejor...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Recomiéndame algo",
            ],
            "download_ready": [
                "🎉 *{title}* está lista\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* se ha descargado!",
            ],
            "play_button": [
                "▶️ Ver en Jellyfin",
            ],
        },
    },
    "fr": {
        "styles": {
            "default": {"thinking": [
                "Laisse-moi penser à quelque chose de bien...",
                "Hmm, je vais trouver quelque chose qui vaut le coup...",
                "Un instant — je choisis quelque chose de spécial...",
            ]},
            "casual": {"thinking": [
                "Attends, je vais dénicher un truc sympa...",
                "Une seconde — quelque chose de bien arrive...",
                "OK, laisse-moi te trouver un bon choix...",
            ]},
            "warm": {"thinking": [
                "Je vais trouver quelque chose que tu apprécieras vraiment...",
                "Je choisis quelque chose de doux et agréable pour toi...",
                "Un instant — je veux que ce soit un super choix...",
            ]},
            "witty": {"thinking": [
                "Consultation de mon algorithme de goût très scientifique...",
                "Je lance les dés des recommandations — métaphoriquement...",
                "Je fouille le coffre du bon matos pour toi...",
            ]},
            "cinephile": {"thinking": [
                "Je compose une short-list depuis les bonnes étagères...",
                "Je parcours le catalogue pour quelque chose de digne...",
                "Un instant — je sélectionne parmi le meilleur...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Recommande-moi quelque chose",
            ],
            "download_ready": [
                "🎉 *{title}* est prêt \\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* a été téléchargé !",
            ],
            "play_button": [
                "▶️ Regarder sur Jellyfin",
            ],
        },
    },
    "de": {
        "styles": {
            "default": {"thinking": [
                "Lass mich über etwas Gutes nachdenken...",
                "Hmm, ich suche etwas, das sich lohnt...",
                "Einen Moment — ich wähle etwas Besonderes...",
            ]},
            "casual": {"thinking": [
                "Warte, ich grabe was Cooles aus...",
                "Gib mir 'ne Sekunde — gleich kommt was Gutes...",
                "Okay okay, ich such dir einen Treffer...",
            ]},
            "warm": {"thinking": [
                "Ich such was, das dir wirklich gefällt...",
                "Ich wähle was Gemütliches und Gutes für dich...",
                "Einen Moment — das soll ein toller Tipp werden...",
            ]},
            "witty": {"thinking": [
                "Konsultiere meinen sehr wissenschaftlichen Geschmacksalgorithmus...",
                "Würfle mit den Empfehlungswürfeln — metaphorisch...",
                "Ich durchkämme den Tresor des Guten für dich...",
            ]},
            "cinephile": {"thinking": [
                "Kuratiere eine Shortlist von den guten Regalen...",
                "Ich blättere im Katalog nach etwas Würdigem...",
                "Einen Moment — Auswahl aus den feineren Stücken...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Empfiehl mir etwas",
            ],
            "download_ready": [
                "🎉 *{title}* ist bereit\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* wurde heruntergeladen!",
            ],
            "play_button": [
                "▶️ Auf Jellyfin ansehen",
            ],
        },
    },
    "it": {
        "styles": {
            "default": {"thinking": [
                "Fammi pensare a qualcosa di buono...",
                "Hmm, cerco qualcosa che valga la pena...",
                "Un attimo — scelgo qualcosa di speciale...",
            ]},
            "casual": {"thinking": [
                "Aspetta, trovo qualcosa di figo...",
                "Dammi un secondo — arriva qualcosa di buono...",
                "Ok ok, ti cerco un colpo vincente...",
            ]},
            "warm": {"thinking": [
                "Cerco qualcosa che ti piacerà davvero...",
                "Scelgo qualcosa di accogliente e buono per te...",
                "Un attimo — voglio che sia una scelta azzeccata...",
            ]},
            "witty": {"thinking": [
                "Consulto il mio algoritmo del gusto molto scientifico...",
                "Lancio i dadi delle raccomandazioni — metaforicamente...",
                "Saccheggio il caveau delle cose buone per te...",
            ]},
            "cinephile": {"thinking": [
                "Curo una shortlist dagli scaffali migliori...",
                "Sfoglio il catalogo in cerca di qualcosa di degno...",
                "Un attimo — seleziono tra le scelte più raffinate...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Consigliami qualcosa",
            ],
            "download_ready": [
                "🎉 *{title}* è pronto\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* è stato scaricato!",
            ],
            "play_button": [
                "▶️ Guarda su Jellyfin",
            ],
        },
    },
    "pt": {
        "styles": {
            "default": {"thinking": [
                "Deixa eu pensar em algo legal...",
                "Hmm, vou achar algo que valha a pena...",
                "Um momento — escolhendo algo especial...",
            ]},
            "casual": {"thinking": [
                "Pera, vou achar algo massa...",
                "Me dá um segundo — vem coisa boa aí...",
                "Beleza, deixa eu achar um acerto pra você...",
            ]},
            "warm": {"thinking": [
                "Vou achar algo que você vai curtir de verdade...",
                "Escolho algo aconchegante e bom pra você...",
                "Um momento — quero que seja uma ótima escolha...",
            ]},
            "witty": {"thinking": [
                "Consultando meu algoritmo científico de gosto...",
                "Jogando os dados das recomendações — metaforicamente...",
                "Vou vasculhar o cofre das coisas boas pra você...",
            ]},
            "cinephile": {"thinking": [
                "Curando uma lista curta das prateleiras boas...",
                "Deixa eu folhear o catálogo em busca de algo digno...",
                "Um momento — selecionando entre as melhores opções...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Me recomenda algo",
            ],
            "download_ready": [
                "🎉 *{title}* está pronto\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* foi baixado!",
            ],
            "play_button": [
                "▶️ Assistir no Jellyfin",
            ],
        },
    },
    "ru": {
        "styles": {
            "default": {"thinking": [
                "Дай-ка подумаю о чём-нибудь хорошем...",
                "Хм, поищу что-то, на что стоит потратить время...",
                "Секунду — подберу что-то особенное...",
            ]},
            "casual": {"thinking": [
                "Погоди, сейчас накопаю что-нибудь крутое...",
                "Дай секунду — сейчас будет что-то хорошее...",
                "Ладно-ладно, сейчас найду тебе удачный вариант...",
            ]},
            "warm": {"thinking": [
                "Подберу что-то, что тебе правда понравится...",
                "Выберу что-нибудь уютное и хорошее для тебя...",
                "Секунду — хочу, чтобы это был отличный выбор...",
            ]},
            "witty": {"thinking": [
                "Консультируюсь с моим очень научным алгоритмом вкуса...",
                "Бросаю кости рекомендаций — метафорически...",
                "Сейчас обыщу хранилище хорошего для тебя...",
            ]},
            "cinephile": {"thinking": [
                "Составляю короткий список с лучших полок...",
                "Пролистаю каталог в поисках чего-то достойного...",
                "Секунду — выбираю из более тонких вариантов...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Порекомендуй что-нибудь",
            ],
            "download_ready": [
                "🎉 *{title}* готов\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* загружен!",
            ],
            "play_button": [
                "▶️ Смотреть в Jellyfin",
            ],
        },
    },
    "ja": {
        "styles": {
            "default": {"thinking": [
                "いいものを考えてみるね...",
                "うーん、見る価値のあるものを探してみる...",
                "ちょっと待って — 特別なものを選ぶね...",
            ]},
            "casual": {"thinking": [
                "待ってて、いいの掘り出してくる...",
                "ちょい待ち — いいの見つかるよ...",
                "オッケー、いいやつ探してくるね...",
            ]},
            "warm": {"thinking": [
                "きっと気に入ってもらえるものを探すね...",
                "ほっこりしていて良いものを選ぶよ...",
                "ちょっと待って — いいおすすめにしたいから...",
            ]},
            "witty": {"thinking": [
                "非常に科学的な趣味アルゴリズムに相談中...",
                "おすすめサイコロを振ってる — 比喩的に...",
                "良作の金庫を漁ってくるね...",
            ]},
            "cinephile": {"thinking": [
                "良い棚からショートリストを作ってる...",
                "カタログを眺めてふさわしいものを探す...",
                "ちょっと待って — 上質な候補から選ぶね...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "何かおすすめして",
            ],
            "download_ready": [
                "🎉 *{title}* の準備ができました\\！ [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* がダウンロードされました！",
            ],
            "play_button": [
                "▶️ Jellyfinで視聴",
            ],
        },
    },
    "zh": {
        "styles": {
            "default": {"thinking": [
                "让我想想有什么好的...",
                "嗯，我来找点值得看的东西...",
                "稍等 — 正在挑点特别的...",
            ]},
            "casual": {"thinking": [
                "等等，我去挖点好看的...",
                "给我一秒 — 好东西马上来...",
                "行行行，给你找个靠谱的...",
            ]},
            "warm": {"thinking": [
                "我来找点你肯定会喜欢的...",
                "给你挑点温馨又好看的...",
                "稍等 — 我想给你个超棒的选择...",
            ]},
            "witty": {"thinking": [
                "正在咨询我超科学的品味算法...",
                "掷推荐骰子中 — 比喻意义上的...",
                "我去好片保险柜里翻翻...",
            ]},
            "cinephile": {"thinking": [
                "正在从好片架上整理一份短名单...",
                "翻翻片单，找点配得上你的...",
                "稍等 — 从精品里挑一个...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "给我推荐点什么",
            ],
            "download_ready": [
                "🎉 *{title}* 已就绪\\！ [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* 已下载！",
            ],
            "play_button": [
                "▶️ 在Jellyfin上观看",
            ],
        },
    },
    "ko": {
        "styles": {
            "default": {"thinking": [
                "뭔가 좋은 걸 생각해볼게...",
                "음, 볼 만한 걸 찾아볼게...",
                "잠깐만 — 특별한 걸 골라볼게...",
            ]},
            "casual": {"thinking": [
                "잠깐, 멋진 거 하나 파볼게...",
                "1초만 — 좋은 거 곧 나올 거야...",
                "알았어, 괜찮은 거 하나 찾아볼게...",
            ]},
            "warm": {"thinking": [
                "정말 마음에 들 만한 걸 찾아볼게...",
                "편안하고 좋은 걸 골라줄게...",
                "잠깐만 — 정말 좋은 추천이 되게 할게...",
            ]},
            "witty": {"thinking": [
                "아주 과학적인 취향 알고리즘에 문의 중...",
                "추천 주사위 굴리는 중 — 비유적으로...",
                "좋은 작품 금고를 뒤져볼게...",
            ]},
            "cinephile": {"thinking": [
                "좋은 선반에서 숏리스트를 만들고 있어...",
                "카탈로그를 넘기며 볼 만한 걸 찾아볼게...",
                "잠깐만 — 더 괜찮은 후보 중에서 고를게...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "뭔가 추천해줘",
            ],
            "download_ready": [
                "🎉 *{title}* 준비 완료\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* 다운로드 완료!",
            ],
            "play_button": [
                "▶️ Jellyfin에서 시청",
            ],
        },
    },
    "ar": {
        "styles": {
            "default": {"thinking": [
                "دعني أفكر في شيء جيد...",
                "همم، سأبحث عن شيء يستحق وقتك...",
                "لحظة — أختار شيئًا مميزًا...",
            ]},
            "casual": {"thinking": [
                "انتظر، سأجد شيئًا رائعًا...",
                "أعطني ثانية — شيء جيد قادم...",
                "حسنًا، دعني أجد لك خيارًا ممتازًا...",
            ]},
            "warm": {"thinking": [
                "سأجد شيئًا ستستمتع به حقًا...",
                "سأختار شيئًا دافئًا وجيدًا لك...",
                "لحظة — أريد أن يكون اختيارًا رائعًا...",
            ]},
            "witty": {"thinking": [
                "أستشير خوارزمية ذوقي العلمية جدًا...",
                "أرمي نرد التوصيات — مجازيًا...",
                "سأفتش خزنة الأشياء الجيدة من أجلك...",
            ]},
            "cinephile": {"thinking": [
                "أعد قائمة قصيرة من الرفوف الجيدة...",
                "أتصفح الكتالوج بحثًا عن شيء يستحق...",
                "لحظة — أختار من الخيارات الأرقى...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "اقترح علي شيئًا",
            ],
            "download_ready": [
                "🎉 *{title}* جاهز\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 تم تحميل *{title}*!",
            ],
            "play_button": [
                "▶️ شاهد على Jellyfin",
            ],
        },
    },
    "hi": {
        "styles": {
            "default": {"thinking": [
                "मुझे कुछ अच्छा सोचने दो...",
                "हम्म, कुछ ऐसा ढूँढता हूँ जो देखने लायक हो...",
                "एक पल — कुछ खास चुन रहा हूँ...",
            ]},
            "casual": {"thinking": [
                "रुको, कुछ धासू ढूँढता हूँ...",
                "एक सेकंड दो — अच्छी चीज़ आ रही है...",
                "ठीक है, तुम्हारे लिए एक बढ़िया विकल्प ढूँढता हूँ...",
            ]},
            "warm": {"thinking": [
                "कुछ ऐसा ढूँढता हूँ जो तुम्हें सच में पसंद आए...",
                "तुम्हारे लिए कुछ आरामदायक और अच्छा चुनता हूँ...",
                "एक पल — यह एक शानदार सुझाव होना चाहिए...",
            ]},
            "witty": {"thinking": [
                "अपने बहुत वैज्ञानिक स्वाद एल्गोरिदम से सलाह ले रहा हूँ...",
                "सिफ़ारिश के पासे फेंक रहा हूँ — रूपक के तौर पर...",
                "अच्छी चीज़ों के खज़ाने में झाँकता हूँ...",
            ]},
            "cinephile": {"thinking": [
                "अच्छी शेल्फ़ से शॉर्टलिस्ट बना रहा हूँ...",
                "कैटलॉग में कुछ योग्य ढूँढ रहा हूँ...",
                "एक पल — बेहतर विकल्पों में से चुन रहा हूँ...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "मुझे कुछ सुझाओ",
            ],
            "download_ready": [
                "🎉 *{title}* तैयार है\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* डाउनलोड हो गया!",
            ],
            "play_button": [
                "▶️ Jellyfin पर देखें",
            ],
        },
    },
    "tr": {
        "styles": {
            "default": {"thinking": [
                "İyi bir şey düşüneyim...",
                "Hmm, izlemeye değer bir şey bulayım...",
                "Bir dakika — özel bir şey seçiyorum...",
            ]},
            "casual": {"thinking": [
                "Bekle, havalı bir şey bulayım...",
                "Bir saniye ver — güzel bir şey geliyor...",
                "Tamam tamam, sana iyi bir seçenek bulayım...",
            ]},
            "warm": {"thinking": [
                "Gerçekten hoşuna gidecek bir şey bulayım...",
                "Senin için sıcak ve güzel bir şey seçiyorum...",
                "Bir dakika — harika bir öneri olsun istiyorum...",
            ]},
            "witty": {"thinking": [
                "Çok bilimsel zevk algoritmama danışıyorum...",
                "Öneri zarlarını atıyorum — mecazi anlamda...",
                "İyi şeyler kasasını senin için karıştırıyorum...",
            ]},
            "cinephile": {"thinking": [
                "İyi raflardan kısa bir liste hazırlıyorum...",
                "Kataloğa göz atıp layık bir şey arıyorum...",
                "Bir dakika — daha seçkin adaylar arasından seçiyorum...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Bana bir şey öner",
            ],
            "download_ready": [
                "🎉 *{title}* hazır\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* indirildi!",
            ],
            "play_button": [
                "▶️ Jellyfin'de izle",
            ],
        },
    },
    "pl": {
        "styles": {
            "default": {"thinking": [
                "Pomyślę o czymś fajnym...",
                "Hmm, poszukam czegoś wartego uwagi...",
                "Chwila — wybieram coś wyjątkowego...",
            ]},
            "casual": {"thinking": [
                "Czekaj, wykopię coś fajnego...",
                "Daj mi sekundę — zaraz będzie coś dobrego...",
                "Dobra dobra, znajdę ci trafiony wybór...",
            ]},
            "warm": {"thinking": [
                "Znajdę coś, co naprawdę ci się spodoba...",
                "Wybiorę coś przytulnego i dobrego dla ciebie...",
                "Chwila — chcę, żeby to był świetny wybór...",
            ]},
            "witty": {"thinking": [
                "Konsultuję się z moim bardzo naukowym algorytmem gustu...",
                "Rzucam kostkami rekomendacji — metaforycznie...",
                "Przeszukam skarbiec dobrych rzeczy dla ciebie...",
            ]},
            "cinephile": {"thinking": [
                "Układam krótką listę z dobrych półek...",
                "Przeglądam katalog w poszukiwaniu czegoś godnego...",
                "Chwila — wybieram spośród lepszych propozycji...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Poleć mi coś",
            ],
            "download_ready": [
                "🎉 *{title}* jest gotowy\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* został pobrany!",
            ],
            "play_button": [
                "▶️ Oglądaj na Jellyfin",
            ],
        },
    },
    "nl": {
        "styles": {
            "default": {"thinking": [
                "Laat me even nadenken over iets goeds...",
                "Hmm, ik zoek iets dat de moeite waard is...",
                "Even geduld — ik kies iets bijzonders...",
            ]},
            "casual": {"thinking": [
                "Wacht even, ik graaf iets cools op...",
                "Geef me een seconde — er komt iets goeds aan...",
                "Oké oké, ik zoek een winnaar voor je...",
            ]},
            "warm": {"thinking": [
                "Ik zoek iets waar je echt van geniet...",
                "Ik kies iets gezelligs en goeds voor je...",
                "Even geduld — dit moet een topkeuze worden...",
            ]},
            "witty": {"thinking": [
                "Raadpleeg mijn zeer wetenschappelijke smaakalgoritme...",
                "Gooi met de aanbevelingsdobbelstenen — figuurlijk...",
                "Ik doorzoek de kluis met goede spullen voor je...",
            ]},
            "cinephile": {"thinking": [
                "Stel een shortlist samen van de goede schappen...",
                "Ik blader door de catalogus naar iets waardigs...",
                "Even geduld — selectie uit de fijnere keuzes...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Beveel me iets aan",
            ],
            "download_ready": [
                "🎉 *{title}* is klaar\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* is gedownload!",
            ],
            "play_button": [
                "▶️ Bekijk op Jellyfin",
            ],
        },
    },
    "sv": {
        "styles": {
            "default": {"thinking": [
                "Låt mig tänka på något bra...",
                "Hmm, jag letar efter något värt din tid...",
                "Ett ögonblick — väljer något speciellt...",
            ]},
            "casual": {"thinking": [
                "Vänta, jag gräver fram något coolt...",
                "Ge mig en sekund — något bra kommer...",
                "Okej okej, jag hittar en vinnare åt dig...",
            ]},
            "warm": {"thinking": [
                "Jag hittar något du verkligen kommer gilla...",
                "Jag väljer något mysigt och bra åt dig...",
                "Ett ögonblick — det här ska bli ett toppval...",
            ]},
            "witty": {"thinking": [
                "Konsulterar min mycket vetenskapliga smakalgoritm...",
                "Kastar rekommendationstärningarna — metaforiskt...",
                "Jag rotar i valvet med bra grejer åt dig...",
            ]},
            "cinephile": {"thinking": [
                "Kurerar en kortlista från de bra hyllorna...",
                "Jag bläddrar i katalogen efter något värdigt...",
                "Ett ögonblick — väljer bland de finare alternativen...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Rekommendera något åt mig",
            ],
            "download_ready": [
                "🎉 *{title}* är redo\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* har laddats ner!",
            ],
            "play_button": [
                "▶️ Titta på Jellyfin",
            ],
        },
    },
    "da": {
        "styles": {
            "default": {"thinking": [
                "Lad mig tænke over noget godt...",
                "Hmm, jeg finder noget, der er tiden værd...",
                "Et øjeblik — vælger noget særligt...",
            ]},
            "casual": {"thinking": [
                "Vent, jeg graver noget fedt frem...",
                "Giv mig et sekund — noget godt er på vej...",
                "Okay okay, jeg finder en vinder til dig...",
            ]},
            "warm": {"thinking": [
                "Jeg finder noget, du virkelig vil nyde...",
                "Jeg vælger noget hyggeligt og godt til dig...",
                "Et øjeblik — det skal blive et godt valg...",
            ]},
            "witty": {"thinking": [
                "Konsulterer min meget videnskabelige smagsalgoritme...",
                "Kaster anbefalingsterningerne — metaforisk...",
                "Jeg roder i kisten med gode sager til dig...",
            ]},
            "cinephile": {"thinking": [
                "Kurerer en kortliste fra de gode hylder...",
                "Jeg bladrer i kataloget efter noget værdigt...",
                "Et øjeblik — vælger blandt de finere valg...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Anbefal mig noget",
            ],
            "download_ready": [
                "🎉 *{title}* er klar\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* er blevet downloadet!",
            ],
            "play_button": [
                "▶️ Se på Jellyfin",
            ],
        },
    },
    "no": {
        "styles": {
            "default": {"thinking": [
                "La meg tenke på noe bra...",
                "Hmm, jeg finner noe som er verdt tiden din...",
                "Et øyeblikk — velger noe spesielt...",
            ]},
            "casual": {"thinking": [
                "Vent, jeg graver frem noe kult...",
                "Gi meg et sekund — noe bra kommer...",
                "Ok ok, jeg finner en vinner til deg...",
            ]},
            "warm": {"thinking": [
                "Jeg finner noe du virkelig vil like...",
                "Jeg velger noe koselig og bra for deg...",
                "Et øyeblikk — dette skal bli et godt valg...",
            ]},
            "witty": {"thinking": [
                "Konsulterer min svært vitenskapelige smaksalgoritme...",
                "Kaster anbefalingsterningene — metaforisk...",
                "Jeg roter i kisten med gode ting for deg...",
            ]},
            "cinephile": {"thinking": [
                "Kurerer en kortliste fra de gode hyllene...",
                "Jeg blar i katalogen etter noe verdig...",
                "Et øyeblikk — velger blant de finere alternativene...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Anbefal meg noe",
            ],
            "download_ready": [
                "🎉 *{title}* er klar\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* er lastet ned!",
            ],
            "play_button": [
                "▶️ Se på Jellyfin",
            ],
        },
    },
    "fi": {
        "styles": {
            "default": {"thinking": [
                "Anna mun miettiä jotain hyvää...",
                "Hmm, etsin jotain katsomisen arvoista...",
                "Hetki — valitsen jotain erityistä...",
            ]},
            "casual": {"thinking": [
                "Oota, kaivan jotain siistiä...",
                "Anna mulle sekunti — hyvää tulossa...",
                "Okei okei, etsin sulle osuman...",
            ]},
            "warm": {"thinking": [
                "Etsin jotain mistä oikeasti pidät...",
                "Valitsen sulle jotain mukavaa ja hyvää...",
                "Hetki — haluan tästä loistavan valinnan...",
            ]},
            "witty": {"thinking": [
                "Konsultoin hyvin tieteellistä makualgoritmiani...",
                "Heitän suositusnoppaa — metaforisesti...",
                "Kaivan hyvien juttujen holvia sulle...",
            ]},
            "cinephile": {"thinking": [
                "Kuraattori lyhytlistaa hyviltä hyllyiltä...",
                "Selaan katalogia etsien jotain arvokasta...",
                "Hetki — valitsen hienompien vaihtoehtojen joukosta...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Suosittele mulle jotain",
            ],
            "download_ready": [
                "🎉 *{title}* on valmis\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* on ladattu!",
            ],
            "play_button": [
                "▶️ Katso Jellyfinissä",
            ],
        },
    },
    "cs": {
        "styles": {
            "default": {"thinking": [
                "Nech mě přemýšlet o něčem dobrém...",
                "Hmm, najdu něco, co stojí za to...",
                "Chvilku — vybírám něco speciálního...",
            ]},
            "casual": {"thinking": [
                "Počkej, vykopu něco super...",
                "Dej mi vteřinu — něco dobrého přijde...",
                "Dobře dobře, najdu ti trefu...",
            ]},
            "warm": {"thinking": [
                "Najdu něco, co si opravdu užiješ...",
                "Vyberu ti něco útulného a dobrého...",
                "Chvilku — chci, aby to byl skvělý tip...",
            ]},
            "witty": {"thinking": [
                "Konzultuji svůj velmi vědecký algoritmus vkusu...",
                "Házím kostkami doporučení — metaforicky...",
                "Prohrabu trezor dobrých věcí pro tebe...",
            ]},
            "cinephile": {"thinking": [
                "Sestavuji krátký seznam z dobrých polic...",
                "Prolistovávám katalog a hledám něco hodného...",
                "Chvilku — vybírám z jemnějších tipů...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Doporuč mi něco",
            ],
            "download_ready": [
                "🎉 *{title}* je připraven\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* byl stažen!",
            ],
            "play_button": [
                "▶️ Sledovat na Jellyfin",
            ],
        },
    },
    "el": {
        "styles": {
            "default": {"thinking": [
                "Άσε με να σκεφτώ κάτι καλό...",
                "Χμ, θα βρω κάτι που αξίζει τον χρόνο σου...",
                "Μια στιγμή — διαλέγω κάτι ξεχωριστό...",
            ]},
            "casual": {"thinking": [
                "Περίμενε, θα βρω κάτι ωραίο...",
                "Δώσε μου ένα δευτερόλεπτο — έρχεται κάτι καλό...",
                "Εντάξει εντάξει, θα σου βρω έναν νικητή...",
            ]},
            "warm": {"thinking": [
                "Θα βρω κάτι που θα απολαύσεις πραγματικά...",
                "Διαλέγω κάτι ζεστό και καλό για σένα...",
                "Μια στιγμή — θέλω να είναι μια εξαιρετική επιλογή...",
            ]},
            "witty": {"thinking": [
                "Συμβουλεύομαι τον πολύ επιστημονικό αλγόριθμο γούστου μου...",
                "Ρίχνω τα ζάρια των προτάσεων — μεταφορικά...",
                "Θα ψάξω στο θησαυροφυλάκιο των καλών για σένα...",
            ]},
            "cinephile": {"thinking": [
                "Επιμελούμαι μια σύντομη λίστα από τα καλά ράφια...",
                "Ξεφυλλίζω τον κατάλογο για κάτι άξιο...",
                "Μια στιγμή — επιλέγω από τις πιο εκλεκτές προτάσεις...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Πρότεινέ μου κάτι",
            ],
            "download_ready": [
                "🎉 *{title}* είναι έτοιμο\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 Το *{title}* κατέβηκε!",
            ],
            "play_button": [
                "▶️ Δες στο Jellyfin",
            ],
        },
    },
    "he": {
        "styles": {
            "default": {"thinking": [
                "תן לי לחשוב על משהו טוב...",
                "הממ, אחפש משהו ששווה את הזמן שלך...",
                "רגע — בוחר משהו מיוחד...",
            ]},
            "casual": {"thinking": [
                "חכה, אחפש משהו מגניב...",
                "תן לי שנייה — משהו טוב בדרך...",
                "אוקיי אוקיי, אמצא לך בחירה מנצחת...",
            ]},
            "warm": {"thinking": [
                "אמצא משהו שבאמת תהנה ממנו...",
                "אבחר משהו נעים וטוב בשבילך...",
                "רגע — אני רוצה שזה יהיה בחירה מעולה...",
            ]},
            "witty": {"thinking": [
                "מתייעץ עם אלגוריתם הטעם המדעי שלי...",
                "זורק את קוביות ההמלצות — באופן מטאפורי...",
                "אחפש בכספת של הדברים הטובים בשבילך...",
            ]},
            "cinephile": {"thinking": [
                "מרכיב רשימה קצרה מהמדפים הטובים...",
                "עובר על הקטלוג בחיפוש אחר משהו ראוי...",
                "רגע — בוחר מתוך האפשרויות המעודנות...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "המלץ לי על משהו",
            ],
            "download_ready": [
                "🎉 *{title}* מוכן\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* הורד!",
            ],
            "play_button": [
                "▶️ צפה ב-Jellyfin",
            ],
        },
    },
    "th": {
        "styles": {
            "default": {"thinking": [
                "ให้ฉันคิดหาอะไรดีๆ สักหน่อย...",
                "อืม ขอหาอะไรที่คุ้มค่าเวลาหน่อย...",
                "รอแป๊บ — กำลังเลือกอะไรพิเศษๆ...",
            ]},
            "casual": {"thinking": [
                "เดี๋ยวนะ ขอขุดอะไรเจ๋งๆ มา...",
                "ขอเวลาสักวิ — ของดีกำลังมา...",
                "โอเคๆ ขอหาอะไรที่ใช่ให้หน่อย...",
            ]},
            "warm": {"thinking": [
                "ขอหาอะไรที่คุณจะชอบจริงๆ...",
                "เลือกอะไรอบอุ่นและดีๆ ให้คุณ...",
                "รอแป๊บ — อยากให้เป็นตัวเลือกที่เยี่ยม...",
            ]},
            "witty": {"thinking": [
                "กำลังปรึกษาอัลกอริทึมรสนิยมสุดวิทยาศาสตร์ของฉัน...",
                "ทอยลูกเต๋าแนะนำ — ในเชิงเปรียบเทียบ...",
                "ขอค้นหาในคลังของดีให้หน่อย...",
            ]},
            "cinephile": {"thinking": [
                "กำลังคัดรายการสั้นจากชั้นดีๆ...",
                "เปิดดูแคตตาล็อกหาอะไรที่คู่ควร...",
                "รอแป๊บ — เลือกจากตัวเลือกชั้นดี...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "แนะนำอะไรให้หน่อย",
            ],
            "download_ready": [
                "🎉 *{title}* พร้อมแล้ว\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ดาวน์โหลดเรียบร้อย!",
            ],
            "play_button": [
                "▶️ ดูบน Jellyfin",
            ],
        },
    },
    "vi": {
        "styles": {
            "default": {"thinking": [
                "Để tôi nghĩ xem có gì hay...",
                "Hmm, tôi tìm cái gì đáng xem...",
                "Chờ chút — đang chọn cái gì đặc biệt...",
            ]},
            "casual": {"thinking": [
                "Khoan, để tôi đào cái gì ngầu...",
                "Cho tôi một giây — cái hay sắp tới...",
                "Ổn rồi, để tôi tìm cái ăn điểm cho bạn...",
            ]},
            "warm": {"thinking": [
                "Tôi tìm cái gì bạn thật sự sẽ thích...",
                "Tôi chọn cái gì ấm áp và hay cho bạn...",
                "Chờ chút — tôi muốn đây là lựa chọn tuyệt vời...",
            ]},
            "witty": {"thinking": [
                "Đang hỏi thuật toán gu rất khoa học của tôi...",
                "Tung xúc xắc gợi ý — theo nghĩa bóng...",
                "Để tôi lục kho đồ ngon cho bạn...",
            ]},
            "cinephile": {"thinking": [
                "Đang tuyển danh sách ngắn từ kệ hay...",
                "Lướt danh mục tìm cái gì xứng đáng...",
                "Chờ chút — chọn từ những lựa chọn tinh tế hơn...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Gợi ý cho tôi cái gì đó",
            ],
            "download_ready": [
                "🎉 *{title}* đã sẵn sàng\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* đã được tải xuống!",
            ],
            "play_button": [
                "▶️ Xem trên Jellyfin",
            ],
        },
    },
    "id": {
        "styles": {
            "default": {"thinking": [
                "Biar aku pikirin sesuatu yang bagus...",
                "Hmm, aku cari sesuatu yang layak ditonton...",
                "Sebentar — memilih sesuatu yang spesial...",
            ]},
            "casual": {"thinking": [
                "Tunggu, aku gali sesuatu yang keren...",
                "Kasih aku sebentar — yang bagus segera datang...",
                "Oke oke, aku carikan pilihan yang pas...",
            ]},
            "warm": {"thinking": [
                "Aku cari sesuatu yang benar-benar kamu suka...",
                "Aku pilih sesuatu yang hangat dan bagus untukmu...",
                "Sebentar — aku ingin ini jadi pilihan yang mantap...",
            ]},
            "witty": {"thinking": [
                "Konsultasi algoritma selera super ilmiahku...",
                "Lempar dadu rekomendasi — secara metaforis...",
                "Aku obok brankas barang bagus untukmu...",
            ]},
            "cinephile": {"thinking": [
                "Menyusun daftar pendek dari rak-rak bagus...",
                "Aku telusuri katalog mencari sesuatu yang layak...",
                "Sebentar — memilih dari kandidat yang lebih halus...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Rekomendasikan sesuatu",
            ],
            "download_ready": [
                "🎉 *{title}* sudah siap\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* sudah diunduh!",
            ],
            "play_button": [
                "▶️ Tonton di Jellyfin",
            ],
        },
    },
    "ms": {
        "styles": {
            "default": {"thinking": [
                "Biar saya fikirkan sesuatu yang bagus...",
                "Hmm, saya cari sesuatu yang berbaloi ditonton...",
                "Sebentar — memilih sesuatu yang istimewa...",
            ]},
            "casual": {"thinking": [
                "Tunggu, saya gali sesuatu yang best...",
                "Beri saya sesaat — yang bagus akan datang...",
                "Okay okay, saya carikan pilihan yang tepat...",
            ]},
            "warm": {"thinking": [
                "Saya cari sesuatu yang anda pasti suka...",
                "Saya pilih sesuatu yang selesa dan bagus untuk anda...",
                "Sebentar — saya mahu ini jadi pilihan yang hebat...",
            ]},
            "witty": {"thinking": [
                "Merujuk algoritma citarasa saintifik saya...",
                "Baling dadu cadangan — secara kiasan...",
                "Saya gali peti barang bagus untuk anda...",
            ]},
            "cinephile": {"thinking": [
                "Menyusun senarai pendek dari rak yang bagus...",
                "Saya selak katalog mencari sesuatu yang layak...",
                "Sebentar — memilih daripada pilihan yang lebih halus...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Cadangkan sesuatu untuk saya",
            ],
            "download_ready": [
                "🎉 *{title}* sudah sedia\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* telah dimuat turun!",
            ],
            "play_button": [
                "▶️ Tonton di Jellyfin",
            ],
        },
    },
    "uk": {
        "styles": {
            "default": {"thinking": [
                "Дай мені подумати про щось гарне...",
                "Хм, пошукаю щось, на що варто витратити час...",
                "Секунду — обираю щось особливе...",
            ]},
            "casual": {"thinking": [
                "Зачекай, зараз накопаю щось круте...",
                "Дай секунду — зараз буде щось хороше...",
                "Гаразд-гаразд, знайду тобі вдалий варіант...",
            ]},
            "warm": {"thinking": [
                "Підберу щось, що тобі справді сподобається...",
                "Оберу щось затишне і гарне для тебе...",
                "Секунду — хочу, щоб це був чудовий вибір...",
            ]},
            "witty": {"thinking": [
                "Консультуюся з моїм дуже науковим алгоритмом смаку...",
                "Кидаю кості рекомендацій — метафорично...",
                "Зараз обшукаю сховище хорошого для тебе...",
            ]},
            "cinephile": {"thinking": [
                "Складаю короткий список з найкращих полиць...",
                "Перегорну каталог у пошуках чогось гідного...",
                "Секунду — обираю з вишуканіших варіантів...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Порекомендуй щось",
            ],
            "download_ready": [
                "🎉 *{title}* готовий\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* завантажено!",
            ],
            "play_button": [
                "▶️ Дивитись у Jellyfin",
            ],
        },
    },
    "ro": {
        "styles": {
            "default": {"thinking": [
                "Lasă-mă să mă gândesc la ceva bun...",
                "Hmm, caut ceva care merită timpul tău...",
                "O clipă — aleg ceva special...",
            ]},
            "casual": {"thinking": [
                "Stai, scot la iveală ceva tare...",
                "Dă-mi o secundă — vine ceva bun...",
                "Bine bine, îți găsesc o alegere câștigătoare...",
            ]},
            "warm": {"thinking": [
                "Găsesc ceva ce vei savura cu adevărat...",
                "Aleg ceva cozy și bun pentru tine...",
                "O clipă — vreau să fie o alegere grozavă...",
            ]},
            "witty": {"thinking": [
                "Consult algoritmul meu foarte științific de gust...",
                "Arunc zarurile recomandărilor — metaforic...",
                "Răscolesc seiful cu lucruri bune pentru tine...",
            ]},
            "cinephile": {"thinking": [
                "Curat o listă scurtă de pe rafturile bune...",
                "Răsfoiesc catalogul în căutarea a ceva demn...",
                "O clipă — selectez din opțiunile mai rafinate...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Recomandă-mi ceva",
            ],
            "download_ready": [
                "🎉 *{title}* este gata\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* a fost descărcat!",
            ],
            "play_button": [
                "▶️ Vizionează pe Jellyfin",
            ],
        },
    },
    "hu": {
        "styles": {
            "default": {"thinking": [
                "Hadd gondoljak ki valami jót...",
                "Hmm, keresek valamit, ami megéri az idődet...",
                "Egy pillanat — kiválasztok valami különlegeset...",
            ]},
            "casual": {"thinking": [
                "Várj, előások valami menőt...",
                "Adj egy másodpercet — jön valami jó...",
                "Rendben rendben, találok neked egy nyerőt...",
            ]},
            "warm": {"thinking": [
                "Találok valamit, amit tényleg élvezni fogsz...",
                "Választok neked valami meleg és jó dolgot...",
                "Egy pillanat — remek ajánlás legyen ez...",
            ]},
            "witty": {"thinking": [
                "Konzultálok a nagyon tudományos ízlésalgoritmusommal...",
                "Dobom az ajánlási kockákat — metaforikusan...",
                "Átkutatom a jó dolgok tárolóját neked...",
            ]},
            "cinephile": {"thinking": [
                "Összeállítok egy rövid listát a jó polcokról...",
                "Átlapozom a katalógust, keresve valami méltót...",
                "Egy pillanat — a finomabb jelöltek közül választok...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Ajánlj valamit",
            ],
            "download_ready": [
                "🎉 *{title}* kész\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* letöltve!",
            ],
            "play_button": [
                "▶️ Nézd meg a Jellyfin-en",
            ],
        },
    },
    "sk": {
        "styles": {
            "default": {"thinking": [
                "Nechaj ma premýšľať o niečom dobrom...",
                "Hmm, nájdem niečo, čo stojí za to...",
                "Chvíľu — vyberám niečo výnimočné...",
            ]},
            "casual": {"thinking": [
                "Počkaj, vykopnem niečo super...",
                "Daj mi sekundu — niečo dobré príde...",
                "Dobre dobre, nájdem ti trafenú voľbu...",
            ]},
            "warm": {"thinking": [
                "Nájdem niečo, čo si naozaj užiješ...",
                "Vyberiem ti niečo útulné a dobré...",
                "Chvíľu — chcem, aby to bol skvelý tip...",
            ]},
            "witty": {"thinking": [
                "Konzultujem svoj veľmi vedecký algoritmus vkusu...",
                "Hádzam kockami odporúčaní — metaforicky...",
                "Prehrabujem trezor dobrých vecí pre teba...",
            ]},
            "cinephile": {"thinking": [
                "Zostavujem krátky zoznam z dobrých políc...",
                "Prelistovávam katalóg a hľadám niečo hodné...",
                "Chvíľu — vyberám z jemnejších tipov...",
            ]},
        },
        "shared": {
            "recommend_button": [
                "Odporuč mi niečo",
            ],
            "download_ready": [
                "🎉 *{title}* je pripravený\\! [{play_label}]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* bol stiahnutý!",
            ],
            "play_button": [
                "▶️ Pozrieť na Jellyfin",
            ],
        },
    },
}

__all__ = ["LANG_OVERLAYS"]
