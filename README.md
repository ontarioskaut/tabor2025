# tabor2025


## jak to funguje?  
Celé je to flask a sqlite  
De facto jen operace nad databází.
  
### poznámky k implementaci
- když má více lidí stejný akronym, tak se zobrazí jen poslední, protože to ukládám do množiny
- boolean je jen Integer, kdekoli jdou používat hodnoty False a True jako 0 a 1, ale nepoužívám je
- Datetime se automaticky vybralo, jak se bude ukládat je to TEXT v ISO formátu. K hodnotám se dá přistupovat i pomocí sqlite, ale já tam používám python datetime
- coin tag může být zároveň user tag, vadí nám to?
- coin se initializuje pomocí set_coinval nebo activate_coin, u druhého se nastaví "na nulu"
- možnost add_user a add_coin by se asi primárně neměli používat, ideální je to nejdřív iniciovat přes init_user, nebo operaci s coinem


## TO-DO (věcí o kterých asi vím)
- logging - řešil bych pomocí python logging modulu a vypadá to být vpohodě
- přesné návratové hodnoty - oproti našemu dokumentu v některých funkcích vracím offset ne atuální čas, klidně to změním - jo, to by bylo fajn
    - fajn , upravím, jen v **jakých jednotkách**? sekundy? string? co ti vyhovuje nejvíc?
- jsem si uvědomil že "category name" vlastně nikde nepoužívám, takže pokud nechceme kategorie jen čísílkové, tak tam přidám join a nějak to upravím - na tomto budu teď pracovat - budou tam select boxy u userů/coinů
- trochu jsem pohýbal se strukturou display_api - doplněny announcements. Ty by se hodilo umět editovat v admin gui
- přidat více režimů pro "Time offset to add" - samotný offset, násobení (procenta), nastavit absolutně
- tlačítko pro synchronizaci času s prohlížečem (hlavní počítač nebude mít přístup k NTP a ani nebude mít RTC)
- logování transakcí - tabulka user, amount, transaction_details_text. Viditelné po kliknutí na uživatele.
- chceme kategorie nechat jako jen jedno číslo, nebo nějak zapracovat, aby mohl být uživatel ve vícero kategoriích?
- tlačítko pro vynulování coinů (případně řešitelné přes "krát 0", pokud by byly další režimy)

## Done To-Do pro kontrolu
- displayed - změnit number input na checkbox
- date select boxy pro iteraktivnější výběr času
    - jsem to změnil, nejjednodušší možnou cestou, ale prohlížec neumožňuje výběr na sekundy a dělá v tom lehce bordel. Dá se použít flatpickr, ale toto je za mě dostatečné
- nemožnost použít jeden tag vícekrát - takže do databáze dát čas posledního použití a pak kontrolovat jeslti to bylo včera nebo ne... to půjde prostě nějak přidat, jen se to bude muset změnit všude
    - v databázi je uložené i poslední použití skrz add_coinval, i bool "is_active". Tag se dá aktivovat pomocí "activate_coin" nebo skrz admin stránku, asi snad funkční řekl bych


## API features:
### API for end nodes
- get identification (get_identification):
    - in: user_tag_id
    - out: {name, user_time}
- odečet času (substract_time):
    - in: {time_to_substract, user_tag_id}
    - out: {status, user_time}
- přičtení času z coinů (add_coinval):
    - in: {coin_tag_id, user_tag_id}
    - out: {status, user_time, coin_value}
- přičtení času (add_time):
    - in: {time to add, user_tag_id}
    - out: {status, user_time}
- tracking (not implemented):
    - in: {tracker_id, lon, lat}
    - out: status
- set coin value (set_coinval):
    - in: {coin_tag_id, coin_value, category}
    - out: status
- activate coin
    -in: {coin_tag_id}
    -out: status
- init user tag: (check if user exist, otherwise, create new with user_tag_id and incremental value as name)
    - in: user_tag_id
    - out: status



### Display API
- get_time (current)
    - in: nothing
    - out: {user_acronyme: user_time} (filter: is_displayed)
    
- get_time (wanted)
	- in: nothing
	- out:
```json
{
  "renew_interval": 5000,
  "screen_delay": 4000,
  "num_times": 10,
  "times": [
    "AB": 7203,
    "BC": 8203,
    "CD": 3253,
    "DE": 7867,
    "EF": 4203,
    "FG": 7203,
    "GH": 5753,
    "HI": 7867,
    "IJ": 7203,
    "JK": 6903,
    "KL": 3253,
    "LM": 9847,
  ],
  "announcements": [
    ["First line 1", "Second line 1", 2000], //(2000 = duration)
    ["First line 2", "Second line 3", 3000],
  ]
}
```

### Admin dashboard API
- admin dashbord (/admin)
    - in: nothing
    - out: fillet html template
- user admin (/admin/users)
    - in: nothing
    - out: filled html template:
        - user list (name, acro, time_offset, user_tag_id, time start, is_displayied) - possible to update all of it
        - add_user (řádek tabulky s polem)
        - bulk add time - add same time to checked users
        - delete user
    
    - 
- coin admin:
    - in: nothing
    - out: filled html template:
        - tag: value list + edit + categories (bulk select => set bulk)
        - update
        - add
        - delete
- users category admin
    - in: nothing
    - out: filled html template:
        - name, number

        - add
        - update
        - delete
        - option to add time to all users in specified categories

- set_user_field:
    - in: {user_id, field_name, new_value}
    - out: status

- bulk_add_user_time:
    - in: {user_ids: [user_id, ...], time_offset}
    - out: status

- bulk_set_coin_field:
    - in: {coin_ids: [coin_id, ...], field_name, new_value}
    - out: status

