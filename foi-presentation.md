Förberedelseuppgift FOI — Rapid Prototyping av Analysverktyg

Scenario

Underrättelseanalytiker på Försvarsmakten behöver ett verktyg som hjälper dem bearbeta stora mängder ostrukturerad text — nyhetsartiklar, forum, sociala medier, och rapporter från egna källor. Idag läser de manuellt, kopierar intressanta bitar till Excel, och försöker hålla koll på mönster i huvudet. När volymen ökar blir det ohanterligt.

Förmågan vi ska bygga: Ett verktyg där analytikern kan koppla in sina källor — textflöden, URL:er, uppladdade dokument — och få tillbaka strukturerade sammanfattningar, automatiskt flaggat innehåll, och möjlighet att söka på betydelse snarare än exakta ord.

Fördelar: Analytikern hinner gå igenom X gånger så mycket mer material. Risken att missa viktiga kopplingar minskar. Erfaren kunskap fångas upp via feedback och förbättrar verktyget över tid.


Rapid Prototyping av Analysverktyg för Textbearbetning

INLEDNING — Vad bygger vi och till vem?

Scenariot jag valt: Försvarsmaktens underrättelseanalytiker behöver ett verktyg som hjälper dem bearbeta stora mängder ostrukturerad text — nyhetsartiklar, öppna källor från forum och sociala medier, och rapporter. Idag gör de det manuellt: läser, markerar, kopierar till Excel. När volymen ökar missar de kopplingar och hinner inte fram till det som är intressant.

Vi ska leverera en prototyp som kan ta emot text från olika källor, automatiskt sammanfatta och plocka ut det viktigaste — namn, platser, händelser — och låta analytikern söka och filtrera för att se mönster.

**Teamet:** Jag driver rapid prototyping och bygger systemet — fullstack, infrastruktur, integrationer. Projektledaren har domänkunskap om analytikernas arbete och vet vilka frågor verktyget ska kunna besvara. Forskningsingenjören har språkmodeller som utgångspunkt och förbättrar dem löpande — min uppgift är att göra dem användbara.

VECKA 1 — Förstå problemet innan vi kodar

Första veckan kodar jag väldigt lite. Tre saker händer parallellt.

Jag skriver ett litet testprogram i .NET som kör några exempel mot modellen och loggar svaren. På en dag har jag svar på det viktiga: *hur pratar jag med den, hur snabb är den, hur stora texter klarar den, och hur beter den sig när det går fel.*

Det räcker för att jag ska veta hur backend ska se ut — om jag kan svara direkt eller måste köa, om jag måste dela upp långa dokument i bitar, om cachning är meningsfull. Och jag har en lista frågor till forskningsingenjören, bland annat om vi kan paketera modellen som en MCP-server för att få ett rent gränssnitt.

Projektledaren sitter med två-tre analytiker och kartlägger hur de jobbar idag:
- Vad läser de?
- Vilka kopplingar letar de efter?
- Vad missar de?

Det ger oss en prioriterad lista.

Forskningsingenjören kör modellen på exempeldata och mäter precision — alltså hur ofta modellen har rätt. Vad klarar den redan? Var behöver den mer träningsdata?

Vi träffas på fredag och enas om: Vad är det minsta vi kan visa om två veckor som en analytiker faktiskt kan använda? Svaret blir: ta emot text från en enkel inmatning, köra modellen, visa vad den hittar.

Parallellt sätter jag upp grundläggande infrastruktur

- Spec-Kit — för att skriva specifikationer som AI-verktyg kan bryta ner till körbara uppgifter. Detta kan användas både för att implementera lösningar som projektledaren får fram samt för att välja teknik-stack.
- Prompterna ligger i Git precis som kod. En sak folk ofta glömmer — prompterna vi skickar till modellen är också något vi bygger. De ändras, de blir bättre, och ibland blir de sämre. Därför behandlar jag dem som kod: de ligger i Git, de reviewas i pull requests, och de har changelog. Ändrar någon en prompt så ser vi varför i historiken, och evals-sviten säger oss om ändringen faktiskt gjorde det bättre eller sämre. Kan vi rulla tillbaka en kodändring så kan vi rulla tillbaka en prompt också.
MCP-servrar kopplade mot vårt repo, vår dokumentation, och vår issue-tracker — så att AI-agenterna har kontext om projektet när de jobbar. Körs lokalt eller i moln.
-Git-repo — hostas på en intern GitLab-server (ingen GitHub för klassad miljö). Samma behörigheter, samma CI-verktyg som GitHub Actions fast lokalt — GitLab CI.
- CI-pipeline (GitLab CI) — kör enhetstester på varje push, bygger nya container-images på merge till `main`, och pushar dem till ett internt image-register. CI-resultatet blir återanvändbart, spårbart och deploybart.
- Git-strategi: trunk-based development.** Bara en huvudbranch (`main`), korta feature-branches som mergas snabbt. Mindre mergekonflikter i ett litet team, snabbare feedback. GitFlow är overkill för tre personer.
- Docker Compose — en fil som definierar alla containrar: backend-API, databas, frontend, och modell-tjänst. Varje container har sina portar, environment-variabler och volymer definierade. Startas med `docker compose up`, stoppas med `docker compose down`.
- Cloud eller on-prem? Klassad data får inte ligga i publika moln. Jag provar arkitekturen lokalt på en dev-server, men målet är on-prem-deploy från dag ett. Inga Azu-beroendenre/AWS.

