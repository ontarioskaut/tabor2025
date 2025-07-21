# tabor2025

něco tam je, můžeš se na to podívat a říct co bych měl udělat jinak

jak to funguje?
Celé je to flask a sqlite
De facto jen operace nad databází.
Tu v aktuální verzi vždy znovu otevřu, změním a přísutp k ní zavřu. Což by u mnoha požadavků najednou mohlo dělat problémy. ale zatím mi to přišlo jako nejjednodušší řešení. - jo, to stačí. víc bych to neřešil



TO-DO (věcí o kterých asi vím)
- logging - řešil bych pomocí python logging modulu a vypadá to být vpohodě
- přesné návratové hodnoty - oproti našemu dokumentu v některých funkcích vracím offset ne atuální čas, klidně to změním - jo, to by bylo fajn
- nemožnost použít jeden tag vícekrát - takže do databáze dát čas posledního použití a pak kontrolovat jeslti to bylo včera nebo ne... to půjde prostě nějak přidat, jen se to bude muset změnit všude
- jsem si uvědomil že "category name" vlastně nikde nepoužívám, takže pokud nechceme kategorie jen čísílkové, tak tam přidám join a nějak to upravím - na tomto budu teď pracovat - budou tam select boxy u userů/coinů
- trochu jsem pohýbal se strukturou display_api - doplněny announcements. Ty by se hodilo umět editovat v admin gui
- přidat více režimů pro "Time offset to add" - samotný offset, násobení (procenta), nastavit absolutně
- date select boxy pro iteraktivnější výběr času
- tlačítko pro synchronizaci času s prohlížečem (hlavní počítač nebude mít přístup k NTP a ani nebude mít RTC)
- displayed - změnit number input na checkbox
- logování transakcí - tabulka user, amount, transaction_details_text. Viditelné po kliknutí na uživatele.



## API features:
### API for end nodes
- get identification:
    - in: user_tag_id
    - out: {name, user_time}
- odečet času:
    - in: {time_to_substract, user_tag_id}
    - out: {status, user_time}
- přičtení času z coinů:
    - in: {coin_tag_id, user_tag_id}
    - out: {status, user_time, coin_value}
- tracking:
    - in: {tracker_id, lon, lat}
    - out: status
- set coin value:
    - in: {coin_tag_id, coin_value, category}
    - out: status
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
- user_admin
    - in: nothing
    - out: filled html template:
        - user list (name (edit), acro (edit), time (edit), user_tag_id (edit))
        - edit -> modal box -> request -> done/failed
        - add_user (řádek tabulky s polem)
- tag_admin:
    - in: nothing
    - out: filled html template:
        - tag: value list + edit + cathegories (bulk select => set bulk)

- set_user_field:
    - in: {user_id, field_name, new_value}
    - out: status

- bulk_add_user_time:
    - in: {user_ids: [user_id, ...], time_offset}
    - out: status

- bulk_set_coin_field:
    - in: {coin_ids: [coin_id, ...], field_name, new_value}
    - out: status

