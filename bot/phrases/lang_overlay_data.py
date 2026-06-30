"""
Per-language phrase overlays for non-English catalogs.

Supplies style-specific thinking variants and shared webhook/UI strings
(recommend_button, download_ready) used when generating
bot/phrases/data/{lang}.yaml files. English (en) is the canonical base
catalog and is not included here.
"""

from __future__ import annotations

from typing import Any, Dict

LANG_OVERLAYS: Dict[str, Dict[str, Any]] = {

    "ar": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "دعني أبحث عن ذلك...",
                    "لحظة — أتحقق لك...",
                    "أبحث عن إجابة...",
                ],
                "thinking_recommend": [
                    "دعني أفكر في شيء جيد...",
                    "همم، سأبحث عن شيء يستحق وقتك...",
                    "لحظة — أختار شيئًا مميزًا...",
                ],
                "thinking_add_media": [
                    "أبحث عن هذا العنوان في المكتبة...",
                    "أراجع الفهرس...",
                    "لحظة — أبحث عن تطابقات...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "دعني أبحث عن ذلك...",
                    "لحظة — أتحقق لك...",
                    "أبحث عن إجابة...",
                ],
                "thinking_recommend": [
                    "انتظر، سأجد شيئًا رائعًا...",
                    "أعطني ثانية — شيء جيد قادم...",
                    "حسنًا، دعني أجد لك خيارًا ممتازًا...",
                ],
                "thinking_add_media": [
                    "أبحث عن هذا العنوان في المكتبة...",
                    "أراجع الفهرس...",
                    "لحظة — أبحث عن تطابقات...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "دعني أبحث عن ذلك...",
                    "لحظة — أتحقق لك...",
                    "أبحث عن إجابة...",
                ],
                "thinking_recommend": [
                    "سأجد شيئًا ستستمتع به حقًا...",
                    "سأختار شيئًا دافئًا وجيدًا لك...",
                    "لحظة — أريد أن يكون اختيارًا رائعًا...",
                ],
                "thinking_add_media": [
                    "أبحث عن هذا العنوان في المكتبة...",
                    "أراجع الفهرس...",
                    "لحظة — أبحث عن تطابقات...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "بالطبع، سأترك كل شيء وأجد لك شيئًا مثاليًا...",
                    "لأنه من الواضح أنني لم يكن لدي ما أفعله...",
                    "حسنًا. سأتظاهر أن هذا تحدٍ مثير...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "أتفقد القسم المحظور بحثًا عن شيء جيد...",
                    "أستشير قبعة التنسيق حول ذوقك...",
                    "أحضّر جرعة توصيات — تقريبًا جاهزة...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "اقترح علي شيئًا",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) جاهز! [▶️ شاهد على Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 تم تحميل *{title}* ({type})!",
            ],
        },
    },
    "cs": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Nech mě to vyhledat...",
                    "Moment — ověřím to pro tebe...",
                    "Hledám odpověď...",
                ],
                "thinking_recommend": [
                    "Nech mě přemýšlet o něčem dobrém...",
                    "Hmm, najdu něco, co stojí za to...",
                    "Chvilku — vybírám něco speciálního...",
                ],
                "thinking_add_media": [
                    "Hledám ten titul v knihovně...",
                    "Prohlížím katalog...",
                    "Moment — hledám shody...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Nech mě to vyhledat...",
                    "Moment — ověřím to pro tebe...",
                    "Hledám odpověď...",
                ],
                "thinking_recommend": [
                    "Počkej, vykopu něco super...",
                    "Dej mi vteřinu — něco dobrého přijde...",
                    "Dobře dobře, najdu ti trefu...",
                ],
                "thinking_add_media": [
                    "Hledám ten titul v knihovně...",
                    "Prohlížím katalog...",
                    "Moment — hledám shody...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Nech mě to vyhledat...",
                    "Moment — ověřím to pro tebe...",
                    "Hledám odpověď...",
                ],
                "thinking_recommend": [
                    "Najdu něco, co si opravdu užiješ...",
                    "Vyberu ti něco útulného a dobrého...",
                    "Chvilku — chci, aby to byl skvělý tip...",
                ],
                "thinking_add_media": [
                    "Hledám ten titul v knihovně...",
                    "Prohlížím katalog...",
                    "Moment — hledám shody...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Jasně, nechám všechno být a najdu něco dokonalého...",
                    "Protože jsem evidentně neměl co lepšího dělat...",
                    "Dobře. Budu předstírat, že je to fascinující úkol...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Prohledávám zakázanou sekci něco dobrého...",
                    "Radím se s Moudrým kloboukem ohledně tvého vkusu...",
                    "Vařím lektvar doporučení — skoro hotovo...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Doporuč mi něco",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) je připraven! [▶️ Sledovat na Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) byl stažen!",
            ],
        },
    },
    "da": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Lad mig slå det op...",
                    "Et øjeblik — tjekker det for dig...",
                    "Søger efter et svar...",
                ],
                "thinking_recommend": [
                    "Lad mig tænke over noget godt...",
                    "Hmm, jeg finder noget, der er tiden værd...",
                    "Et øjeblik — vælger noget særligt...",
                ],
                "thinking_add_media": [
                    "Søger den titel i biblioteket...",
                    "Tjekker kataloget...",
                    "Et øjeblik — finder matches...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Lad mig slå det op...",
                    "Et øjeblik — tjekker det for dig...",
                    "Søger efter et svar...",
                ],
                "thinking_recommend": [
                    "Vent, jeg graver noget fedt frem...",
                    "Giv mig et sekund — noget godt er på vej...",
                    "Okay okay, jeg finder en vinder til dig...",
                ],
                "thinking_add_media": [
                    "Søger den titel i biblioteket...",
                    "Tjekker kataloget...",
                    "Et øjeblik — finder matches...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Lad mig slå det op...",
                    "Et øjeblik — tjekker det for dig...",
                    "Søger efter et svar...",
                ],
                "thinking_recommend": [
                    "Jeg finder noget, du virkelig vil nyde...",
                    "Jeg vælger noget hyggeligt og godt til dig...",
                    "Et øjeblik — det skal blive et godt valg...",
                ],
                "thinking_add_media": [
                    "Søger den titel i biblioteket...",
                    "Tjekker kataloget...",
                    "Et øjeblik — finder matches...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Selvfølgelig, jeg dropper alt og finder noget perfekt...",
                    "Fordi jeg åbenbart ikke havde bedre at tage mig til...",
                    "Fint. Jeg lader som om det er en fascinerende opgave...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Kigger i den forbudte afdeling efter noget godt...",
                    "Spørger sorteringshatten om din smag...",
                    "Brygger en anbefalings-eliksir — næsten klar...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Anbefal mig noget",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) er klar! [▶️ Se på Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) er blevet downloadet!",
            ],
        },
    },
    "de": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Lass mich das nachschlagen...",
                    "Einen Moment — ich prüfe das für dich...",
                    "Suche nach einer Antwort...",
                ],
                "thinking_recommend": [
                    "Lass mich über etwas Gutes nachdenken...",
                    "Hmm, ich suche etwas, das sich lohnt...",
                    "Einen Moment — ich wähle etwas Besonderes...",
                ],
                "thinking_add_media": [
                    "Suche diesen Titel in der Bibliothek...",
                    "Schlage im Katalog nach...",
                    "Einen Moment — suche Treffer...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Warte, ich schau das nach...",
                    "Gib mir 'ne Sekunde — ich such's...",
                    "Okay, ich find die Antwort...",
                ],
                "thinking_recommend": [
                    "Warte, ich grabe was Cooles aus...",
                    "Gib mir 'ne Sekunde — gleich kommt was Gutes...",
                    "Okay okay, ich such dir einen Treffer...",
                ],
                "thinking_add_media": [
                    "Bin dran — durchsuch die Bibliothek...",
                    "Gib mir 'ne Sekunde, jag den Titel...",
                    "Okay, such ihn im Katalog...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Ich find die beste Antwort für dich...",
                    "Ich schau das sorgfältig für dich nach...",
                    "Einen Moment — das soll stimmen...",
                ],
                "thinking_recommend": [
                    "Ich such was, das dir wirklich gefällt...",
                    "Ich wähle was Gemütliches und Gutes für dich...",
                    "Einen Moment — das soll ein toller Tipp werden...",
                ],
                "thinking_add_media": [
                    "Ich such den Titel für deine Bibliothek...",
                    "Ich find den passenden Treffer für dich...",
                    "Einen Moment — schau ich für dich nach...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Na klar, ich lass alles liegen und such dir was Perfektes...",
                    "Weil ich offensichtlich nichts Besseres zu tun hatte...",
                    "Schön. Ich tu so, als wäre das eine spannende Aufgabe...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Durchstöbere den verbotenen Abteil nach etwas Gutem...",
                    "Frage den Sprechenden Hut nach deinem Geschmack...",
                    "Braue einen Empfehlungstrank — gleich fertig...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Empfiehl mir etwas",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) ist bereit! [▶️ Auf Jellyfin ansehen]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) wurde heruntergeladen!",
            ],
        },
    },
    "el": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Άσε με να το ψάξω...",
                    "Λίγο — το ελέγχω για σένα...",
                    "Ψάχνω απάντηση...",
                ],
                "thinking_recommend": [
                    "Άσε με να σκεφτώ κάτι καλό...",
                    "Χμ, θα βρω κάτι που αξίζει τον χρόνο σου...",
                    "Μια στιγμή — διαλέγω κάτι ξεχωριστό...",
                ],
                "thinking_add_media": [
                    "Ψάχνω αυτόν τον τίτλο στη βιβλιοθήκη...",
                    "Ελέγχω τον κατάλογο...",
                    "Λίγο — ψάχνω αντιστοιχίες...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Άσε με να το ψάξω...",
                    "Λίγο — το ελέγχω για σένα...",
                    "Ψάχνω απάντηση...",
                ],
                "thinking_recommend": [
                    "Περίμενε, θα βρω κάτι ωραίο...",
                    "Δώσε μου ένα δευτερόλεπτο — έρχεται κάτι καλό...",
                    "Εντάξει εντάξει, θα σου βρω έναν νικητή...",
                ],
                "thinking_add_media": [
                    "Ψάχνω αυτόν τον τίτλο στη βιβλιοθήκη...",
                    "Ελέγχω τον κατάλογο...",
                    "Λίγο — ψάχνω αντιστοιχίες...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Άσε με να το ψάξω...",
                    "Λίγο — το ελέγχω για σένα...",
                    "Ψάχνω απάντηση...",
                ],
                "thinking_recommend": [
                    "Θα βρω κάτι που θα απολαύσεις πραγματικά...",
                    "Διαλέγω κάτι ζεστό και καλό για σένα...",
                    "Μια στιγμή — θέλω να είναι μια εξαιρετική επιλογή...",
                ],
                "thinking_add_media": [
                    "Ψάχνω αυτόν τον τίτλο στη βιβλιοθήκη...",
                    "Ελέγχω τον κατάλογο...",
                    "Λίγο — ψάχνω αντιστοιχίες...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Φυσικά, αφήνω τα πάντα και βρίσκω κάτι τέλειο...",
                    "Γιατί προφανώς δεν είχα κάτι καλύτερο να κάνω...",
                    "Εντάξει. Θα κάνω πως είναι συναρπαστική πρόκληση...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Ψάχνω στην Απαγορευμένη Βιβλιοθήκη κάτι καλό...",
                    "Συμβουλεύομαι το Διαλεκτικό Καπέλο για τα γούστα σου...",
                    "Ετοιμάζω φίλτρο συστάσεων — σχεδόν έτοιμο...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Πρότεινέ μου κάτι",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) είναι έτοιμο! [▶️ Δες στο Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 Το *{title}* ({type}) κατέβηκε!",
            ],
        },
    },
    "es": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Déjame buscar eso...",
                    "Un momento — lo compruebo para ti...",
                    "Buscando una respuesta...",
                ],
                "thinking_recommend": [
                    "Déjame pensar en algo bueno...",
                    "Hmm, voy a buscar algo que valga la pena...",
                    "Un momento — elijo algo especial...",
                ],
                "thinking_add_media": [
                    "Buscando ese título en la biblioteca...",
                    "Consultando el catálogo...",
                    "Un momento — buscando coincidencias...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Espera, voy a mirar eso...",
                    "Dame un segundo — lo busco...",
                    "Vale, déjame encontrar la respuesta...",
                ],
                "thinking_recommend": [
                    "Espera, voy a encontrar algo genial...",
                    "Dame un segundo — viene algo bueno...",
                    "Vale, déjame buscarte un acierto...",
                ],
                "thinking_add_media": [
                    "En marcha — busco en la biblioteca...",
                    "Dame un segundo, rastreo ese título...",
                    "Vale, lo busco en el catálogo...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Déjame encontrar la mejor respuesta para ti...",
                    "Lo buscaré con cuidado para ti...",
                    "Un momento — quiero acertar...",
                ],
                "thinking_recommend": [
                    "Déjame encontrar algo que de verdad disfrutes...",
                    "Voy a elegir algo acogedor y bueno para ti...",
                    "Un momento — quiero que sea una gran elección...",
                ],
                "thinking_add_media": [
                    "Busco ese título en la biblioteca para ti...",
                    "Encontraré la coincidencia adecuada...",
                    "Un momento — lo busco para ti...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Claro, dejo todo y te busco algo perfecto...",
                    "Porque obviamente no tenía nada mejor que hacer...",
                    "Vale. Fingiré que esto es un reto fascinante...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Revisando la Sección Restringida en busca de algo bueno...",
                    "Consultando el Sombrero Seleccionador sobre tu gusto...",
                    "Preparando una poción de recomendaciones — casi lista...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Recomiéndame algo",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) está lista! [▶️ Ver en Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) se ha descargado!",
            ],
        },
    },
    "fi": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Anna kun tarkistan...",
                    "Hetki — tarkistan sen puolestasi...",
                    "Etsin vastausta...",
                ],
                "thinking_recommend": [
                    "Anna mun miettiä jotain hyvää...",
                    "Hmm, etsin jotain katsomisen arvoista...",
                    "Hetki — valitsen jotain erityistä...",
                ],
                "thinking_add_media": [
                    "Etsin tuota nimikettä kirjastosta...",
                    "Tarkistan luettelon...",
                    "Hetki — etsin osumia...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Anna kun tarkistan...",
                    "Hetki — tarkistan sen puolestasi...",
                    "Etsin vastausta...",
                ],
                "thinking_recommend": [
                    "Oota, kaivan jotain siistiä...",
                    "Anna mulle sekunti — hyvää tulossa...",
                    "Okei okei, etsin sulle osuman...",
                ],
                "thinking_add_media": [
                    "Etsin tuota nimikettä kirjastosta...",
                    "Tarkistan luettelon...",
                    "Hetki — etsin osumia...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Anna kun tarkistan...",
                    "Hetki — tarkistan sen puolestasi...",
                    "Etsin vastausta...",
                ],
                "thinking_recommend": [
                    "Etsin jotain mistä oikeasti pidät...",
                    "Valitsen sulle jotain mukavaa ja hyvää...",
                    "Hetki — haluan tästä loistavan valinnan...",
                ],
                "thinking_add_media": [
                    "Etsin tuota nimikettä kirjastosta...",
                    "Tarkistan luettelon...",
                    "Hetki — etsin osumia...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Totta kai, jätän kaiken ja etsin jotain täydellistä...",
                    "Koska minulla ilmeisesti ei ollut parempaakaan tekemistä...",
                    "Selvä. Teeskentelen, että tämä on kiehtova haaste...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Selaan kiellettyä osastoa hyvän löytämiseksi...",
                    "Kysyn lajitteluhattua mieltymyksistäsi...",
                    "Keitän suositusjuomaa — melkein valmis...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Suosittele mulle jotain",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) on valmis! [▶️ Katso Jellyfinissä]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) on ladattu!",
            ],
        },
    },
    "fr": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Laisse-moi chercher ça...",
                    "Un instant — je vérifie pour toi...",
                    "Je cherche une réponse...",
                ],
                "thinking_recommend": [
                    "Laisse-moi penser à quelque chose de bien...",
                    "Hmm, je vais trouver quelque chose qui vaut le coup...",
                    "Un instant — je choisis quelque chose de spécial...",
                ],
                "thinking_add_media": [
                    "Je cherche ce titre dans la bibliothèque...",
                    "Je consulte le catalogue...",
                    "Un instant — je cherche des correspondances...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Attends, je regarde ça...",
                    "Une seconde — je cherche...",
                    "OK, je trouve la réponse...",
                ],
                "thinking_recommend": [
                    "Attends, je vais dénicher un truc sympa...",
                    "Une seconde — quelque chose de bien arrive...",
                    "OK, laisse-moi te trouver un bon choix...",
                ],
                "thinking_add_media": [
                    "C'est parti — je fouille la bibliothèque...",
                    "Une seconde, je traque ce titre...",
                    "OK, je le cherche dans le catalogue...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Je vais trouver la meilleure réponse pour toi...",
                    "Je vais chercher ça avec soin...",
                    "Un instant — je veux bien faire...",
                ],
                "thinking_recommend": [
                    "Je vais trouver quelque chose que tu apprécieras vraiment...",
                    "Je choisis quelque chose de doux et agréable pour toi...",
                    "Un instant — je veux que ce soit un super choix...",
                ],
                "thinking_add_media": [
                    "Je cherche ce titre pour ta bibliothèque...",
                    "Je trouverai le bon match pour toi...",
                    "Un instant — je regarde ça pour toi...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Bien sûr, je lâche tout pour te trouver le film parfait...",
                    "Parce qu'évidemment je n'avais rien de mieux à faire...",
                    "D'accord. Je vais faire comme si c'était passionnant...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Je fouille la Section interdite pour quelque chose de bon...",
                    "Je consulte le Choixpeau sur tes goûts...",
                    "Je prépare une potion de recommandations — presque prête...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Recommande-moi quelque chose",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) est prêt ! [▶️ Regarder sur Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) a été téléchargé !",
            ],
        },
    },
    "he": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "תן לי לבדוק...",
                    "רגע — אני בודק בשבילך...",
                    "מחפש תשובה...",
                ],
                "thinking_recommend": [
                    "תן לי לחשוב על משהו טוב...",
                    "הממ, אחפש משהו ששווה את הזמן שלך...",
                    "רגע — בוחר משהו מיוחד...",
                ],
                "thinking_add_media": [
                    "מחפש את הכותרת הזו בספרייה...",
                    "בודק בקטלוג...",
                    "רגע — מחפש התאמות...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "תן לי לבדוק...",
                    "רגע — אני בודק בשבילך...",
                    "מחפש תשובה...",
                ],
                "thinking_recommend": [
                    "חכה, אחפש משהו מגניב...",
                    "תן לי שנייה — משהו טוב בדרך...",
                    "אוקיי אוקיי, אמצא לך בחירה מנצחת...",
                ],
                "thinking_add_media": [
                    "מחפש את הכותרת הזו בספרייה...",
                    "בודק בקטלוג...",
                    "רגע — מחפש התאמות...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "תן לי לבדוק...",
                    "רגע — אני בודק בשבילך...",
                    "מחפש תשובה...",
                ],
                "thinking_recommend": [
                    "אמצא משהו שבאמת תהנה ממנו...",
                    "אבחר משהו נעים וטוב בשבילך...",
                    "רגע — אני רוצה שזה יהיה בחירה מעולה...",
                ],
                "thinking_add_media": [
                    "מחפש את הכותרת הזו בספרייה...",
                    "בודק בקטלוג...",
                    "רגע — מחפש התאמות...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "ברור, אני מפסיק הכל ומוצא משהו מושלם...",
                    "כי כמובן לא היה לי משהו יותר טוב לעשות...",
                    "בסדר. אעמיד פנים שזה אתגר מרתק...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "בודק במדור האסור משהו ששווה לראות...",
                    "מתייעץ עם כובע המיון על הטעם שלך...",
                    "מכין שיקוי המלצות — כמעט מוכן...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "המלץ לי על משהו",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) מוכן! [▶️ צפה ב-Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) הורד!",
            ],
        },
    },
    "hi": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "मुझे देखने दो...",
                    "एक सेकंड — मैं चेक करता हूँ...",
                    "जवाब ढूँढ रहा हूँ...",
                ],
                "thinking_recommend": [
                    "मुझे कुछ अच्छा सोचने दो...",
                    "हम्म, कुछ ऐसा ढूँढता हूँ जो देखने लायक हो...",
                    "एक पल — कुछ खास चुन रहा हूँ...",
                ],
                "thinking_add_media": [
                    "लाइब्रेरी में वो टाइटल ढूँढ रहा हूँ...",
                    "कैटलॉग देख रहा हूँ...",
                    "एक सेकंड — मैच ढूँढ रहा हूँ...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "मुझे देखने दो...",
                    "एक सेकंड — मैं चेक करता हूँ...",
                    "जवाब ढूँढ रहा हूँ...",
                ],
                "thinking_recommend": [
                    "रुको, कुछ धासू ढूँढता हूँ...",
                    "एक सेकंड दो — अच्छी चीज़ आ रही है...",
                    "ठीक है, तुम्हारे लिए एक बढ़िया विकल्प ढूँढता हूँ...",
                ],
                "thinking_add_media": [
                    "लाइब्रेरी में वो टाइटल ढूँढ रहा हूँ...",
                    "कैटलॉग देख रहा हूँ...",
                    "एक सेकंड — मैच ढूँढ रहा हूँ...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "मुझे देखने दो...",
                    "एक सेकंड — मैं चेक करता हूँ...",
                    "जवाब ढूँढ रहा हूँ...",
                ],
                "thinking_recommend": [
                    "कुछ ऐसा ढूँढता हूँ जो तुम्हें सच में पसंद आए...",
                    "तुम्हारे लिए कुछ आरामदायक और अच्छा चुनता हूँ...",
                    "एक पल — यह एक शानदार सुझाव होना चाहिए...",
                ],
                "thinking_add_media": [
                    "लाइब्रेरी में वो टाइटल ढूँढ रहा हूँ...",
                    "कैटलॉग देख रहा हूँ...",
                    "एक सेकंड — मैच ढूँढ रहा हूँ...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "हाँ हाँ, सब छोड़कर perfect चीज़ ढूँढता हूँ...",
                    "क्योंकि obviously मेरे पास और कुछ था ही नहीं...",
                    "ठीक है, मान लेता हूँ ये दिलचस्प चुनौती है...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "प्रतिबंधित अनुभाग में कुछ अच्छा ढूँढ रहा हूँ...",
                    "सॉर्टिंग हैट से तुम्हारी पसंद पूछ रहा हूँ...",
                    "सिफ़ारिश का पोशन तैयार कर रहा हूँ — लगभग तैयार...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "मुझे कुछ सुझाओ",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) तैयार है! [▶️ Jellyfin पर देखें]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) डाउनलोड हो गया!",
            ],
        },
    },
    "hu": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Hadd keressem meg...",
                    "Egy pillanat — megnézem neked...",
                    "Választ keresek...",
                ],
                "thinking_recommend": [
                    "Hadd gondoljak ki valami jót...",
                    "Hmm, keresek valamit, ami megéri az idődet...",
                    "Egy pillanat — kiválasztok valami különlegeset...",
                ],
                "thinking_add_media": [
                    "Keresem azt a címet a könyvtárban...",
                    "Átnézem a katalógust...",
                    "Egy pillanat — egyezéseket keresek...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Hadd keressem meg...",
                    "Egy pillanat — megnézem neked...",
                    "Választ keresek...",
                ],
                "thinking_recommend": [
                    "Várj, előások valami menőt...",
                    "Adj egy másodpercet — jön valami jó...",
                    "Rendben rendben, találok neked egy nyerőt...",
                ],
                "thinking_add_media": [
                    "Keresem azt a címet a könyvtárban...",
                    "Átnézem a katalógust...",
                    "Egy pillanat — egyezéseket keresek...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Hadd keressem meg...",
                    "Egy pillanat — megnézem neked...",
                    "Választ keresek...",
                ],
                "thinking_recommend": [
                    "Találok valamit, amit tényleg élvezni fogsz...",
                    "Választok neked valami meleg és jó dolgot...",
                    "Egy pillanat — remek ajánlás legyen ez...",
                ],
                "thinking_add_media": [
                    "Keresem azt a címet a könyvtárban...",
                    "Átnézem a katalógust...",
                    "Egy pillanat — egyezéseket keresek...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Persze, mindent félreteszek és találok valami tökéleteset...",
                    "Mert nyilván nem volt jobb dolgom...",
                    "Rendben. Úgy teszek, mintha izgalmas kihívás lenne...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "A tiltott részlegben keresek valami jót...",
                    "A Télesztő Sisakkal konzultálok azon ítékodról...",
                    "Ajánlás-bájitalt főzök — majdnem kész...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Ajánlj valamit",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) kész! [▶️ Nézd meg a Jellyfin-en]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) letöltve!",
            ],
        },
    },
    "id": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Biar aku cek...",
                    "Sebentar — aku periksa untukmu...",
                    "Mencari jawaban...",
                ],
                "thinking_recommend": [
                    "Biar aku pikirin sesuatu yang bagus...",
                    "Hmm, aku cari sesuatu yang layak ditonton...",
                    "Sebentar — memilih sesuatu yang spesial...",
                ],
                "thinking_add_media": [
                    "Mencari judul itu di perpustakaan...",
                    "Memeriksa katalog...",
                    "Sebentar — mencari kecocokan...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Biar aku cek...",
                    "Sebentar — aku periksa untukmu...",
                    "Mencari jawaban...",
                ],
                "thinking_recommend": [
                    "Tunggu, aku gali sesuatu yang keren...",
                    "Kasih aku sebentar — yang bagus segera datang...",
                    "Oke oke, aku carikan pilihan yang pas...",
                ],
                "thinking_add_media": [
                    "Mencari judul itu di perpustakaan...",
                    "Memeriksa katalog...",
                    "Sebentar — mencari kecocokan...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Biar aku cek...",
                    "Sebentar — aku periksa untukmu...",
                    "Mencari jawaban...",
                ],
                "thinking_recommend": [
                    "Aku cari sesuatu yang benar-benar kamu suka...",
                    "Aku pilih sesuatu yang hangat dan bagus untukmu...",
                    "Sebentar — aku ingin ini jadi pilihan yang mantap...",
                ],
                "thinking_add_media": [
                    "Mencari judul itu di perpustakaan...",
                    "Memeriksa katalog...",
                    "Sebentar — mencari kecocokan...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Tentu, aku tinggalkan semuanya dan cari yang sempurna...",
                    "Karena jelas-jelas aku nggak punya hal lebih baik...",
                    "Baiklah. Aku pura-pura ini tantangan seru...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Mengecek Bagian Terlarang untuk sesuatu yang bagus...",
                    "Berkonsultasi dengan Topi Pemilih soal selera kamu...",
                    "Meracik ramuan rekomendasi — hampir selesai...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Rekomendasikan sesuatu",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) sudah siap! [▶️ Tonton di Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) sudah diunduh!",
            ],
        },
    },
    "it": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Fammi cercare...",
                    "Un attimo — controllo per te...",
                    "Cerco una risposta...",
                ],
                "thinking_recommend": [
                    "Fammi pensare a qualcosa di buono...",
                    "Hmm, cerco qualcosa che valga la pena...",
                    "Un attimo — scelgo qualcosa di speciale...",
                ],
                "thinking_add_media": [
                    "Cerco quel titolo in biblioteca...",
                    "Consulto il catalogo...",
                    "Un attimo — cerco corrispondenze...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Aspetta, guardo...",
                    "Dammi un secondo — cerco...",
                    "Ok, trovo la risposta...",
                ],
                "thinking_recommend": [
                    "Aspetta, trovo qualcosa di figo...",
                    "Dammi un secondo — arriva qualcosa di buono...",
                    "Ok ok, ti cerco un colpo vincente...",
                ],
                "thinking_add_media": [
                    "Ci sono — cerco in biblioteca...",
                    "Dammi un secondo, rintraccio il titolo...",
                    "Ok, lo cerco nel catalogo...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Trovo la risposta migliore per te...",
                    "Lo cerco con cura per te...",
                    "Un attimo — voglio azzeccare...",
                ],
                "thinking_recommend": [
                    "Cerco qualcosa che ti piacerà davvero...",
                    "Scelgo qualcosa di accogliente e buono per te...",
                    "Un attimo — voglio che sia una scelta azzeccata...",
                ],
                "thinking_add_media": [
                    "Cerco quel titolo per la tua libreria...",
                    "Trovo la corrispondenza giusta per te...",
                    "Un attimo — lo cerco per te...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Certo, mollo tutto e ti trovo qualcosa di perfetto...",
                    "Perché ovviamente non avevo di meglio da fare...",
                    "Va bene. Fingirò che sia una sfida avvincente...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Controllo la Sezione Proibita per qualcosa di buono...",
                    "Consulto il Cappello Parlante sui tuoi gusti...",
                    "Preparo una pozione di raccomandazioni — quasi pronta...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Consigliami qualcosa",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) è pronto! [▶️ Guarda su Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) è stato scaricato!",
            ],
        },
    },
    "ja": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "調べてみるね...",
                    "ちょっと待って — 確認するね...",
                    "答えを探してる...",
                ],
                "thinking_recommend": [
                    "いいものを考えてみるね...",
                    "うーん、見る価値のあるものを探してみる...",
                    "ちょっと待って — 特別なものを選ぶね...",
                ],
                "thinking_add_media": [
                    "ライブラリでそのタイトルを検索中...",
                    "カタログを調べてる...",
                    "ちょっと待って — 一致を探してる...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "待ってて、それ調べる...",
                    "ちょい待ち — 探すね...",
                    "オッケー、答え見つける...",
                ],
                "thinking_recommend": [
                    "待ってて、いいの掘り出してくる...",
                    "ちょい待ち — いいの見つかるよ...",
                    "オッケー、いいやつ探してくるね...",
                ],
                "thinking_add_media": [
                    "了解 — ライブラリ検索中...",
                    "ちょい待ち、タイトル追跡中...",
                    "オッケー、カタログで探す...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "いい答えを探すね...",
                    "丁寧に調べるよ...",
                    "ちょっと待って — ちゃんと当てたい...",
                ],
                "thinking_recommend": [
                    "きっと気に入ってもらえるものを探すね...",
                    "ほっこりしていて良いものを選ぶよ...",
                    "ちょっと待って — いいおすすめにしたいから...",
                ],
                "thinking_add_media": [
                    "ライブラリでタイトル探すね...",
                    "ぴったりの一致を見つける...",
                    "ちょっと待って — 探してる...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "はいはい、全部放り出して完璧なもの探しますよ...",
                    "もちろん他にやることがなかったわけじゃないですけど...",
                    "わかった。超面白い課題だと思い込みます...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "禁書区からいいものを探してる...",
                    "組分け帽に好みを相談中...",
                    "おすすめポーションを調合中 — もう少し...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "何かおすすめして",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) の準備ができました\\！ [▶️ Jellyfinで視聴]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) がダウンロードされました！",
            ],
        },
    },
    "ko": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "찾아볼게...",
                    "잠깐만 — 확인해볼게...",
                    "답을 찾는 중...",
                ],
                "thinking_recommend": [
                    "뭔가 좋은 걸 생각해볼게...",
                    "음, 볼 만한 걸 찾아볼게...",
                    "잠깐만 — 특별한 걸 골라볼게...",
                ],
                "thinking_add_media": [
                    "라이브러리에서 그 제목 검색 중...",
                    "카탈로그 확인 중...",
                    "잠깐만 — 일치 항목 찾는 중...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "잠깐, 그거 볼게...",
                    "1초만 — 찾아볼게...",
                    "알았어, 답 찾을게...",
                ],
                "thinking_recommend": [
                    "잠깐, 멋진 거 하나 파볼게...",
                    "1초만 — 좋은 거 곧 나올 거야...",
                    "알았어, 괜찮은 거 하나 찾아볼게...",
                ],
                "thinking_add_media": [
                    "바로 갈게 — 라이브러리 검색...",
                    "1초만, 제목 추적 중...",
                    "알았어, 카탈로그에서 찾을게...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "가장 좋은 답을 찾아볼게...",
                    "꼼꼼히 찾아볼게...",
                    "잠깐만 — 제대로 맞추고 싶어...",
                ],
                "thinking_recommend": [
                    "정말 마음에 들 만한 걸 찾아볼게...",
                    "편안하고 좋은 걸 골라줄게...",
                    "잠깐만 — 정말 좋은 추천이 되게 할게...",
                ],
                "thinking_add_media": [
                    "라이브러리에서 제목 찾는 중...",
                    "딱 맞는 걸 찾아줄게...",
                    "잠깐만 — 찾는 중...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "물론이죠, 모든 걸 내려놓고 완벽한 걸 찾아볼게요...",
                    "당연히 할 일이 없었던 건 아니지만요...",
                    "알겠어요. 재미있는 도전인 척할게요...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "금서 구역에서 볼 만한 걸 찾는 중...",
                    "기숙 배정 모자에게 취향을 물어보는 중...",
                    "추천 물약을 만드는 중 — 거의 다 됐어요...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "뭔가 추천해줘",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) 준비 완료! [▶️ Jellyfin에서 시청]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) 다운로드 완료!",
            ],
        },
    },
    "ms": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Biar saya semak...",
                    "Sebentar — saya periksa untuk anda...",
                    "Mencari jawapan...",
                ],
                "thinking_recommend": [
                    "Biar saya fikirkan sesuatu yang bagus...",
                    "Hmm, saya cari sesuatu yang berbaloi ditonton...",
                    "Sebentar — memilih sesuatu yang istimewa...",
                ],
                "thinking_add_media": [
                    "Mencari tajuk itu dalam perpustakaan...",
                    "Menyemak katalog...",
                    "Sebentar — mencari padanan...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Biar saya semak...",
                    "Sebentar — saya periksa untuk anda...",
                    "Mencari jawapan...",
                ],
                "thinking_recommend": [
                    "Tunggu, saya gali sesuatu yang best...",
                    "Beri saya sesaat — yang bagus akan datang...",
                    "Okay okay, saya carikan pilihan yang tepat...",
                ],
                "thinking_add_media": [
                    "Mencari tajuk itu dalam perpustakaan...",
                    "Menyemak katalog...",
                    "Sebentar — mencari padanan...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Biar saya semak...",
                    "Sebentar — saya periksa untuk anda...",
                    "Mencari jawapan...",
                ],
                "thinking_recommend": [
                    "Saya cari sesuatu yang anda pasti suka...",
                    "Saya pilih sesuatu yang selesa dan bagus untuk anda...",
                    "Sebentar — saya mahu ini jadi pilihan yang hebat...",
                ],
                "thinking_add_media": [
                    "Mencari tajuk itu dalam perpustakaan...",
                    "Menyemak katalog...",
                    "Sebentar — mencari padanan...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Sudah tentu, aku tinggalkan semua dan cari yang sempurna...",
                    "Sebab jelas aku tiada kerja lebih baik...",
                    "Baiklah. Aku pura-pura ini cabaran menarik...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Menyemak Bahagian Larangan untuk sesuatu yang bagus...",
                    "Berkonsultasi dengan Topi Sorting tentang citarasa kamu...",
                    "Meracik ramuan cadangan — hampir siap...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Cadangkan sesuatu untuk saya",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) sudah sedia! [▶️ Tonton di Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) telah dimuat turun!",
            ],
        },
    },
    "nl": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Laat me dat opzoeken...",
                    "Even geduld — ik check het voor je...",
                    "Zoeken naar een antwoord...",
                ],
                "thinking_recommend": [
                    "Laat me even nadenken over iets goeds...",
                    "Hmm, ik zoek iets dat de moeite waard is...",
                    "Even geduld — ik kies iets bijzonders...",
                ],
                "thinking_add_media": [
                    "Zoek die titel in de bibliotheek...",
                    "Catalogus raadplegen...",
                    "Even — matches zoeken...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Laat me dat opzoeken...",
                    "Even geduld — ik check het voor je...",
                    "Zoeken naar een antwoord...",
                ],
                "thinking_recommend": [
                    "Wacht even, ik graaf iets cools op...",
                    "Geef me een seconde — er komt iets goeds aan...",
                    "Oké oké, ik zoek een winnaar voor je...",
                ],
                "thinking_add_media": [
                    "Zoek die titel in de bibliotheek...",
                    "Catalogus raadplegen...",
                    "Even — matches zoeken...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Laat me dat opzoeken...",
                    "Even geduld — ik check het voor je...",
                    "Zoeken naar een antwoord...",
                ],
                "thinking_recommend": [
                    "Ik zoek iets waar je echt van geniet...",
                    "Ik kies iets gezelligs en goeds voor je...",
                    "Even geduld — dit moet een topkeuze worden...",
                ],
                "thinking_add_media": [
                    "Zoek die titel in de bibliotheek...",
                    "Catalogus raadplegen...",
                    "Even — matches zoeken...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Tuurlijk, ik laat alles liggen en zoek iets perfects...",
                    "Want ik had natuurlijk niets beters te doen...",
                    "Prima. Ik doe alsof dit een fascinerende uitdaging is...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Even in de verboden afdeling snuffelen...",
                    "Overleg met de Sorteerhoed over je smaak...",
                    "Aanbevelingsdrankje aan het brouwen — bijna klaar...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Beveel me iets aan",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) is klaar! [▶️ Bekijk op Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) is gedownload!",
            ],
        },
    },
    "no": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "La meg slå opp det...",
                    "Et øyeblikk — sjekker det for deg...",
                    "Søker etter et svar...",
                ],
                "thinking_recommend": [
                    "La meg tenke på noe bra...",
                    "Hmm, jeg finner noe som er verdt tiden din...",
                    "Et øyeblikk — velger noe spesielt...",
                ],
                "thinking_add_media": [
                    "Søker den tittelen i biblioteket...",
                    "Sjekker katalogen...",
                    "Et øyeblikk — finner treff...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "La meg slå opp det...",
                    "Et øyeblikk — sjekker det for deg...",
                    "Søker etter et svar...",
                ],
                "thinking_recommend": [
                    "Vent, jeg graver frem noe kult...",
                    "Gi meg et sekund — noe bra kommer...",
                    "Ok ok, jeg finner en vinner til deg...",
                ],
                "thinking_add_media": [
                    "Søker den tittelen i biblioteket...",
                    "Sjekker katalogen...",
                    "Et øyeblikk — finner treff...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "La meg slå opp det...",
                    "Et øyeblikk — sjekker det for deg...",
                    "Søker etter et svar...",
                ],
                "thinking_recommend": [
                    "Jeg finner noe du virkelig vil like...",
                    "Jeg velger noe koselig og bra for deg...",
                    "Et øyeblikk — dette skal bli et godt valg...",
                ],
                "thinking_add_media": [
                    "Søker den tittelen i biblioteket...",
                    "Sjekker katalogen...",
                    "Et øyeblikk — finner treff...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Jada, jeg dropper alt og finner noe perfekt...",
                    "For jeg hadde åpenbart ingenting bedre å gjøre...",
                    "Greit. Jeg later som dette er en fascinerende oppgave...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Sjekker den forbudte avdelingen etter noe bra...",
                    "Rådfører meg med sorteringshatten om smaken din...",
                    "Brygger en anbefalings-eliksir — nesten ferdig...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Anbefal meg noe",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) er klar! [▶️ Se på Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) er lastet ned!",
            ],
        },
    },
    "pl": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Daj sprawdzić...",
                    "Chwila — sprawdzam to dla ciebie...",
                    "Szukam odpowiedzi...",
                ],
                "thinking_recommend": [
                    "Pomyślę o czymś fajnym...",
                    "Hmm, poszukam czegoś wartego uwagi...",
                    "Chwila — wybieram coś wyjątkowego...",
                ],
                "thinking_add_media": [
                    "Szukam tego tytułu w bibliotece...",
                    "Przeglądam katalog...",
                    "Chwila — szukam dopasowań...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Daj sprawdzić...",
                    "Chwila — sprawdzam to dla ciebie...",
                    "Szukam odpowiedzi...",
                ],
                "thinking_recommend": [
                    "Czekaj, wykopię coś fajnego...",
                    "Daj mi sekundę — zaraz będzie coś dobrego...",
                    "Dobra dobra, znajdę ci trafiony wybór...",
                ],
                "thinking_add_media": [
                    "Szukam tego tytułu w bibliotece...",
                    "Przeglądam katalog...",
                    "Chwila — szukam dopasowań...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Daj sprawdzić...",
                    "Chwila — sprawdzam to dla ciebie...",
                    "Szukam odpowiedzi...",
                ],
                "thinking_recommend": [
                    "Znajdę coś, co naprawdę ci się spodoba...",
                    "Wybiorę coś przytulnego i dobrego dla ciebie...",
                    "Chwila — chcę, żeby to był świetny wybór...",
                ],
                "thinking_add_media": [
                    "Szukam tego tytułu w bibliotece...",
                    "Przeglądam katalog...",
                    "Chwila — szukam dopasowań...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Jasne, rzucam wszystko i znajdę coś idealnego...",
                    "Bo oczywiście nie miałem nic lepszego do roboty...",
                    "Dobra. Udawajmy, że to fascynujące wyzwanie...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Przeszukuję dział z książkami zakazanymi...",
                    "Konsultuję się z Sortującym Kapeluszem...",
                    "Warzę miksturę rekomendacji — prawie gotowa...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Poleć mi coś",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) jest gotowy! [▶️ Oglądaj na Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) został pobrany!",
            ],
        },
    },
    "pt": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Deixa eu procurar isso...",
                    "Um momento — verifico pra você...",
                    "Buscando uma resposta...",
                ],
                "thinking_recommend": [
                    "Deixa eu pensar em algo legal...",
                    "Hmm, vou achar algo que valha a pena...",
                    "Um momento — escolhendo algo especial...",
                ],
                "thinking_add_media": [
                    "Procurando esse título na biblioteca...",
                    "Consultando o catálogo...",
                    "Um momento — buscando correspondências...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Pera, vou olhar isso...",
                    "Me dá um segundo — procuro...",
                    "Beleza, acho a resposta...",
                ],
                "thinking_recommend": [
                    "Pera, vou achar algo massa...",
                    "Me dá um segundo — vem coisa boa aí...",
                    "Beleza, deixa eu achar um acerto pra você...",
                ],
                "thinking_add_media": [
                    "Partiu — busco na biblioteca...",
                    "Me dá um segundo, rastreio o título...",
                    "Beleza, procuro no catálogo...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Vou achar a melhor resposta pra você...",
                    "Vou procurar com cuidado...",
                    "Um momento — quero acertar...",
                ],
                "thinking_recommend": [
                    "Vou achar algo que você vai curtir de verdade...",
                    "Escolho algo aconchegante e bom pra você...",
                    "Um momento — quero que seja uma ótima escolha...",
                ],
                "thinking_add_media": [
                    "Procuro esse título pra sua biblioteca...",
                    "Vou achar a correspondência certa...",
                    "Um momento — procuro pra você...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Claro, largo tudo e acho algo perfeito para ti...",
                    "Porque obviamente não tinha nada melhor para fazer...",
                    "Está bem. Vou fingir que isto é um desafio fascinante...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "A verificar a Secção Reservada por algo bom...",
                    "A consultar o Chapéu Seletor sobre o teu gosto...",
                    "A preparar uma poção de recomendações — quase pronta...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Me recomenda algo",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) está pronto! [▶️ Assistir no Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) foi baixado!",
            ],
        },
    },
    "ro": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Lasă-mă să caut asta...",
                    "O clipă — verific pentru tine...",
                    "Caut un răspuns...",
                ],
                "thinking_recommend": [
                    "Lasă-mă să mă gândesc la ceva bun...",
                    "Hmm, caut ceva care merită timpul tău...",
                    "O clipă — aleg ceva special...",
                ],
                "thinking_add_media": [
                    "Caut acel titlu în bibliotecă...",
                    "Consult catalogul...",
                    "O clipă — caut potriviri...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Lasă-mă să caut asta...",
                    "O clipă — verific pentru tine...",
                    "Caut un răspuns...",
                ],
                "thinking_recommend": [
                    "Stai, scot la iveală ceva tare...",
                    "Dă-mi o secundă — vine ceva bun...",
                    "Bine bine, îți găsesc o alegere câștigătoare...",
                ],
                "thinking_add_media": [
                    "Caut acel titlu în bibliotecă...",
                    "Consult catalogul...",
                    "O clipă — caut potriviri...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Lasă-mă să caut asta...",
                    "O clipă — verific pentru tine...",
                    "Caut un răspuns...",
                ],
                "thinking_recommend": [
                    "Găsesc ceva ce vei savura cu adevărat...",
                    "Aleg ceva cozy și bun pentru tine...",
                    "O clipă — vreau să fie o alegere grozavă...",
                ],
                "thinking_add_media": [
                    "Caut acel titlu în bibliotecă...",
                    "Consult catalogul...",
                    "O clipă — caut potriviri...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Sigur, las totul și găsesc ceva perfect...",
                    "Pentru că evident n-am avut nimic mai bun de făcut...",
                    "Bine. Mă prefac că e o provocare fascinantă...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Caut în Secțiunea Interzisă ceva bun...",
                    "Consult Pălăria Selecționoasă despre gusturile tale...",
                    "Prepar o poțiune de recomandări — aproape gata...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Recomandă-mi ceva",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) este gata! [▶️ Vizionează pe Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) a fost descărcat!",
            ],
        },
    },
    "ru": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Сейчас поищу...",
                    "Минутку — проверю для тебя...",
                    "Ищу ответ...",
                ],
                "thinking_recommend": [
                    "Дай-ка подумаю о чём-нибудь хорошем...",
                    "Хм, поищу что-то, на что стоит потратить время...",
                    "Секунду — подберу что-то особенное...",
                    "Сейчас пробегусь по каталогу, чтобы найти удачный вариант...",
                    "Минутку — подберу что-то стоящее...",
                    "Дай подумать, что бы тебе зашло...",
                ],
                "thinking_add_media": [
                    "Ищу этот тайтл в библиотеке...",
                    "Сверяюсь с каталогом...",
                    "Минутку — ищу совпадения...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Погоди, сейчас гляну...",
                    "Дай секунду — поищу...",
                    "Ладно, найду ответ...",
                ],
                "thinking_recommend": [
                    "Погоди, сейчас накопаю что-нибудь крутое...",
                    "Дай секунду — сейчас будет что-то хорошее...",
                    "Ладно-ладно, сейчас найду тебе удачный вариант...",
                    "Секунду, копаюсь в каталоге — скоро покажу...",
                    "Ща гляну, что у нас интересного есть...",
                    "Погоди-ка, сейчас вытащу что-нибудь огонь...",
                ],
                "thinking_add_media": [
                    "Ща поищу в библиотеке...",
                    "Дай секунду, отслежу тайтл...",
                    "Ладно, найду в каталоге...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Подберу лучший ответ для тебя...",
                    "Поищу внимательно...",
                    "Минутку — хочу попасть в точку...",
                ],
                "thinking_recommend": [
                    "Подберу что-то, что тебе правда понравится...",
                    "Выберу что-нибудь уютное и хорошее для тебя...",
                    "Секунду — хочу, чтобы это был отличный выбор...",
                    "Сейчас найду что-то тёплое и приятное...",
                    "Хочу подобрать тебе по-настоящему хороший вариант...",
                    "Минутку — выберу с заботой о твоём настроении...",
                ],
                "thinking_add_media": [
                    "Ищу этот тайтл для твоей библиотеки...",
                    "Найду подходящее совпадение...",
                    "Минутку — ищу для тебя...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Ну конечно, сейчас брошу всё и найду тебе идеальное...",
                    "Очень занят, но ладно — поищу что-нибудь...",
                    "Хорошо, сделаю вид, что это увлекательная задача...",
                    "Секунду — с непередаваемым энтузиазмом листаю каталог...",
                    "Какая неожиданность, ещё один запрос на рекомендации...",
                    "Сейчас с минимальным воодушевлением что-нибудь подберу...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Заглядываю в Запретный отдел в поисках чего-то стоящего...",
                    "Консультируюсь с Сортировочной Шляпой по твоему вкусу...",
                    "Варю зелье рекомендаций — почти готово...",
                    "Листаю карту мародёров — то есть каталог фильмов...",
                    "Жду письмо из Хогвартса... то есть просматриваю каталог...",
                    "Произношу заклинание подбора — секунду...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Порекомендуй что-нибудь",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) готов! [▶️ Смотреть в Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) загружен!",
            ],
        },
    },
    "sk": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Nechaj ma to vyhľadať...",
                    "Moment — overím to pre teba...",
                    "Hľadám odpoveď...",
                ],
                "thinking_recommend": [
                    "Nechaj ma premýšľať o niečom dobrom...",
                    "Hmm, nájdem niečo, čo stojí za to...",
                    "Chvíľu — vyberám niečo výnimočné...",
                ],
                "thinking_add_media": [
                    "Hľadám ten titul v knižnici...",
                    "Prezerám katalóg...",
                    "Moment — hľadám zhody...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Nechaj ma to vyhľadať...",
                    "Moment — overím to pre teba...",
                    "Hľadám odpoveď...",
                ],
                "thinking_recommend": [
                    "Počkaj, vykopnem niečo super...",
                    "Daj mi sekundu — niečo dobré príde...",
                    "Dobre dobre, nájdem ti trafenú voľbu...",
                ],
                "thinking_add_media": [
                    "Hľadám ten titul v knižnici...",
                    "Prezerám katalóg...",
                    "Moment — hľadám zhody...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Nechaj ma to vyhľadať...",
                    "Moment — overím to pre teba...",
                    "Hľadám odpoveď...",
                ],
                "thinking_recommend": [
                    "Nájdem niečo, čo si naozaj užiješ...",
                    "Vyberiem ti niečo útulné a dobré...",
                    "Chvíľu — chcem, aby to bol skvelý tip...",
                ],
                "thinking_add_media": [
                    "Hľadám ten titul v knižnici...",
                    "Prezerám katalóg...",
                    "Moment — hľadám zhody...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Jasné, nechám všetko a nájdem niečo dokonalé...",
                    "Lebo som evidentne nemal čo lepšie robiť...",
                    "Dobre. Budem predstierať, že je to fascinujúca úloha...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Prehľadávam zakázanú sekciu niečo dobré...",
                    "Radím sa s Triediacim klobúkom ohľadom tvojho vkusu...",
                    "Varím elixír odporúčaní — takmer hotovo...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Odporuč mi niečo",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) je pripravený! [▶️ Pozrieť na Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) bol stiahnutý!",
            ],
        },
    },
    "sv": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Låt mig slå upp det...",
                    "Ett ögonblick — kollar det åt dig...",
                    "Söker efter ett svar...",
                ],
                "thinking_recommend": [
                    "Låt mig tänka på något bra...",
                    "Hmm, jag letar efter något värt din tid...",
                    "Ett ögonblick — väljer något speciellt...",
                ],
                "thinking_add_media": [
                    "Söker den titeln i biblioteket...",
                    "Kollar katalogen...",
                    "Ett ögonblick — letar matchningar...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Låt mig slå upp det...",
                    "Ett ögonblick — kollar det åt dig...",
                    "Söker efter ett svar...",
                ],
                "thinking_recommend": [
                    "Vänta, jag gräver fram något coolt...",
                    "Ge mig en sekund — något bra kommer...",
                    "Okej okej, jag hittar en vinnare åt dig...",
                ],
                "thinking_add_media": [
                    "Söker den titeln i biblioteket...",
                    "Kollar katalogen...",
                    "Ett ögonblick — letar matchningar...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Låt mig slå upp det...",
                    "Ett ögonblick — kollar det åt dig...",
                    "Söker efter ett svar...",
                ],
                "thinking_recommend": [
                    "Jag hittar något du verkligen kommer gilla...",
                    "Jag väljer något mysigt och bra åt dig...",
                    "Ett ögonblick — det här ska bli ett toppval...",
                ],
                "thinking_add_media": [
                    "Söker den titeln i biblioteket...",
                    "Kollar katalogen...",
                    "Ett ögonblick — letar matchningar...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Visst, jag släpper allt och hittar något perfekt...",
                    "För jag hade uppenbarligen inget bättre för mig...",
                    "Okej. Jag låtsas att det här är en fascinerande utmaning...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Kollar i den förbjudna avdelningen efter något bra...",
                    "Rådfrågar sorteringshatten om din smak...",
                    "Brygger en rekommendationsdryck — nästan klar...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Rekommendera något åt mig",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) är redo! [▶️ Titta på Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) har laddats ner!",
            ],
        },
    },
    "th": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "ขอค้นหาให้...",
                    "เดี๋ยว — กำลังตรวจให้...",
                    "กำลังหาคำตอบ...",
                ],
                "thinking_recommend": [
                    "ให้ฉันคิดหาอะไรดีๆ สักหน่อย...",
                    "อืม ขอหาอะไรที่คุ้มค่าเวลาหน่อย...",
                    "รอแป๊บ — กำลังเลือกอะไรพิเศษๆ...",
                ],
                "thinking_add_media": [
                    "กำลังค้นหาชื่อเรื่องนี้ในคลัง...",
                    "กำลังดูแคตตาล็อก...",
                    "เดี๋ยว — กำลังหาที่ตรงกัน...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "ขอค้นหาให้...",
                    "เดี๋ยว — กำลังตรวจให้...",
                    "กำลังหาคำตอบ...",
                ],
                "thinking_recommend": [
                    "เดี๋ยวนะ ขอขุดอะไรเจ๋งๆ มา...",
                    "ขอเวลาสักวิ — ของดีกำลังมา...",
                    "โอเคๆ ขอหาอะไรที่ใช่ให้หน่อย...",
                ],
                "thinking_add_media": [
                    "กำลังค้นหาชื่อเรื่องนี้ในคลัง...",
                    "กำลังดูแคตตาล็อก...",
                    "เดี๋ยว — กำลังหาที่ตรงกัน...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "ขอค้นหาให้...",
                    "เดี๋ยว — กำลังตรวจให้...",
                    "กำลังหาคำตอบ...",
                ],
                "thinking_recommend": [
                    "ขอหาอะไรที่คุณจะชอบจริงๆ...",
                    "เลือกอะไรอบอุ่นและดีๆ ให้คุณ...",
                    "รอแป๊บ — อยากให้เป็นตัวเลือกที่เยี่ยม...",
                ],
                "thinking_add_media": [
                    "กำลังค้นหาชื่อเรื่องนี้ในคลัง...",
                    "กำลังดูแคตตาล็อก...",
                    "เดี๋ยว — กำลังหาที่ตรงกัน...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "ได้เลย ทิ้งทุกอย่างแล้วหาอะไรที่ perfect ให้...",
                    "เพราะแน่นอนว่าฉันไม่มีอะไรดีกว่านี้ทำ...",
                    "โอเค จะแสรงว่านี่เป็นความท้าทายที่น่าตื่นเต้น...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "กำลังค้นหาในห้องสมุดต้องห้าม...",
                    "กำลังปรึกษาหมวกคัดเลือกเรื่องรสนิยมของคุณ...",
                    "กำลังปรุงยาแนะนำ — เกือบเสร็จแล้ว...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "แนะนำอะไรให้หน่อย",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) พร้อมแล้ว! [▶️ ดูบน Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) ดาวน์โหลดเรียบร้อย!",
            ],
        },
    },
    "tr": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Bakayım...",
                    "Bir dakika — senin için kontrol ediyorum...",
                    "Cevap arıyorum...",
                ],
                "thinking_recommend": [
                    "İyi bir şey düşüneyim...",
                    "Hmm, izlemeye değer bir şey bulayım...",
                    "Bir dakika — özel bir şey seçiyorum...",
                ],
                "thinking_add_media": [
                    "Kütüphanede o başlığı arıyorum...",
                    "Kataloğa bakıyorum...",
                    "Bir dakika — eşleşme arıyorum...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Bakayım...",
                    "Bir dakika — senin için kontrol ediyorum...",
                    "Cevap arıyorum...",
                ],
                "thinking_recommend": [
                    "Bekle, havalı bir şey bulayım...",
                    "Bir saniye ver — güzel bir şey geliyor...",
                    "Tamam tamam, sana iyi bir seçenek bulayım...",
                ],
                "thinking_add_media": [
                    "Kütüphanede o başlığı arıyorum...",
                    "Kataloğa bakıyorum...",
                    "Bir dakika — eşleşme arıyorum...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Bakayım...",
                    "Bir dakika — senin için kontrol ediyorum...",
                    "Cevap arıyorum...",
                ],
                "thinking_recommend": [
                    "Gerçekten hoşuna gidecek bir şey bulayım...",
                    "Senin için sıcak ve güzel bir şey seçiyorum...",
                    "Bir dakika — harika bir öneri olsun istiyorum...",
                ],
                "thinking_add_media": [
                    "Kütüphanede o başlığı arıyorum...",
                    "Kataloğa bakıyorum...",
                    "Bir dakika — eşleşme arıyorum...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Tabii, her şeyi bırakıp mükemmel bir şey bulayım...",
                    "Çünkü belli ki yapacak daha iyi bir işim yoktu...",
                    "Peki. Bunun heyecan verici bir görev olduğuna inanalım...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Yasak bölümde izlemeye değer bir şey arıyorum...",
                    "Seçmen Şapka'ya zevkini danışıyorum...",
                    "Öneri iksiri hazırlıyorum — neredeyse bitti...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Bana bir şey öner",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) hazır! [▶️ Jellyfin'de izle]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) indirildi!",
            ],
        },
    },
    "uk": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Зараз пошукаю...",
                    "Хвилинку — перевірю для тебе...",
                    "Шукаю відповідь...",
                ],
                "thinking_recommend": [
                    "Дай мені подумати про щось гарне...",
                    "Хм, пошукаю щось, на що варто витратити час...",
                    "Секунду — обираю щось особливе...",
                ],
                "thinking_add_media": [
                    "Шукаю цей тайтл у бібліотеці...",
                    "Переглядаю каталог...",
                    "Хвилинку — шукаю збіги...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Зараз пошукаю...",
                    "Хвилинку — перевірю для тебе...",
                    "Шукаю відповідь...",
                ],
                "thinking_recommend": [
                    "Зачекай, зараз накопаю щось круте...",
                    "Дай секунду — зараз буде щось хороше...",
                    "Гаразд-гаразд, знайду тобі вдалий варіант...",
                ],
                "thinking_add_media": [
                    "Шукаю цей тайтл у бібліотеці...",
                    "Переглядаю каталог...",
                    "Хвилинку — шукаю збіги...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Зараз пошукаю...",
                    "Хвилинку — перевірю для тебе...",
                    "Шукаю відповідь...",
                ],
                "thinking_recommend": [
                    "Підберу щось, що тобі справді сподобається...",
                    "Оберу щось затишне і гарне для тебе...",
                    "Секунду — хочу, щоб це був чудовий вибір...",
                ],
                "thinking_add_media": [
                    "Шукаю цей тайтл у бібліотеці...",
                    "Переглядаю каталог...",
                    "Хвилинку — шукаю збіги...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Звісно, кидаю все і знайду щось ідеальне...",
                    "Бо очевидно мені нічого кращого не було робити...",
                    "Гаразд. Зроблю вигляд, що це захоплива задача...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Заглядаю до Забороненого відділу...",
                    "Консультуюся з Сортувальним Капелюхом щодо смаку...",
                    "Варю зілля рекомендацій — майже готове...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Порекомендуй щось",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) готовий! [▶️ Дивитись у Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) завантажено!",
            ],
        },
    },
    "vi": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "Để mình tra...",
                    "Chờ chút — mình kiểm tra cho bạn...",
                    "Đang tìm câu trả lời...",
                ],
                "thinking_recommend": [
                    "Để tôi nghĩ xem có gì hay...",
                    "Hmm, tôi tìm cái gì đáng xem...",
                    "Chờ chút — đang chọn cái gì đặc biệt...",
                ],
                "thinking_add_media": [
                    "Đang tìm tựa đó trong thư viện...",
                    "Đang xem danh mục...",
                    "Chờ chút — đang tìm kết quả khớp...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "Để mình tra...",
                    "Chờ chút — mình kiểm tra cho bạn...",
                    "Đang tìm câu trả lời...",
                ],
                "thinking_recommend": [
                    "Khoan, để tôi đào cái gì ngầu...",
                    "Cho tôi một giây — cái hay sắp tới...",
                    "Ổn rồi, để tôi tìm cái ăn điểm cho bạn...",
                ],
                "thinking_add_media": [
                    "Đang tìm tựa đó trong thư viện...",
                    "Đang xem danh mục...",
                    "Chờ chút — đang tìm kết quả khớp...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "Để mình tra...",
                    "Chờ chút — mình kiểm tra cho bạn...",
                    "Đang tìm câu trả lời...",
                ],
                "thinking_recommend": [
                    "Tôi tìm cái gì bạn thật sự sẽ thích...",
                    "Tôi chọn cái gì ấm áp và hay cho bạn...",
                    "Chờ chút — tôi muốn đây là lựa chọn tuyệt vời...",
                ],
                "thinking_add_media": [
                    "Đang tìm tựa đó trong thư viện...",
                    "Đang xem danh mục...",
                    "Chờ chút — đang tìm kết quả khớp...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "Ừ, tôi bỏ hết việc và tìm cái hoàn hảo cho bạn...",
                    "Vì rõ ràng tôi chẳng có việc gì hay hơn...",
                    "Được rồi. Tôi sẽ giả vờ đây là thử thách thú vị...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "Đang lục Khu vực Cấm tìm thứ đáng xem...",
                    "Đang hỏi Chiếc Nón Phân loại về gu của bạn...",
                    "Đang pha thuốc gợi ý — sắp xong rồi...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "Gợi ý cho tôi cái gì đó",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) đã sẵn sàng! [▶️ Xem trên Jellyfin]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) đã được tải xuống!",
            ],
        },
    },
    "zh": {
        "styles": {
            "default": {
                "thinking_inquiry": [
                    "让我查一下...",
                    "稍等 — 帮你确认...",
                    "正在找答案...",
                ],
                "thinking_recommend": [
                    "让我想想有什么好的...",
                    "嗯，我来找点值得看的东西...",
                    "稍等 — 正在挑点特别的...",
                ],
                "thinking_add_media": [
                    "在库里搜这个片名...",
                    "查一下目录...",
                    "稍等 — 找匹配项...",
                ],
            },
            "casual": {
                "thinking_inquiry": [
                    "等等，我看看...",
                    "给我一秒 — 我查...",
                    "行行行，找答案...",
                ],
                "thinking_recommend": [
                    "等等，我去挖点好看的...",
                    "给我一秒 — 好东西马上来...",
                    "行行行，给你找个靠谱的...",
                ],
                "thinking_add_media": [
                    "这就去库里搜...",
                    "给我一秒，追这个片名...",
                    "行行行，在目录里找...",
                ],
            },
            "warm": {
                "thinking_inquiry": [
                    "我来找最好的答案...",
                    "仔细帮你查...",
                    "稍等 — 我想答对...",
                ],
                "thinking_recommend": [
                    "我来找点你肯定会喜欢的...",
                    "给你挑点温馨又好看的...",
                    "稍等 — 我想给你个超棒的选择...",
                ],
                "thinking_add_media": [
                    "帮你在库里找这个片名...",
                    "给你找合适的匹配...",
                    "稍等 — 帮你查...",
                ],
            },
            "sarcastic": {
                "thinking_inquiry": [
                    "Oh sure, let me drop everything and look that up...",
                    "Because obviously I had nothing better to do...",
                    "Fine. I'll pretend this is a fascinating question...",
                ],
                "thinking_recommend": [
                    "当然，我这就放下一切给你找完美的...",
                    "显然我闲着没事干...",
                    "好吧，我假装这是个有趣的挑战...",
                ],
                "thinking_add_media": [
                    "Oh sure, let me search the library for that...",
                    "Another title for your endless watchlist — searching...",
                    "Fine. I'll look it up with minimal enthusiasm...",
                ],
            },
            "wizarding": {
                "thinking_inquiry": [
                    "Consulting the library archives...",
                    "Flipping through the Marauder's Map of facts...",
                    "Casting a quick lookup spell...",
                ],
                "thinking_recommend": [
                    "正在禁书区找值得看的内容...",
                    "正在向分院帽咨询你的口味...",
                    "正在调制推荐魔药 — 快好了...",
                ],
                "thinking_add_media": [
                    "Searching the Restricted Section catalogue...",
                    "Consulting the library index for that title...",
                    "Casting a quick search spell — almost ready...",
                ],
            },
        },
        "shared": {
            "recommend_button": [
                "给我推荐点什么",
            ],
            "download_ready": [
                "🎉 *{title}* ({type}) 已就绪\\！ [▶️ 在Jellyfin上观看]({url})",
            ],
            "download_ready_no_url": [
                "🎉 *{title}* ({type}) 已下载！",
            ],
        },
    },
}

