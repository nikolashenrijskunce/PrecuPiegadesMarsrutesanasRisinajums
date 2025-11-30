# PrecuPiegadesMarsrutesanasRisinajums
Izstrādātais risinājums priekš preču piegādes maršrutēšanas problēmas studiju kursā "Projektēšanas laboratorija"

# Risinājuma mērķis:
Šis risinājums tika izveidots, lai nodrošinātu IT infrastruktūru piegādes kompānijai. Tas nodrošina dažāda līmeņa lietotāju funkcijas, aktuālo datu uzglabāšanu datubāzē, grafisko lietotāju saskarni un algoritmu, kas veic automatizētu maršrutu izveidi ar algoritmu.

# Lietotāju līmeņi
- Klients (client): Var izveidot profilu, veikt pasūtījumus, apskatīt aktuālos pasūtījumus, var redzēt informāciju par savu profilu.
- Šoferis (driver): Var apskatīt aktuālos maršrutus, var apskatīties informāciju par savu profilu, var apsktīties transportlīdzkļu sarakstu.
- Administrators (admin): Var redzēt visus pasūtījumus, var redzēt visus šoferus un katram šoferim piešķirt automašīnu, var pivienot jaunus šoferus un jaunas automašīnas.

# Algoritms
Algoritms tiek realizēts ar Google OR-Tools, kas nodrošina aprēķinu un Google Routes API, kas nodrošina distnču matricas iegūšanu. Tas tiek realizēts utils/oute_calc.py failā.

Algoritma soļi:
1. Failam padod sarakstu ar adresēm, uz kurām ir jāveic piegādes.
2. Iedoto informāciju pārstrukturizē un padod Google serveriem, kas veic aprēķinu.
3. No Google serveriem saņem atbildi, kur iegūst distanču matricu un to pārveido Python saraksta formātā.
4. Saraksts tiek padots funkcijai, kas ar Google OR rīkiem veic aprēķinu matricai, lai iegūtu strukturizētu sarakstu ar maršrutiem, kas iekļauj vairākus piegādes punktus ar optimālāko punktu sasniegšanas laiku.

Aprēķini tiek veikti izmantojot manhetenas attālumu. Sīkāku informāciju par aprēķina gaitu var meklēt šajā resursā: https://www.geeksforgeeks.org/data-science/manhattan-distance/


