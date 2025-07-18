# tabor2025

něco tam je, můžeš se na to podívat a říct co bych měl udělat jinak

jak to funguje?
Celé je to flask a sqlite
De facto jen operace nad databází
  Databázi v aktuální verzi vždy znovu otevřu, změním a přísutp k ní zavřu... Ale asi věřím, že je to to lepší řešení



TO-DO (věcí o kterých asi vím)
- logging - řešil bych pomocí python logging modulu a vypadá to být vpohodě
- přesné návratové hodnoty - oproti našemu dokumentu v některých funkcích vracím offset ne atuální čas, klidně to změním
- nemožnost použít jeden tag vícekrát - takže do databáze dát čas posledního použití a pak kontrolovat jeslti to bylo včera nebo ne... to půjde prostě nějak přidat, jen se to bude muset změnit všude
- jsem si uvědomil že "category name" vlastně nikde nepoužívám, takže pokud nechceme kategorie jen čísílkové, tak tam přidám join a nějak to upravím