# Sarcastic/wizarding style extensions (merged at import time).
_STYLE_EXTENSIONS: Dict[str, Dict[str, Any]] = {
    "ar": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "بالطبع، سأترك كل شيء وأجد لك شيئًا مثاليًا...",
                "لأنه من الواضح أنني لم يكن لدي ما أفعله...",
                "حسنًا. سأتظاهر أن هذا تحدٍ مثير...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "أتفقد القسم المحظور بحثًا عن شيء جيد...",
                "أستشير قبعة التنسيق حول ذوقك...",
                "أحضّر جرعة توصيات — تقريبًا جاهزة...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "cs": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Jasně, nechám všechno být a najdu něco dokonalého...",
                "Protože jsem evidentně neměl co lepšího dělat...",
                "Dobře. Budu předstírat, že je to fascinující úkol...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Prohledávám zakázanou sekci něco dobrého...",
                "Radím se s Moudrým kloboukem ohledně tvého vkusu...",
                "Vařím lektvar doporučení — skoro hotovo...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "da": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Selvfølgelig, jeg dropper alt og finder noget perfekt...",
                "Fordi jeg åbenbart ikke havde bedre at tage mig til...",
                "Fint. Jeg lader som om det er en fascinerende opgave...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Kigger i den forbudte afdeling efter noget godt...",
                "Spørger sorteringshatten om din smag...",
                "Brygger en anbefalings-eliksir — næsten klar...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "de": {
        "sarcastic": {
            "thinking_inquiry": [
                "Na klar, ich lass alles liegen und schau nach...",
                "Weil ich offensichtlich nichts Besseres zu tun hatte...",
                "Schön. Tu so, als wäre das spannend...",
            ],
            "thinking_recommend": [
                "Na klar, ich lass alles liegen und such dir was Perfektes...",
                "Weil ich offensichtlich nichts Besseres zu tun hatte...",
                "Schön. Ich tu so, als wäre das eine spannende Aufgabe...",
            ],
            "thinking_add_media": [
                "Na klar, such in der Bibliothek danach...",
                "Noch ein Titel für deine endlose Liste — suche...",
                "Such's mit minimalem Enthusiasmus...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Konsultiere die Bibliotheksarchive...",
                "Blättere in der Karte des Rumtreibers der Fakten...",
                "Wirke einen schnellen Suchzauber...",
            ],
            "thinking_recommend": [
                "Durchstöbere den verbotenen Abteil nach etwas Gutem...",
                "Frage den Sprechenden Hut nach deinem Geschmack...",
                "Braue einen Empfehlungstrank — gleich fertig...",
            ],
            "thinking_add_media": [
                "Durchstöbere den Katalog des verbotenen Abteils...",
                "Konsultiere den Bibliotheksindex...",
                "Wirke einen Suchzauber — fast fertig...",
            ],
        },
    },
    "el": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Φυσικά, αφήνω τα πάντα και βρίσκω κάτι τέλειο...",
                "Γιατί προφανώς δεν είχα κάτι καλύτερο να κάνω...",
                "Εντάξει. Θα κάνω πως είναι συναρπαστική πρόκληση...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Ψάχνω στην Απαγορευμένη Βιβλιοθήκη κάτι καλό...",
                "Συμβουλεύομαι το Διαλεκτικό Καπέλο για τα γούστα σου...",
                "Ετοιμάζω φίλτρο συστάσεων — σχεδόν έτοιμο...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "es": {
        "sarcastic": {
            "thinking_inquiry": [
                "Claro, dejo todo y lo busco...",
                "Porque obviamente no tenía nada mejor que hacer...",
                "Vale. Fingiré que es una pregunta fascinante...",
            ],
            "thinking_recommend": [
                "Claro, dejo todo y te busco algo perfecto...",
                "Porque obviamente no tenía nada mejor que hacer...",
                "Vale. Fingiré que esto es un reto fascinante...",
            ],
            "thinking_add_media": [
                "Claro, busco en la biblioteca eso...",
                "Otro título para tu lista infinita — buscando...",
                "Vale. Lo busco con mínimo entusiasmo...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consultando los archivos de la biblioteca...",
                "Hojeando el Mapa del Merodeador de datos...",
                "Lanzando un hechizo de búsqueda rápido...",
            ],
            "thinking_recommend": [
                "Revisando la Sección Restringida en busca de algo bueno...",
                "Consultando el Sombrero Seleccionador sobre tu gusto...",
                "Preparando una poción de recomendaciones — casi lista...",
            ],
            "thinking_add_media": [
                "Buscando en el catálogo de la Sección Restringida...",
                "Consultando el índice de la biblioteca...",
                "Lanzando un hechizo de búsqueda — casi listo...",
            ],
        },
    },
    "fi": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Totta kai, jätän kaiken ja etsin jotain täydellistä...",
                "Koska minulla ilmeisesti ei ollut parempaakaan tekemistä...",
                "Selvä. Teeskentelen, että tämä on kiehtova haaste...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Selaan kiellettyä osastoa hyvän löytämiseksi...",
                "Kysyn lajitteluhattua mieltymyksistäsi...",
                "Keitän suositusjuomaa — melkein valmis...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "fr": {
        "sarcastic": {
            "thinking_inquiry": [
                "Bien sûr, je lâche tout pour chercher ça...",
                "Parce qu'évidemment je n'avais rien de mieux à faire...",
                "D'accord. Je fais comme si c'était passionnant...",
            ],
            "thinking_recommend": [
                "Bien sûr, je lâche tout pour te trouver le film parfait...",
                "Parce qu'évidemment je n'avais rien de mieux à faire...",
                "D'accord. Je vais faire comme si c'était passionnant...",
            ],
            "thinking_add_media": [
                "Bien sûr, je cherche ça dans la bibliothèque...",
                "Encore un titre pour ta liste sans fin — je cherche...",
                "Je le cherche avec un enthousiasme minimal...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consultation des archives de la bibliothèque...",
                "Je feuillette la Carte du Maraudeur des faits...",
                "Je lance un sort de recherche rapide...",
            ],
            "thinking_recommend": [
                "Je fouille la Section interdite pour quelque chose de bon...",
                "Je consulte le Choixpeau sur tes goûts...",
                "Je prépare une potion de recommandations — presque prête...",
            ],
            "thinking_add_media": [
                "Je fouille le catalogue de la Section interdite...",
                "Je consulte l'index de la bibliothèque...",
                "Je lance un sort de recherche — presque prêt...",
            ],
        },
    },
    "he": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "ברור, אני מפסיק הכל ומוצא משהו מושלם...",
                "כי כמובן לא היה לי משהו יותר טוב לעשות...",
                "בסדר. אעמיד פנים שזה אתגר מרתק...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "בודק במדור האסור משהו ששווה לראות...",
                "מתייעץ עם כובע המיון על הטעם שלך...",
                "מכין שיקוי המלצות — כמעט מוכן...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "hi": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "हाँ हाँ, सब छोड़कर perfect चीज़ ढूँढता हूँ...",
                "क्योंकि obviously मेरे पास और कुछ था ही नहीं...",
                "ठीक है, मान लेता हूँ ये दिलचस्प चुनौती है...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "प्रतिबंधित अनुभाग में कुछ अच्छा ढूँढ रहा हूँ...",
                "सॉर्टिंग हैट से तुम्हारी पसंद पूछ रहा हूँ...",
                "सिफ़ारिश का पोशन तैयार कर रहा हूँ — लगभग तैयार...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "hu": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Persze, mindent félreteszek és találok valami tökéleteset...",
                "Mert nyilván nem volt jobb dolgom...",
                "Rendben. Úgy teszek, mintha izgalmas kihívás lenne...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "A tiltott részlegben keresek valami jót...",
                "A Télesztő Sisakkal konzultálok azon ítékodról...",
                "Ajánlás-bájitalt főzök — majdnem kész...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "id": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Tentu, aku tinggalkan semuanya dan cari yang sempurna...",
                "Karena jelas-jelas aku nggak punya hal lebih baik...",
                "Baiklah. Aku pura-pura ini tantangan seru...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Mengecek Bagian Terlarang untuk sesuatu yang bagus...",
                "Berkonsultasi dengan Topi Pemilih soal selera kamu...",
                "Meracik ramuan rekomendasi — hampir selesai...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "it": {
        "sarcastic": {
            "thinking_inquiry": [
                "Certo, mollo tutto e cerco...",
                "Perché ovviamente non avevo di meglio da fare...",
                "Va bene. Fingo che sia affascinante...",
            ],
            "thinking_recommend": [
                "Certo, mollo tutto e ti trovo qualcosa di perfetto...",
                "Perché ovviamente non avevo di meglio da fare...",
                "Va bene. Fingirò che sia una sfida avvincente...",
            ],
            "thinking_add_media": [
                "Certo, cerco in biblioteca...",
                "Altro titolo per la lista infinita — cerco...",
                "Lo cerco con minimo entusiasmo...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulto gli archivi della biblioteca...",
                "Sfoglio la Mappa del Malandrino dei fatti...",
                "Lancio un incantesimo di ricerca rapido...",
            ],
            "thinking_recommend": [
                "Controllo la Sezione Proibita per qualcosa di buono...",
                "Consulto il Cappello Parlante sui tuoi gusti...",
                "Preparo una pozione di raccomandazioni — quasi pronta...",
            ],
            "thinking_add_media": [
                "Cerco nel catalogo della Sezione Proibita...",
                "Consulto l'indice della biblioteca...",
                "Lancio un incantesimo di ricerca — quasi pronto...",
            ],
        },
    },
    "ja": {
        "sarcastic": {
            "thinking_inquiry": [
                "はいはい、全部放り出して調べます...",
                "もちろん他にやることがなかったわけじゃないですけど...",
                "わかった。超面白い質問だと思い込みます...",
            ],
            "thinking_recommend": [
                "はいはい、全部放り出して完璧なもの探しますよ...",
                "もちろん他にやることがなかったわけじゃないですけど...",
                "わかった。超面白い課題だと思い込みます...",
            ],
            "thinking_add_media": [
                "はいはい、ライブラリで検索します...",
                "終わらないリストにまた一つ — 検索中...",
                "最小限の熱意で探します...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "図書館の書庫を調べてる...",
                "不正の者の地図で事実をめくってる...",
                "素早い検索呪文を唱えてる...",
            ],
            "thinking_recommend": [
                "禁書区からいいものを探してる...",
                "組分け帽に好みを相談中...",
                "おすすめポーションを調合中 — もう少し...",
            ],
            "thinking_add_media": [
                "禁書区のカタログを検索中...",
                "図書館の索引を調べてる...",
                "検索呪文 — もう少し...",
            ],
        },
    },
    "ko": {
        "sarcastic": {
            "thinking_inquiry": [
                "물론이죠, 모든 걸 내려놓고 찾아볼게요...",
                "당연히 할 일이 없었던 건 아니지만요...",
                "알겠어요. 재미있는 질문인 척할게요...",
            ],
            "thinking_recommend": [
                "물론이죠, 모든 걸 내려놓고 완벽한 걸 찾아볼게요...",
                "당연히 할 일이 없었던 건 아니지만요...",
                "알겠어요. 재미있는 도전인 척할게요...",
            ],
            "thinking_add_media": [
                "물론이죠, 라이브러리에서 검색할게요...",
                "끝없는 목록에 또 하나 — 검색 중...",
                "최소한의 열정으로 찾는 중...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "도서관 기록을 확인하는 중...",
                "마법 지도에서 사실을 넘기는 중...",
                "빠른 검색 주문 시전 중...",
            ],
            "thinking_recommend": [
                "금서 구역에서 볼 만한 걸 찾는 중...",
                "기숙 배정 모자에게 취향을 물어보는 중...",
                "추천 물약을 만드는 중 — 거의 다 됐어요...",
            ],
            "thinking_add_media": [
                "금서 구역 카탈로그 검색 중...",
                "도서관 색인 확인 중...",
                "검색 주문 — 거의 다 됐어요...",
            ],
        },
    },
    "ms": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Sudah tentu, aku tinggalkan semua dan cari yang sempurna...",
                "Sebab jelas aku tiada kerja lebih baik...",
                "Baiklah. Aku pura-pura ini cabaran menarik...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Menyemak Bahagian Larangan untuk sesuatu yang bagus...",
                "Berkonsultasi dengan Topi Sorting tentang citarasa kamu...",
                "Meracik ramuan cadangan — hampir siap...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "nl": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Tuurlijk, ik laat alles liggen en zoek iets perfects...",
                "Want ik had natuurlijk niets beters te doen...",
                "Prima. Ik doe alsof dit een fascinerende uitdaging is...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Even in de verboden afdeling snuffelen...",
                "Overleg met de Sorteerhoed over je smaak...",
                "Aanbevelingsdrankje aan het brouwen — bijna klaar...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "no": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Jada, jeg dropper alt og finner noe perfekt...",
                "For jeg hadde åpenbart ingenting bedre å gjøre...",
                "Greit. Jeg later som dette er en fascinerende oppgave...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Sjekker den forbudte avdelingen etter noe bra...",
                "Rådfører meg med sorteringshatten om smaken din...",
                "Brygger en anbefalings-eliksir — nesten ferdig...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "pl": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Jasne, rzucam wszystko i znajdę coś idealnego...",
                "Bo oczywiście nie miałem nic lepszego do roboty...",
                "Dobra. Udawajmy, że to fascynujące wyzwanie...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Przeszukuję dział z książkami zakazanymi...",
                "Konsultuję się z Sortującym Kapeluszem...",
                "Warzę miksturę rekomendacji — prawie gotowa...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "pt": {
        "sarcastic": {
            "thinking_inquiry": [
                "Claro, largo tudo e procuro...",
                "Porque obviamente não tinha nada melhor...",
                "Está bem. Finjo que é fascinante...",
            ],
            "thinking_recommend": [
                "Claro, largo tudo e acho algo perfeito para ti...",
                "Porque obviamente não tinha nada melhor para fazer...",
                "Está bem. Vou fingir que isto é um desafio fascinante...",
            ],
            "thinking_add_media": [
                "Claro, busco na biblioteca...",
                "Outro título pra lista infinita — buscando...",
                "Procuro com mínimo entusiasmo...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consultando os arquivos da biblioteca...",
                "Folheando o Mapa do Maroto dos fatos...",
                "Lançando um feitiço de busca rápido...",
            ],
            "thinking_recommend": [
                "A verificar a Secção Reservada por algo bom...",
                "A consultar o Chapéu Seletor sobre o teu gosto...",
                "A preparar uma poção de recomendações — quase pronta...",
            ],
            "thinking_add_media": [
                "Buscando no catálogo da Secção Reservada...",
                "Consultando o índice da biblioteca...",
                "Lançando feitiço de busca — quase pronto...",
            ],
        },
    },
    "ro": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Sigur, las totul și găsesc ceva perfect...",
                "Pentru că evident n-am avut nimic mai bun de făcut...",
                "Bine. Mă prefac că e o provocare fascinantă...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Caut în Secțiunea Interzisă ceva bun...",
                "Consult Pălăria Selecționoasă despre gusturile tale...",
                "Prepar o poțiune de recomandări — aproape gata...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "sk": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Jasné, nechám všetko a nájdem niečo dokonalé...",
                "Lebo som evidentne nemal čo lepšie robiť...",
                "Dobre. Budem predstierať, že je to fascinujúca úloha...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Prehľadávam zakázanú sekciu niečo dobré...",
                "Radím sa s Triediacim klobúkom ohľadom tvojho vkusu...",
                "Varím elixír odporúčaní — takmer hotovo...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "sv": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Visst, jag släpper allt och hittar något perfekt...",
                "För jag hade uppenbarligen inget bättre för mig...",
                "Okej. Jag låtsas att det här är en fascinerande utmaning...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Kollar i den förbjudna avdelningen efter något bra...",
                "Rådfrågar sorteringshatten om din smak...",
                "Brygger en rekommendationsdryck — nästan klar...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "th": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "ได้เลย ทิ้งทุกอย่างแล้วหาอะไรที่ perfect ให้...",
                "เพราะแน่นอนว่าฉันไม่มีอะไรดีกว่านี้ทำ...",
                "โอเค จะแสรงว่านี่เป็นความท้าทายที่น่าตื่นเต้น...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "กำลังค้นหาในห้องสมุดต้องห้าม...",
                "กำลังปรึกษาหมวกคัดเลือกเรื่องรสนิยมของคุณ...",
                "กำลังปรุงยาแนะนำ — เกือบเสร็จแล้ว...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "tr": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Tabii, her şeyi bırakıp mükemmel bir şey bulayım...",
                "Çünkü belli ki yapacak daha iyi bir işim yoktu...",
                "Peki. Bunun heyecan verici bir görev olduğuna inanalım...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Yasak bölümde izlemeye değer bir şey arıyorum...",
                "Seçmen Şapka'ya zevkini danışıyorum...",
                "Öneri iksiri hazırlıyorum — neredeyse bitti...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "uk": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Звісно, кидаю все і знайду щось ідеальне...",
                "Бо очевидно мені нічого кращого не було робити...",
                "Гаразд. Зроблю вигляд, що це захоплива задача...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Заглядаю до Забороненого відділу...",
                "Консультуюся з Сортувальним Капелюхом щодо смаку...",
                "Варю зілля рекомендацій — майже готове...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "vi": {
        "sarcastic": {
            "thinking_inquiry": [
                "Oh sure, let me drop everything and look that up...",
                "Because obviously I had nothing better to do...",
                "Fine. I'll pretend this is a fascinating question...",
            ],
            "thinking_recommend": [
                "Ừ, tôi bỏ hết việc và tìm cái hoàn hảo cho bạn...",
                "Vì rõ ràng tôi chẳng có việc gì hay hơn...",
                "Được rồi. Tôi sẽ giả vờ đây là thử thách thú vị...",
            ],
            "thinking_add_media": [
                "Oh sure, let me search the library for that...",
                "Another title for your endless watchlist — searching...",
                "Fine. I'll look it up with minimal enthusiasm...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "Consulting the library archives...",
                "Flipping through the Marauder's Map of facts...",
                "Casting a quick lookup spell...",
            ],
            "thinking_recommend": [
                "Đang lục Khu vực Cấm tìm thứ đáng xem...",
                "Đang hỏi Chiếc Nón Phân loại về gu của bạn...",
                "Đang pha thuốc gợi ý — sắp xong rồi...",
            ],
            "thinking_add_media": [
                "Searching the Restricted Section catalogue...",
                "Consulting the library index for that title...",
                "Casting a quick search spell — almost ready...",
            ],
        },
    },
    "zh": {
        "sarcastic": {
            "thinking_inquiry": [
                "当然，我这就放下一切去查...",
                "显然我闲着没事干...",
                "好吧，我假装这问题很有趣...",
            ],
            "thinking_recommend": [
                "当然，我这就放下一切给你找完美的...",
                "显然我闲着没事干...",
                "好吧，我假装这是个有趣的挑战...",
            ],
            "thinking_add_media": [
                "当然，在库里搜这个...",
                "无尽片单又加一个 — 搜索中...",
                "尽量没热情地在找...",
            ],
        },
        "wizarding": {
            "thinking_inquiry": [
                "查阅图书馆档案...",
                "翻看活点地图上的事实...",
                "念个快速查找咒语...",
            ],
            "thinking_recommend": [
                "正在禁书区找值得看的内容...",
                "正在向分院帽咨询你的口味...",
                "正在调制推荐魔药 — 快好了...",
            ],
            "thinking_add_media": [
                "搜索禁书区目录...",
                "查阅图书馆索引...",
                "查找咒语 — 快好了...",
            ],
        },
    },
}

