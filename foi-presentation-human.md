# Förberedelseuppgift FOI - Rapid prototyping av analysverktyg

## Scenario och uppdrag

I scenariot arbetar underrättelseanalytiker med stora textmängder: nyhetsflöden, forum, sociala medier och interna rapporter. Arbetet görs i dag till stor del manuellt. Relevanta utdrag kopieras mellan olika verktyg, ofta hela vägen till Excel. När inflödet ökar blir arbetssättet svårt att skala, och det ökar risken att missa samband mellan händelser, aktörer och platser.

Målet med prototypen är att korta tiden från råtext till användbar analys. Analytikern ska kunna mata in material via text, länk eller dokumentuppladdning och få tillbaka en första strukturerad bild: sammanfattning, centrala datapunkter och möjlighet att söka semantiskt i materialet.

Det här är inte en produktionssättning av hela förmågan. Det är en fungerande prototyp som visar att arbetsflödet håller, att tekniken är validerad och att användarfeedback går att omsätta till förbättringar sprint för sprint.

## Team och ansvar

Vi är tre roller:

- Jag driver prototypen och bygger helheten: backend, frontend, integrationslager, CI och driftbar utvecklingsmiljö.
- Projektledaren ansvarar för användarbehov, prioritering och tillgång till domänpersoner.
- Forskningsingenjören ansvarar för modellkvalitet, utvärdering av modellvarianter och förbättringar över tid.

En praktisk princip i samarbetet är att modellteamet ska kunna utveckla och byta modell utan att resten av systemet behöver skrivas om. Därför lägger vi tidigt ett tydligt integrationskontrakt mellan applikationen och modellen.

## Arbetssätt från dag ett

Jag börjar med att skapa en körbar grundmiljö så att vi kan testa idéer snabbt och återupprepa resultat.

- Kod och promptar versionshanteras i Git på intern GitLab.
- CI kör tester på varje push och bygger deploybara container-images vid merge.
- Tjänsterna körs via Docker Compose för enkel uppstart, stopp och felsökning.
- Arkitekturen planeras för on-prem, eftersom klassad information inte ska tvinga oss till publika molnberoenden.

Parallellt arbetar vi med kravbilden. Projektledaren för dialog med analytiker om vilka frågor de faktiskt behöver få svar på. Jag tar fram en teknisk testharness mot modellen för att verifiera fyra saker tidigt: anropsmönster, svarstid, kontextgränser och felbeteenden.

Det här ger underlag till ett realistiskt MVP-beslut redan första veckan: vad vi visar i första demon och vad som medvetet lämnas till senare sprint.

## Säkerhet och dataklassning tidigt, inte sist

I den här typen av uppdrag styr dataklassning arkitekturen. Därför lyfter vi säkerhet direkt i början istället för att behandla den som ett separat slutsteg.

Praktiskt innebär det att:

- miljöer separeras efter klassningsnivå,
- trafik ut från systemet är stängd som standard,
- paket och images hämtas från interna kontrollerade register,
- modellanrop, feedback och kritiska steg loggas för spårbarhet.

Vi tar också en tidig riskworkshop med fokus på språk och domän: klarar modellen svenska i kombination med militärt fackspråk tillräckligt bra för att ge värde? Om svaret är nej behöver modellteamet en plan B utan att applikationslagret fastnar.

## Vecka 2-3: första fungerande vertikal

När grund och riskbild är satt bygger jag en komplett, tunn vertikal genom systemet. Fokus är funktion framför perfektion.

### Backend och flöde

Backend byggs i ASP.NET Core med ett tydligt flöde från inmatning till resultat:

1. Inmatning av text, länk eller dokument.
2. Orkestrering av analyssteg.
3. Tool-calls för sammanfattning, extraktion och indexering.
4. Persistens och sökbarhet.

Modellen exponeras via ett stabilt gränssnitt, så att vi kan byta modellvariant med begränsad påverkan på övriga tjänster.

### Datalager i två nivåer

Vi använder två datalager med olika ansvar:

- Relationsdatabas för dokumentmetadata, feedback, körhistorik och administrativ data.
- Vektorindex för semantisk sökning och återhämtning av relevant kontext.

Kombinationen gör att vi både kan hantera klassisk applikationsdata och samtidigt söka på betydelse, inte bara ordmatchning.

