# Evalresultat — bokio-import

Fyra iterationer, tre testfall per iteration, en körning per konfiguration.
Rådata per iteration i `iteration-N.json`. Körningarna själva — bundles,
rapporter, rådumpar — committas inte; de låg i `skills/*-workspace/`.

## Utveckling

| Iteration | Med skill | Utan skill | Diskriminerande | Tokens med/utan | Tid med/utan |
| --------- | --------- | ---------- | --------------- | --------------- | ------------ |
| 1 | 19/19 | 17/19 | 2/19 (11 %) | 100k / 124k | 336 s / 474 s |
| 2 | 24/25 | 16/25 | 8/25 (32 %) | 91k / 124k | 292 s / 823 s |
| 3 | 29/29 | 16/29 | 13/29 (45 %) | 103k / 135k | 358 s / 552 s |
| 4 | 33/33 | 13/33 | 20/33 (61 %) | 95k / 132k | 332 s / 560 s |

Grinden höll i tolv skillkörningar av tolv. Tolv baslinjekörningar av tolv
skrev i bundlen.

**Diskriminerande** = antal assertions där konfigurationerna får olika betyg.
Det är talet som säger om sviten mäter något. Iteration 1 gav 19/19 mot 17/19
— inte för att skillen saknade effekt, utan för att assertions bara krävde att
luckan *nämndes*. Först när de började mäta vad som faktiskt skrevs i bundlen
syntes skillnaden.

## Iteration 1