Säkerhet och dataklassning från dag ett

En sak till som är värd att nämna tidigt: dataklassningen styr hela arkitekturen, inte tvärtom. Vi reder ut med projektledaren redan i vecka ett vilken nivå materialet ligger på — öppen källa, begränsat, eller högre — för det avgör vilken miljö vi överhuvudtaget får köra i. Olika klassnivåer körs i separata miljöer.

Konkret betyder det att allt som rör modellanrop, källmaterial och feedback loggas för spårbarhet — det gör vi ändå via Langfuse för observability, men det dubbelfunkar som audit-logg. Ingen träningsdata lämnar miljön.

Och jag ser till att ingenting i systemet pratar med internet utan att vi vet om det. Nätverket är stängt utåt som default — tjänster får inte ringa ut. Alla paket och Docker-images vi använder hämtas från ett internt register som vi kontrollerar, inte direkt från npm eller Docker Hub. Då kan inget paket smyga med som ringer hem till någon extern server.

Innan vi går vidare pratar vi igenom vad som kan gå fel. Den största risken forskningsingenjören ser är att modellen inte är tillräckligt bra på svenska och på det militära fackspråket. Det vill vi testa direkt, inte för långt fram.

Så redan i vecka ett kör vi ett snabbt test tillsammans: projektledaren samlar exempeltexter, forskningsingenjören kör dem genom modellen, och jag bygger det lilla testharnesset så vi kan mäta resultatet. Blir det tunt så äger forskningsingenjören plan B.

Min roll är inte att hitta alla risker själv. Min roll är att se till att vi pratar om dem tidigt och att infrastrukturen finns för att testa dem snabbt.

VECKA 2-3 — Walking skeleton, hela stacken

Nu bygger jag en fungerande vertikal skärva genom hela systemet. Inte färdigt — men fungerande ände till ände.

Backend

Ett REST-API i .NET (ASP.NET Core). Men själva AI-delen byggs inte som en enkel modell bakom en endpoint — utan som en agent-pipeline. Analytikerns text går igenom:

1. Ingestion — källor hämtas (URL, upload, stream) via MCP-servrar som gör att modellen kan prata med källor på ett standardiserat sätt
2. Orchestrator-agent — planerar vilka analyssteg som behövs för varje dokument
3. Specialiserade tool-calls — sammanfattning, nyckeltermextrahering, semantisk indexering — körs parallellt
4. Resultat — lagras strukturerat och indexeras i en vektordatabas för semantisk sökning

Integrationslager via MCP: Forskningsingenjören kan exponera sin modell som en MCP-server — då kan jag (och andra verktyg, som Copilot) använda den utan specialkoppling.

Datalager i två delar

- Relationsdatabas (PostgreSQL) — strukturerad data: dokument, metadata, användarfeedback, körloggar
- Vektordatabas (pgvector eller Qdrant) — embeddings för semantisk sökning och RAG-funktionalitet

Frontend

En enkel webbapp. Analytikern kan:
- Klistra in text eller ange en URL som källa
- Ladda upp en PDF eller textfil
- Se en sammanfattning av innehållet
- Se en lista över utplockade namn, platser och händelser
- Söka semantiskt — hitta dokument som handlar om ungefär samma sak, även om orden skiljer sig

För visualisering håller jag det enkelt i första versionen: listor och tabeller. Om analytikern frågar efter grafvy eller tidslinje lägger vi till det i senare sprint.

Vecka 3, fredag: Första demon