### Frontend för snabb användarvalidering

Frontend byggs med React och TypeScript i en enkel form som stödjer arbetsflödet utan att gömma information i avancerad UI.

I första versionen ska användaren kunna:

- mata in text eller ladda upp dokument,
- få en sammanfattning,
- se extraherad data,
- ge enkel feedback på kvalitet.

Listor och tabeller räcker initialt. Visualiseringar som tidslinje eller graf läggs på efter att användarna bekräftat behovet.

### Första demo

I slutet av vecka tre visar vi en end-to-end-demo på verkligt material. Målet är inte hög precision på allt, utan att bevisa arbetsflödet och få konkret återkoppling från användare.

## Vecka 4-6: iteration med användare och mätbar kvalitet

Här går projektet från teknikdemo till kontrollerad förbättring.

### Feedbackloop

Vi fångar användarfeedback strukturerat i gränssnittet, till exempel tumme upp eller ner med kommentar. Det ger snabb signal om var modellen hjälper och var den brister.

### Evals som del av CI

En central del är att införa evals tidigt. Jag ser det som enhetstester, men för AI-output.

- Vi bygger ett dataset med representativa testfall.
- Vi definierar vad ett acceptabelt svar ska innehålla.
- Testsviten körs automatiskt i CI vid ändringar i promptar, modellkonfiguration eller kod.

Vissa kontroller kan vara regelbaserade. Andra kräver kvalitativ bedömning, där en separat modell används som domare. Verktyg som Promptfoo, Inspect eller Langfuse kan användas beroende på miljökrav och mognad.

Poängen är enkel: vi ska kunna upptäcka regression innan användaren gör det.

### Begränsad användartillgång

Analytiker är inte alltid tillgängliga varje dag. Därför kombinerar vi flera arbetssätt:

- automatiska tester i pipeline,
- syntetisk testdata för återupprepbara scenarier,
- projektledaren som proxy mellan användarsessioner,
- riktade observationstillfällen när analytiker kan delta.

Det här håller tempot uppe utan att tappa användarförankring.

### Modellbyte utan omtag

När modellteamet vill testa en ny variant ska bytet ske via konfiguration och valideras av evals-sviten. Målet är låg friktion, men med kontrollerad kvalitet.

## Vecka 7-8: paketering och leveransbar prototyp

Sista fasen handlar om driftsäkerhet, spårbarhet och tydlig demo.

### Driftbar startupplevelse

En ny miljö ska kunna startas med ett fåtal kommandon. Alla centrala tjänster ska fångas i samma compose-upplägg, med tydliga loggar och hälsokontroller.

### On-prem-kompatibel AI-stack

Vi använder en stack som fungerar i begränsad miljö:

- lokal modellkörning,
- self-hosted observability,
- interna integrationer bakom brandvägg.

Observability är avgörande. Vi behöver se svarstider, felmönster, kostnadsdrivare och kvalitetsutveckling över tid, annars blir systemet en black box.

### AI-stöd i utvecklingsarbetet

I utvecklingen använder vi AI-verktyg för att öka hastigheten i låg- till mellanriskmoment, till exempel boilerplate, testutkast och dokumentation. Arkitekturbeslut dokumenteras löpande i ADR-format för att bevara beslutshistorik.

### Slutdemo

Slutdemon speglar ett realistiskt arbetspass:

1. Batchinläsning av dokument.
2. Sammanfattning och extraktion.
3. Semantisk sökning på frågeställning.
4. Enkel visualisering och filtrering.
5. Feedback på kvalitet.
6. Export av resultat.

Parallellt visar vi systemhälsa och evals-status för att demonstrera både funktion och kontroll.

## Sammanfattning

Det som gör den här typen av rapid prototyping framgångsrik är inte en enskild modell eller ett enskilt verktyg. Det är kombinationen av fyra arbetssätt:

- hela stacken demonstrerbar varje sprint,
- tydliga kontrakt mellan komponenter,
- kontinuerlig användarförankring,
- evals före feature-ökning.

Utan den sista punkten är det lätt att bygga en imponerande demo som inte håller över tid. Med strukturerad utvärdering, tydlig feedbackloop och kontrollerad iteration får vi i stället en prototyp som går att lita på och bygga vidare på.