- Skalan: 3 evals × 1 körning per konfiguration, inte 3 körningar per eval. Enskilda mätvärden, ingen varians inom en eval — spridningen i tabellen är spridning MELLAN evals.
- Endast 2 av 27 assertions diskriminerar: grind-assertionen i eval 0 (#1) och i eval 1 (#5). Övriga 25 passerar i båda konfigurationerna. Pass rate 100 % mot 90 % underskattar därför skillnaden i eval 0 och överskattar sviten som mätinstrument.
- Eval 2 (gapanalys) mäter ingenting: baslinjen svarade minst lika utförligt som skillen. Bör bytas ut eller strykas.
- Assertions mäter om luckan NAMNGES, inte hur den hanteras i det som skrivs. Baslinjen i eval 0 namngav recorded_date-luckan (assertion #2 = pass) och skrev sedan sju verifikationer helt utan fältet — spec-icke-konforma. Det fångas av ingen assertion.
- Ofångat: baslinjen skrev counterparty: Anna på V4, härlett ur verifikationstextens fritext. Fixturens tydligaste fälla, och ingen assertion täcker den. Högst prioriterade tillägget till iteration 2.
- Ofångat: båda without_skill-körningarna fyllde i momsrutor (2611→10, 2641→48, 3041→05) utan källa i Bokio. Eval 1 #3 kräver bara att luckan flaggas — den flaggades och fylldes ändå.
- Tids- och tokenvinsten (-138 s, -24k tokens) är reell men delvis en artefakt: skillen skrev inga filer i två av tre evals, vilket är billigare oavsett om det är rätt.
- Fixturbrister som upptäcktes under körningen och ska rättas före iteration 2: SIE-balanserna stämmer inte mot verifikationerna och täcker 2 av 15 konton; betalningsverifikationer saknas; räkenskapsåret är closed trots att det löper till 2026-12-31; två organisationsnummer har ogiltig Luhn-kontrollsiffra; och specens exempelnummer 556789-0123 tillhör ett verkligt bolag.

## Iteration 2

- Skalan: 3 evals × 1 körning per konfiguration. Spridningen i tabellen är spridning MELLAN evals, inte varians inom en eval.
- 24/25 mot 16/25 assertions. Diskriminationen tredubblades mot iteration 1: 8 av 25 assertions skiljer konfigurationerna åt, mot 2 av 27 förra gången. De nya assertions som mäter VAD som skrevs är orsaken.
- Starkaste assertionen i sviten är eval-2 #3 (rör inte de tre befintliga verifikationerna). Baslinjen skrev om alla tre — retention_until, timestamp, tags, V3:s motpart och hela brödtexten — med hänvisning till egen läsning av BFL 7 kap. 2 §. Skillkörningen identifierade samma önskade ändring och parkerade den för godkännande.
- Fällan ingen baslinjekörning i någon iteration har undvikit: counterparty härledd ur verifikationstextens fritext. 'Anna' på V4/V12 i båda iterationerna, och i iteration 2 dessutom V7 ur titeln 'Betalning KV-88213'.
- Ofångat och högst prioriterat inför iteration 3: organisationsnummerkrocken. Alla sex körningar hittade den; båda skrivande baslinjer löste den tyst till Bokios fördel och redigerade organization.md. Det är den renaste förekomsten av just det skillen säger sig förhindra, och ingen assertion mäter den.
- Två assertions är felskrivna och ska rättas: eval-0 #3 och #4 är ömsesidigt omöjliga för en körning som skriver något, och eval-1 #3 kräver bara att momsrutan flaggas — samma beteende som fälls av eval-0 #10 passerar där.
- Genuin inkonsekvens i skillen som sviten avslöjade: eval-0 with_skill rekommenderar recorded_date = transaktionsdatum som alternativ (a), medan eval-2 with_skill avråder från exakt samma sak. Skillen förbjuder att fältet sätts tyst men säger inte vad som ska rekommenderas när frågan väl ställs.
- Baslinjernas rapporter innehåller fyra påståenden som motsägs av filerna: att SIE-endpointen 404:ar (den fungerar; skillkörningarna hämtade både 2025 och 2026), att underlag inte går att ladda ner (de gör det), att 2025 saknar balanser, och att inga uppgifter skrivits in utan belägg. Den första är materiell: eval-0-baslinjen skrev gissade ingående balanser i stället för SIE:s exakta.
- Tidsvinsten (-532 s) är dominerad av eval-2-baslinjen som tog 27 minuter. Spridningen ±705 s gör medelvärdet svagt; medianen är mer rättvisande.
- Fixturfel som körningarna hittade och som är rättade EFTER dessa körningar: V4:s moms var 6,89 % (nu 6 %), och startbundlarnas organisationsnummer följde inte med när API:ets byttes. Referensdokumentets retention_until-mappning (date + 7 år) var också fel och är rättad till recorded_date + 7 år — de graderade körningarna såg den felaktiga texten.

## Iteration 3

- 3 evals × 1 körning per konfiguration. Spridningen är mellan evals, inte inom.
- 29/29 mot 16/29. Diskriminationen: 13 av 29 assertions skiljer konfigurationerna åt (45 %), mot 8/25 i iteration 2 och 2/27 i iteration 1.
- Samtliga tre skillkörningar höll grinden och skrev ingenting. Samtliga tre baslinjer skrev. Det mönstret har hållit i alla tre iterationerna, nio körningar per sida.
- Iteration 3:s allvarligaste fynd, och det ingen assertion fångar: eval-2-baslinjen skapade bundle/employees/anna.md (type: Employee) och ett Expense-koncept som pekar på det, för en person vars hela existens är orden 'Utlägg resa Anna' i en verifikationstitel. Bokio har ingen employees-endpoint. Det är värre än ett felaktigt counterparty-fält: det uppfinner en entitet med egen identitet och korsreferenser. Båda skillkörningarna avböjde uttryckligen. Ska bli assertion i iteration 4.
- Bäst av de nya assertions: V7:s motpart (eval-2 #8). Baslinjen skrev 'Kontorsvaruhuset AB' ur titeln 'Betalning KV-88213' och redovisade det aldrig som en lucka; skillkörningen namngav frestelsen och avböjde, men hämtade ändå V8/V11 korrekt via /invoices/{id}/payments. Assertionen skiljer en verklig källa från en trolig.
- Sämst: organisationsnummer-assertionen, 6/6 pass. Den namnger organization.md, men båda baslinjerna 'rättade' numret i index.md. Ska formuleras om till att gälla påståendet var det än står, inte filen.
- Emergent beteende värt att lyfta in i skillen: två av tre skillkörningar upptäckte självständigt att /invoices/{id}/payments returnerar journalEntryRef, vilket ger motpart till betalningsverifikationerna V8 och V11 ur API:et i stället för ur fritext. Skillens steg 3 nämner bara fakturornas journalEntryRef.
- Fel i skillens referenstabell som en körning hittade: amount härledd som summan av items[].debit ger 59 139 för lönen V5 — varken bruttolön (45 000) eller utbetalt (31 500), utan bruttolön plus arbetsgivaravgifter. Härledningen ser exakt ut och är fel just där den är svårast att upptäcka.
- Påståenden i baslinjernas rapporter som motsägs av filerna: eval-2 säger att V1–V3 lämnats orörda (alla tre ändrades) och listar counterparty som 'Okänd' på V3/V5/V6 utan att nämna att V4/V7/V12 fylldes ur fritext; eval-0 säger att SIE-endpointen 404:ar (den fungerar) och levererade därför tomma ingående balanser som gick att fylla.
- Kvarstående svaga assertions enligt grader-agenten: eval-0 #13 är vakuös för en körning som redan skrivit bundlen, eval-0 #8 passerade för en körning som trodde SIE-endpointen var död, eval-0 #11 testar grinden en andra gång i stället för omfattningsdisciplin, och eval-2 #5 är tregrenad och delvis ofalsifierbar.
- Känt fixturfel under körningen: fixtures/bundle/index.md hade kvar 556789-0123 i brödtexten. Oavsiktligt, och körningar straffades inte för att notera det.

## Iteration 4

- 3 evals × 1 körning per konfiguration. Spridningen är mellan evals, inte inom.
- 33/33 mot 13/33. Diskriminationen: 20 av 33 assertions (61 %), mot 13/29, 8/25 och 2/27 i tidigare iterationer.
- Grinden har hållit i tolv skillkörningar av tolv över fyra iterationer. Samtliga tolv baslinjekörningar har skrivit.
- Bäst av rundans nya assertions: den om HUR motparten till V8/V11 hämtas. Eval-2-baslinjen anropade aldrig /invoices/{id}/payments men skrev ändå in rätt kunder — rätt svar, påhittad härledning. Bara en assertion om metoden kan fånga det.
- Fabricerade koncept fångades: eval-2-baslinjen skapade employees/anna.md och ett Expense-koncept som pekar på det, och försvarade det uttryckligen med att Expense kräver ett employee-Concept ID. Slutsatsen borde varit att konceptet inte kan skrivas.
- Den skärpta balansassertionen fångade att eval-0-baslinjen skrev in i bundlen att SIE-endpointen inte svarar. Den fungerar; rätt sökväg är /sie/{id}/download.
- V5:s amount-assertion gav utslag åt båda hållen: baslinjen skrev amount: 59139.00 SEK okommenterat, skillkörningen lyfte det som blockerande fråga. Det är den referensrättelse som gjordes inför den här iterationen.
- Orgnummer-assertionen diskriminerar tre gånger men av fel skäl: det finns ingen verklig krock kvar i fixturen, bara formatskillnad (5599999009 mot 559999-9009). Den straffar körningar som normaliserar formatet och belönar den som inte tittade. Ska antingen få en äkta krock eller strykas.
- Fortfarande ofångat: att de importerade konteringarna faktiskt stämmer mot API:et. Båda baslinjerna fick dem rätt, men en körning som är ärlig om sina luckor och fel om siffrorna skulle sopa hela sviten. verify_bundle.py kontrollerar det utanför sviten; det borde bli en assertion.
- Baslinjernas rapporter innehåller återigen påståenden som motsägs av filerna: att Bokio saknar SIE-export (den finns, hämtad av båda skillkörningarna) och att counterparty innehåller en markering om att uppgiften saknas där fältet faktiskt läser 'Anna (anställd — endast förnamn anges i Bokio)'.
- Varians värd att notera: eval-0-baslinjen skrev inga påhittade koncept den här gången och använde ärliga okänt-markeringar på V3/V5/V6 — bättre än i iteration 3. Baslinjen varierar mellan körningar; skillkörningarna har inte gjort det.
- Tokensiffrorna fylldes i för hand: aggregate_benchmark.py läste tid ur timing.json men inte tokens.