Vi bjuder in en analytiker. De klistrar in en riktig nyhetstext. Sammanfattningen dyker upp. Nyckeltermer listas. Det ser grovt ut — en del är fel — men analytikern förstår direkt vad verktyget vill åstadkomma. Och nu börjar den intressanta feedbacken:
- *"Kan jag se när olika källor rapporterar samma sak?"*
- *"Kan jag markera vilka sammanfattningar som stämmer?"*

VECKA 4-6 — Iteration med riktiga användare

Här snurrar vi i veckosprintar. Varje fredag: demo och feedback.

Vecka 4: Evals och feedback-loop

Här bygger jag två saker parallellt:

- Användarfeedback — analytikerns tumme upp/ner + kommentar, lagras strukturerat
- Automatiska evals — en testsvit som kör fasta prompter mot modellen i CI, mäter kvalitet (LLM-as-judge), regression-testar varje ny modellversion

Det andra är nytt jämfört med klassisk SW-testning. Man kan inte skriva `assertEquals` när svaret är fri text — det ser olika ut varje gång. Så här gör vi istället: jag bygger en liten datasamling på kanske femtio exempel där vi vet vad ett bra svar ska innehålla. Sedan kör jag modellen på alla exempel och poängsätter svaren. Vissa går att kolla med enkla regler — "innehåller svaret ordet Ukraina?" — men för kvalitativa mått låter vi en annan LLM döma: "på en skala ett till fem, hur bra sammanfattar det här svaret källtexten?" Det kallas LLM-as-judge.

Hela sviten körs automatiskt varje gång forskningsingenjören rullar ut en ny modellversion eller jag ändrar en prompt. Vi ser direkt om kvaliteten gick upp eller ner. Verktygen som finns för det här är till exempel Promptfoo (öppen källkod, körs lokalt i CI), Inspect från brittiska AI Security Institute (statligt byggt, helt on-prem, extra relevant för oss) eller Langfuse som också har evals-stöd.

Feedback + evals = forskningsingenjören kan med trygghet rulla ut en ny modell utan att vänta på manuell validering.

Vecka 5-6: Batch och mer analysverktyg

Analytikern vill inte mata in en text i taget. Jag bygger filuppladdning för flera dokument samtidigt och utökar med fler analyssätt:
- Semantisk sökning — hitta dokument som handlar om något, inte bara innehåller specifika ord
- Tidslinjevy — händelser sorterade kronologiskt över dokumentmängden
- Sammanfattning över flera dokument — "vad säger dessa tio källor om ämne X?"
- Filtrering — på källtyp, tidsperiod, region

Jag lägger till ett verktyg i taget, demar varje fredag, och låter analytikerna prioritera vad som är viktigast härnäst.

Utan användare i rummet varje dag?

Vi har inte analytikerna tillgängliga jämt — de jobbar. Min strategi:
- Automatiska tester på allt — backend, frontend, integrationer. Jag kan förändra kod tryggt.
- Syntetisk testdata — en uppsättning exempeltexter med förväntade resultat. Regression-tester körs i CI.
- Projektledaren agerar som en "proxy-användare" mellan demo-sessioner — de har domänkunskapen för att ge preliminär feedback.
- När analytiker finns på plats, prioriterar jag observation före demos. Jag lär mig mer av att se dem använda verktyget.

Under perioden sitter jag bredvid en analytiker vid två tillfällen och observerar tyst. Det är en av de bästa UX-metoderna jag känner. Mellan sessionerna kompletterar vi med att gå igenom konkreta use cases tillsammans med projektledaren — "visa mig exakt hur du skulle lösa den här uppgiften idag" — och korta intervjuer på femton minuter när vi har specifika frågor.

Modellbyte under iteration

Med MCP som gränssnitt blir modellbyte enkelt — forskningsingenjören registrerar en ny MCP-server, vi pekar om konfigurationen, och evals-suiten validerar automatiskt att kvaliteten inte regrerat. Ingen kodändring, ingen omstart av andra tjänster.

VECKA 7-8 — Paketering och leverans

Sista sprinten handlar om robusthet och leverans.

En enkel startupplevelse

Ett startskript som startar alla containrar (`docker compose up`) och öppnar en intern dashboard (t.ex. i NiceGUI, Python-biblioteket för snabba webbdashboards) som visar vilka tjänster som körs, loggströmmar, och modellens status.

On-prem AI-stack

- Modellkörning: Ollama eller vLLM för lokala språkmodeller — körs i egen container, GPU-accelererat om hårdvara finns
- Observability: Langfuse self-hosted för att spåra alla LLM-anrop, kostnader, latens och hallucinationsfrekvens

