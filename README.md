# PrecuPiegadesMarsrutesanasRisinajums
Izstrādātais risinājums priekš preču piegādes maršrutēšanas problēmas studiju kursā "Projektēšanas laboratorija"

# Risinājuma mērķis:
Šis risinājums tika izveidots, lai nodrošinātu IT infrastruktūru piegādes kompānijai. Tas nodrošina dažāda līmeņa lietotāju funkcijas, aktuālo datu uzglabāšanu datubāzē, grafisko lietotāju saskarni un algoritmu, kas veic automatizētu maršrutu izveidi ar algoritmu.
### Izmantotās tehnoloģijas
- Programmēšanas valoda: Python
- Datu bāze: SQLite
- Frontend: HTML, CSS, JavaScript
- Maršrutēšana: Google Maps API
- Datu apstrāde: Flask

### Sistēmas galvenās sastāvdaļas
- Lietotāja saskarne
- Maršrutēšanas aprēķināšana
- Datu bāze

Sistēma ir veidota kā tīmekļa lietotne. Lietotāja saskarne nodrošina datu ievadi un vizualizāciju. Servera puse apstrādā datu glabāšanu un maršrutēšanas aprēķinus. Maršrutēšanas modulis izmanto ārējos karšu pakalpojumus ģeokodēšanai un maršrutu aprēķināšanai.
### Sistēmas ierobežojumi
Sistēma neņem vērā satiksmes sastrēgumus reāllaikā, vadītāju darba laika ierobežojumus, transportlīdzekļu kravnesību.

# Lietotāju līmeņi
- Klients (client): Var izveidot profilu, veikt pasūtījumus, apskatīt aktuālos pasūtījumus, var redzēt informāciju par savu profilu.
- Šoferis (driver): Var apskatīt aktuālos pasūtījumus, informāciju par savu profilu un transportlīdzekli, maršrutus konkrētiem pasūtījumiem.
- Administrators (admin): Var redzēt visus pasūtījumus, visus maršrutus ar izvēlētajiem šoferiem un aprēķinātajiem piegādes laikiem. Var redzēt visus transportlīdzekļus un visus šoferus.
#### Drošibas un piekļuves kontrole
1. Tiek izmantota autentifikācija ar paroli 
2. Izveidotas dažādes piekļuves tiesības atkarībā no lomas
3. Klienti redzi tikai savus pasūtījumus, vadītāji redz tikai savus maršrutus.
# Maršrutēšans loģika
Sistēma automātiski sadala piegādes starp vadītājiem un izveido apmeklējamo adrešu secību katram vadītājam. Maršrutēšana notiek secīgi, izmantojot ģeogrāfisko attālumu aprēķināšanu un vienkāršotus optimizācijas algoritmus.
1. Visas piegādes adreses tiek pārvērstas ģeogrāfiskajās koordinātēs izmantojot **Geocoding mehānismu**
2. Tiek izmantots **Balanced K-means klasterizācijas algoritms**, lai sadalītu pasūtījumus starp vadītājiem. (tas nodrošina līdzsvarotu pasūtījumu sadali)
    - K-means klasterizācijai tiek iestatīts fiksēts klasteru skaits (vadītāju skaits)
    - Tiek izmantots kapacitātes ierobežojums, lai klasteri būtu līdzsvaroti
    - klasteru centri tiek pārrēķināti vairākas reizes
3. Tiek aprēķināti braukšanas laiki starp visiem punktiem izmantojot **Distance Matrix** 
4. Ar **Nearest Neighbour algoritmu** nosaka piegādes punktu apmeklēšanas secību. Maršruts sākas noliktavā un katrā solī tiek izvēlēts tuvākais vēl neapmeklētais punkts. Turpinās līdz ir apmeklēti visi punkti. (tas ir vienkāršs un ātrs)
5. Maršruti tiek attēloti kartē ar **Directions** mehānismu. Un tiek aprēķināti paredzētie ierašanās laiki katrā pieturā.

# Datu struktūra
### Klienti (clients)
|Lauks|Apraksts|
|----|----|
|client_id|klienta identifikators|
|name|epasts|
|address|adrese|
|phone|tālrunis|
|password|parole|
---
*viens klients var būt saistīts ar vairākiem pasūtījumiem*
### Produkti (products)
|Lauks|Apraksts|
|----|----|
|product_id|produkta identifikators|
|name|nosaukums|
|weight|svars|
|price|cena|
---
*produkti tiek piesaistīti pasūtījumiem caur pasūtījuma vienībām*
### Pasūtījumi (orders)
|Lauks|Apraksts|
|----|----|
|order_id|pasūtījuma identifikators|
|client_id|klienta identifikators|
|order_date|pasūtījuma izveidošanas datums|
|pickup_address|saņemšanas adrese|
|delivery_address|piegādes adrese|
|estimated_delivery_time|plānotais piegādes laiks|
|driver_name|piešķirtā vadītāja vārds|
|price|kopējā pasūtījuma cena|
---
*pasūtījums ir saistīts ar vienu klientu un vairākām pasūtījuma vienībām*

### Pasūtījuma vienības (order_items)
|Lauks|Apraksts|
|----|----|
|order_item_id|pasūtījuma vienības identifikators|
|order_id|pasūtījuma identifikators|
|product_id|produkta identifikators|
|quantity|daudzums|
---
*saistība starp produktiem un pasūtījumiem*
### Transportlīdzekļi (vehicles)
|Lauks|Apraksts|
|----|----|
|vehicle_id|transportlīdzekļa identifikators|
|model|transportlīdzekļa modelis|
|milage|transportlīdzekļa nobrakumus|
|fuel_consumption|degvielas patēriņš|
|technical_inspection_expiry|tehniskās apskates termiņš|
---
*transportlīdzeklis var būt piesaistīts vadītājam un pasūtījumam*

### Vadītāji (drivers)
|Lauks|Apraksts|
|----|----|
|driver_id|vadītāja identifikators|
|name|vārds|
|email|epasta adrese|
|phone|tālrunis|
|vehicle_id|piešķirtais transportlīdzeklis|
|hours_worked|nostrādātās stundas|
---
*vadītājs ir piesaistīts transportlīdzeklim un vairākiem pasūtījumiem*
# Sistēmas uzlabojumu iespejas
- Laika logu ievērošana piegādēm
- Transportlīdzekļu kapacitātes ierobežojumi
- Reāllaika GPS izsekošana

# Atsauces

- Koda ģenerēšana notika ar ChatGPT palīdzību
- HTML lapu veidošanai tika izmantots Figma + ChatGPT
- OpenAI. (2024). ChatGPT (GPT-4). https://chat.openai.com
- https://developers.google.com/maps/documentation/javascript/legacy/directions