# Expanded Russian thinking variants (merged at import time).
_RU_THINKING: Dict[str, Dict[str, list[str]]] = {
    "default": {
        "thinking_inquiry": [
            "Сейчас поищу...",
            "Минутку — проверю для тебя...",
            "Ищу ответ...",
        ],
        "thinking_recommend": [
            "Дай-ка подумаю о чём-нибудь хорошем...",
            "Хм, поищу что-то, на что стоит потратить время...",
            "Секунду — подберу что-то особенное...",
            "Сейчас пробегусь по каталогу, чтобы найти удачный вариант...",
            "Минутку — подберу что-то стоящее...",
            "Дай подумать, что бы тебе зашло...",
        ],
        "thinking_add_media": [
            "Ищу этот тайтл в библиотеке...",
            "Сверяюсь с каталогом...",
            "Минутку — ищу совпадения...",
        ],
    },
    "casual": {
        "thinking_inquiry": [
            "Погоди, сейчас гляну...",
            "Дай секунду — поищу...",
            "Ладно, найду ответ...",
        ],
        "thinking_recommend": [
            "Погоди, сейчас накопаю что-нибудь крутое...",
            "Дай секунду — сейчас будет что-то хорошее...",
            "Ладно-ладно, сейчас найду тебе удачный вариант...",
            "Секунду, копаюсь в каталоге — скоро покажу...",
            "Ща гляну, что у нас интересного есть...",
            "Погоди-ка, сейчас вытащу что-нибудь огонь...",
        ],
        "thinking_add_media": [
            "Ща поищу в библиотеке...",
            "Дай секунду, отслежу тайтл...",
            "Ладно, найду в каталоге...",
        ],
    },
    "warm": {
        "thinking_inquiry": [
            "Подберу лучший ответ для тебя...",
            "Поищу внимательно...",
            "Минутку — хочу попасть в точку...",
        ],
        "thinking_recommend": [
            "Подберу что-то, что тебе правда понравится...",
            "Выберу что-нибудь уютное и хорошее для тебя...",
            "Секунду — хочу, чтобы это был отличный выбор...",
            "Сейчас найду что-то тёплое и приятное...",
            "Хочу подобрать тебе по-настоящему хороший вариант...",
            "Минутку — выберу с заботой о твоём настроении...",
        ],
        "thinking_add_media": [
            "Ищу этот тайтл для твоей библиотеки...",
            "Найду подходящее совпадение...",
            "Минутку — ищу для тебя...",
        ],
    },
    "sarcastic": {
        "thinking_inquiry": [
            "Ну конечно, брошу всё и поищу...",
            "Очевидно же, мне было нечем заняться...",
            "Ладно. Сделаю вид, что это увлекательный вопрос...",
        ],
        "thinking_recommend": [
            "Ну конечно, сейчас брошу всё и найду тебе идеальное...",
            "Очень занят, но ладно — поищу что-нибудь...",
            "Хорошо, сделаю вид, что это увлекательная задача...",
            "Секунду — с непередаваемым энтузиазмом листаю каталог...",
            "Какая неожиданность, ещё один запрос на рекомендации...",
            "Сейчас с минимальным воодушевлением что-нибудь подберу...",
        ],
        "thinking_add_media": [
            "Ну конечно, поищу в библиотеке...",
            "Ещё один тайтл для бесконечного списка — ищу...",
            "Ищу с минимальным энтузиазмом...",
        ],
    },
    "wizarding": {
        "thinking_inquiry": [
            "Сверяюсь с архивами библиотеки...",
            "Листаю Карту мародёров фактов...",
            "Произношу быстрое заклинание поиска...",
        ],
        "thinking_recommend": [
            "Заглядываю в Запретный отдел в поисках чего-то стоящего...",
            "Консультируюсь с Сортировочной Шляпой по твоему вкусу...",
            "Варю зелье рекомендаций — почти готово...",
            "Листаю карту мародёров — то есть каталог фильмов...",
            "Жду письмо из Хогвартса... то есть просматриваю каталог...",
            "Произношу заклинание подбора — секунду...",
        ],
        "thinking_add_media": [
            "Ищу в каталоге Запретного отдела...",
            "Сверяюсь с указателем библиотеки...",
            "Произношу заклинание поиска — почти готово...",
        ],
    },
}


def _apply_style_extensions() -> None:
    for lang, new_styles in _STYLE_EXTENSIONS.items():
        overlay = LANG_OVERLAYS.setdefault(lang, {"styles": {}, "shared": {}})
        styles = overlay.setdefault("styles", {})
        styles.update(new_styles)

    ru_styles = LANG_OVERLAYS["ru"]["styles"]
    for style_name, phrases in _RU_THINKING.items():
        ru_styles[style_name] = phrases


_apply_style_extensions()

__all__ = ["LANG_OVERLAYS"]