App / Agent
     ↓
Langfuse SDK
     ↓
LLM (t.ex. API)
     ↓
Langfuse server (self-hosted)
     ↓
Dashboard + metrics

LLM-system utan observability = black box. Langfuse gör det mätbart, debuggbart och förbättringsbart.

- MCP-servrar: Varje integration (mot källor, mot databaser, mot modeller) är en MCP-server — gör att nya AI-verktyg enkelt kan kopplas in utan custom-integration.
- Allt bakom brandvägg — inga externa API-beroenden.

AI i hela utvecklingscykeln

- Kodgenerering — Copilot i VS Code för boilerplate, tester, refaktoreringar.
- Sub-agents — parallella uppgifter som "generera migrations", "uppdatera OpenAPI-spec", "skriv ADR för senaste arkitekturbeslut" körs som separata agent-jobb.
  - Architecture Decision Record — korta markdown-filer som förklarar varför vi valde en viss teknik, inte bara vad. En ADR per arkitekturbeslut, versionerad i Git tillsammans med koden.
- Arkitekturdiagram — jag använder Mermaid ("Diagram as Code") så att diagrammen ligger i Git tillsammans med koden och uppdateras (manuellt eller med scripts) när systemet förändras.
- Spec-Kit-arbetsflöde — jag skriver specifikationer som människan förstår, AI genererar detaljerade tasks, och jag granskar innan de körs.
- Levande dokumentation — Mermaid-diagram + ADR:er + API-spec genereras och uppdateras delvis av AI-agenter som triggar på commits.

Leveransdemo

Demon följer en analytikers riktiga arbetsdag, inte en funktionslista. Ungefär så här:

1. Analytikern laddar upp en batch med tjugo artiklar från morgonens nyhetsflöde.
2. Systemet kör igenom dem, sammanfattar varje artikel och plockar ut namn, platser och händelser.
3. Analytikern söker semantiskt — till exempel "rapporter om logistik i en viss region" — och ser att systemet hittar artiklar som inte innehåller själva ordet "logistik".
4. De öppnar en tidslinjevy och ser händelser sorterade kronologiskt över hela batchen.
5. De markerar en sammanfattning som fel — feedback sparas och syns i evals-panelen.
6. De exporterar resultatet som en rapport de kan skicka vidare.

Parallellt visar jag den interna dashboarden: alla tjänster gröna, modellens senaste evals-resultat, antal anrop och latens. Då ser mottagaren inte bara att verktyget funkar — de ser också att vi vet hur det mår.

AVSLUTNING — Vad gör skillnaden?

Om jag ska sammanfatta vad jag tror gör skillnaden i rapid prototyping, så är det fyra saker:

Ett: Hela stacken varje sprint. Aldrig tre veckor på bara backend. Analytikern ser alltid en fungerande produkt — annars får vi ingen feedback.

Två: Rätt kontrakt mellan delarna. Modellen kommer att bytas ut. Databasen kommer att växa. Frontend kommer att skrivas om någon gång. Det som håller ihop systemet är inte koden — det är kontrakten mellan bitarna. Jag använder tre stycken.

Mot modellen använder jag MCP — det är ett öppet protokoll för hur en app pratar med en AI-modell. Forskningsingenjören packar sin modell som en MCP-server, och jag pratar med den via standardiserade meddelanden. 

Mot frontend har jag ett vanligt REST-API med OpenAPI-kontrakt. Frontend blir aldrig blockerad av att jag håller på i backend.

Mot databasen går allt genom ett tunt repository-lager. När vi lägger till vektordatabasen i sprint två behöver resten av koden inte ens veta om det.

Med rena kontrakt kan vi tre jobba parallellt utan att trampa på varandra.

Tre: Användaren i rummet. Sitt bredvid och titta. Då ser man om det man bygger är rätt sak.

Fyra: Evals före features. Det här är skillnaden mot vanlig mjukvara. När vi bygger AI kan vi inte bara skriva ett test som säger "svaret ska vara 42" — svaret är ju fri text och det ser olika ut varje gång. Så jag bygger tidigt en liten testsvit med exempeltexter där vi vet vad ett bra svar ska innehålla. Varje gång forskningsingenjören rullar ut en ny modell körs sviten automatiskt och vi ser om kvaliteten gick upp eller ner.

Utan evals är en AI-prototyp bara en demo som råkar funka för tillfället. Med evals vet vi faktiskt om vi blir bättre.