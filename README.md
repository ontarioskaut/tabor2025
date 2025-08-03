# tabor2025


## Jak to funguje?  
Celé je to flask a sqlite  
De facto jen operace nad databází.
  
### Poznámky k implementaci
- celé to je nezabezpečené a náchylné k injekcím
- když má více lidí stejný akronym, tak se zobrazí jen poslední, protože to ukládám do množiny
- boolean je jen Integer, kdekoli jdou používat hodnoty False a True jako 0 a 1, ale nepoužívám je
- Datetime se automaticky vybralo, jak se bude ukládat je to TEXT v ISO formátu. K hodnotám se dá přistupovat i pomocí sqlite, ale já tam používám python datetime
- coin tag může být zároveň user tag, vadí nám to?
- coin se initializuje pomocí set_coinval nebo activate_coin, u druhého se nastaví "na nulu"
- možnost add_user a add_coin by se asi primárně neměli používat, ideální je to nejdřív iniciovat přes init_user, nebo operaci s coinem
- https://sqlite.org/autoinc.html tvrdí, že se primary key dá jako "o jedna vyšší" automaticky a nemusím to dělat já... ale asi to tak už nechám. AUTOINCREMENT je prý zbytečný a jen zajišťuje, aby ID nemohlo být použito už nikdy znovu, ani po vymazání nějakého prvku, což podle mě nechceme, navíc sami tvrdí že to je extra CPU
    - integer primary key je automaticky ROWID a dá se tak k němu přistupovat
- na mnoha místech by bylo pěknější si volat ty funkce navzájem, třeba z bulk_time_add volat prostě jen add_time na jednotlivé usery, tam by se ale databáze otevírala sem tam což nechci, a udělat dodatečnou funkci by nebyl problém, ale asi mi to přijde zbytečné
- show_times_02 si každých WEB_REFRESH_INTERVAL sekund (konfigurovatelné v `config.py`) stahuje aktuální data, timery běží jen na frontendu


## TO-DO (věcí o kterých asi vím)
- Bude potřeba někde uchovávat a editovat annoncements, ale jelikož budou obsahovat i grafické prvky, bude to Hruška řešit nezávisle. S tím se pojí i sestém pro displeje, který bude renderovat obrazovky přímo na serveru kvůli škálovatelnosti.
    - v tu chvíli si to chce pamatovat nastavení a annoucments i mimo kód, takže mít dvě další tabulky v databázi...
- můžeme přidat "eval" funkci na stringy
- aplikace do mobilu pro aktivaci - existuje https://developer.mozilla.org/en-US/docs/Web/API/Web_NFC_API, takže bude stačit udělat PWA


## Done To-Do pro kontrolu
- displayed - změnit number input na checkbox
- date select boxy pro iteraktivnější výběr času
    - jsem to změnil, nejjednodušší možnou cestou, ale prohlížec neumožňuje výběr na sekundy úplně přesně a dělá v tom lehce bordel. Dá se použít flatpickr, ale toto je za mě dostatečné
- nemožnost použít jeden tag vícekrát - takže do databáze dát čas posledního použití a pak kontrolovat jeslti to bylo včera nebo ne... to půjde prostě nějak přidat, jen se to bude muset změnit všude
    - v databázi je uložené i poslední použití skrz add_coinval, i bool "is_active". Tag se dá aktivovat pomocí "activate_coin" nebo skrz admin stránku, asi snad funkční řekl bych
- logování transakcí - tabulka user, amount, transaction_details_text. Viditelné po kliknutí na uživatele.
    - bude tam databáze
    - líbí se mi přístup přes triggers, což by mělo být rychlejší a lepší vůči změnám, nyní mám nastavený trigger na "update", ale vlastně nevím, jestli tím nepřicházíme o nějakou informaci, třeba se takto nedozvíme jestli to bylo z coinu nebo od člověka a nemůžeme s tím pracovat, takže je to možná nepoužitelné
    - log se zatím dá zobrazit v test_log
    - a nevím co všechno vlastně chceme logovat, pokud jen změnu offsetů, tak to není takový problém doplnit jako kompletní přehled všech operací
    - kdyžtak je k to na /show_logs a je tam filtr na uživatele
- přesné návratové hodnoty - oproti našemu dokumentu v některých funkcích vracím offset ne atuální čas, klidně to změním - jo, to by bylo fajn
    - v sekundách
- kategorie - speciální relace user id - category id, v tabulce select boxy, každý uživatel může mít více kategorií
    - ehhhhhhhhhhhhhhhhhhhhhhhhhh
    - funguje to
    - a asi i dobře a asi i lépe než jsem původně myslel že to udělám
    - v /admin stránce je na to odkaz, někdy třebas doplnim tu "dokumentaci"
    - ale u coinů jsem nechal jen jednu kategorii
- přidat více režimů pro "Time offset to add" - samotný offset, násobení (procenta), nastavit absolutně
    podíváme se na poslední znak a podle toho upravíme
    - jo, mění to podle posledního znaku
    - ve speciálním api a v bulk polích


## API features
- [API Documentation](docs/api_docs.md)

