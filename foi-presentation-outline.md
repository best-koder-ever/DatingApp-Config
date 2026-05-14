# FOI Presentation — Speaker Outline

❌ "Min uppgift är att göra modellen användbar."
❌ "Min roll är inte att hitta alla risker själv — min roll är att vi pratar om dem tidigt."
❌ "Det som håller ihop systemet är inte koden — det är kontrakten mellan bitarna."
❌ "Utan evals är en AI-prototyp bara en demo som råkar funka för tillfället."
❌ "Det är så jag driver rapid prototyping."

═══════════════════════════════════════════════════════
## 1. INLEDNING — 40 sek
═══════════════════════════════════════════════════════

**SCENARIO:** Försvarsmaktens underrättelseanalytiker

**PROBLEM:**
- drunknar i text — nyheter, forum, rapporter
- idag: läs manuellt → kopiera till Excel
- volymen ökar → missar kopplingar

**LÖSNING:** ta in text → sammanfatta → plocka data → sökbart på betydelse/semantisk sökning

**TEAMET:**
- **JAG** → driver, bygger, fullstack
- **PL** (projektledare) → domän, vet vad analytikern behöver
- **FI** (forskningsingenjör) → modellen

⚓ *"Min uppgift är att göra modellen användbar."*

═══════════════════════════════════════════════════════
## 2. VECKA 1 — Förstå innan vi kodar — 50 sek
═══════════════════════════════════════════════════════

### 3 saker parallellt

| Vem | Gör |
|-----|-----|
| ** JAG ** | teknisk test mot modellen |
| ** Projektledaren **  | kartlägger analytikerna |
| ** Forskningsingenjören **  | mäter precision på exempeldata |

**Min test svarar på:**
- hur kan man anropa den
- hur snabb svarar den
- hur stort är context fönstret 
- hur hanteras felhantering, hur kan man mäta hallucinationer
- → kan Forskningsingenjören paketera som **MCP-server**?

**FREDAG:** enas om MVP

### Infra (parallellt)

- git på inter repo -  **GitLab** + **GitLab CI**
- **docker-compose** (alla containrar)
- **prompts i git** (reviewas, changelog, rollbackbara)
- **Spec-Kit** (specs → AI-tasks)
- **trunk-based** short-trunk undviker merge konfikter
- **on-prem** från dag ett — ingen molnberoende

### Säkerhet (kort)

- **dataklassning styr arkitekturen**
- stängt nät utåt + internt paketregister
- allt loggas (Langfuse = audit-logg på köpet)

### Risk

- **största:** modellen klarar inte svenska + militärt fackspråk
- → snabbtest redan v1, **Forskningsingenjören ser över detta**

⚓ *"Min roll är inte att hitta alla risker själv — min roll är att vi pratar om dem tidigt."*

═══════════════════════════════════════════════════════
## 3. VECKA 2-3 — Walking skeleton — 1:20
═══════════════════════════════════════════════════════

> End-to-end lösning. Inte färdigt — fungerande.

### Backend — .NET (ASP.NET Core)

Flöde 1 — INMATNING (analytiker laddar upp dokument)

Dokument laddas upp
     ↓
FI:s modell  →  sammanfatta + extrahera data
     ↓
Spara i databasen (text + vektorer)



Flöde 2 — FRÅGA (analytiker söker/frågar) 

 **Agent-pipeline**:

Analytikerns fråga
     ↓
Orchestrator (planerar) → 3 parallella anrop (.Net Semantic Kernel eller LangChain har inte användt dem själv ännu)
├ Vektor-DB (semantisk sökning)
├ MySQL (dokument) Söker i DB
└ LLM modellen (via MCP)
     ↓
Svar

### Datalager — två delar

- **├ MySQL (dokument) Söker i DB** — dokument, metadata, feedback
- **pgvector / Qdrant** — embeddings för semantisk sökning

### Frontend — webbapp på desktop

- **React + TypeScript** — starkast ekosystem för data vyer (tabeller, tidslinjer)

- v2-3 funktioner: klistra in / ladda upp / se sammanfattning / se extraherad data / tumme upp/ner

### V3 fredag = FÖRSTA DEMON

- analytiker testar live
- feedback börjar: *"kan jag se när källor rapporterar samma sak?"*

═══════════════════════════════════════════════════════
## 4. VECKA 4-6 — Iteration med användare — 1:20
═══════════════════════════════════════════════════════

> Veckosprintar. Varje fredag: demo + feedback.

### V4 — Evals + feedback-loop

**Evals = enhetstester, fast för AI.**

- **50 testfall** i en YAML-fil: input + vad svaret ska innehålla
- **Promptfoo** kör dem i CI varje push
- **Tre nivåer:** regel-check · LLM-as-judge (1–5) · mänsklig stickprov
- **Tröskel 90%** — under = bygget blir rött
- **Användarfeedback** (tumme upp/ner) blir nya testfall

→ Forskningsingenjören byter modell utan manuell validering.
→ Jag ser direkt om något blev sämre efter en ändring.

### V5-6 — Batch + fler analysverktyg

- batch-uppladdning
- semantisk sökning
- tidslinjevy
- multi-doc-sammanfattning
- filter (källtyp, tid, region)

### Begränsad tillgång till analytiker?

**När vi inte kan träffas:**
- automatiska tester på syntetisk data
- Projektledaren agerar proxy-användare

**När vi kan träffas:**
- åka till deras arbetsplats, sitta bredvid och observera tyst

### Modellbyte under iteration

→ MCP gör det trivialt: registrera ny server, evals validerar, ingen kodändring

═══════════════════════════════════════════════════════
## 5. VECKA 7-8 — Paketering & leverans — 1:00
═══════════════════════════════════════════════════════

### Startupplevelse

- `docker compose up` → allt rullar
- intern dashboard (NiceGUI) → tjänster, loggar, modellstatus

### On-prem AI-stack

- **Ollama / vLLM** — lokala språkmodeller, GPU-container
- **Langfuse self-hosted** — alla LLM-anrop, latens, kostnad

    Observability: Langfuse self-hosted för att tracka alla LLM-anrop, kostnader (om vi lägger till större modeller senare), latens och hallucinationsfrekvens

    App / Agent
        ↓
    Langfuse SDK
        ↓
    LLM (t.ex. API)
        ↓
    Langfuse server (self-hosted)
        ↓
    Dashboard + metrics


    LLM-system utan observability = black box

    Langfuse gör det till:
    👉 mätbart, debuggbart och förbättringsbart



- **MCP-servrar** — varje integration
- allt bakom brandvägg

### AI i utvecklingscykeln

- Copilot (kod)
- Sub-agents (migrations, OpenAPI, ADR)
- Mermaid (diagram-as-code)
- Spec-Kit (specs → tasks)

### Leveransdemo (riktig arbetsdag, INTE funktionslista)

1. ladda upp 20 artiklar
2. systemet sammanfattar + extraherar
3. semantisk sökning
4. tidslinjevy
5. markera fel → feedback → evals
6. exportera rapport

→ visa intern dashboard parallellt: *"vi vet hur systemet mår"*

═══════════════════════════════════════════════════════
## 6. AVSLUTNING — 4 principer — 30 sek
═══════════════════════════════════════════════════════

### 1. Hela stacken varje sprint
> Aldrig fastna i veckor på bara backend.

### 2. Rätt kopplingar mellan delarna

⚓ *"Det som håller ihop systemet är inte koden — det är kontrakten mellan bitarna."*

Tre gränssnitt som skyddar oss när saker byts ut:
- **Mot modellen** → MCP (standardprotokoll — byter FI modell, inget i min kod ändras)
- **Mot frontend** → REST + OpenAPI (beskrivning av alla anrop — frontend och backend kan byggas parallellt)
- **Mot databasen** → repository-lager (all SQL samlad ett ställe — byter vi databas, bara den biten ändras)

### 3. Användaren i rummet
> Sitt bredvid och titta.

### 4. Evals före features

⚓ *"Utan evals är en AI-prototyp bara en demo som råkar funka för tillfället."*

⚓ *"Det är så jag driver rapid prototyping."*

═══════════════════════════════════════════════════════
## 7. FAQ — i bakhuvudet (säg INTE proaktivt)
═══════════════════════════════════════════════════════

| F | Kort svar |
|---|-----------|
| Varför .NET? | starkast i det, lika produktivt, modell är ändå separat tjänst |
| Varför trunk-based? | 3 personer + 8v → GitFlow overkill |
| Hallucinationer? | feedback fångar fel, källan visas alltid, analytiker = sista skydd |
| Om FI inte levererar? | bygger mot integrationslagret → koppla in generisk LLM som fallback |
| TRL vs produktion? | TRL 4: ingen hårdning, ingen multi-user, ingen skalning |
| Om FI och PL är oense? | gör det till datafråga: bygg båda, kör evals, låt analytiker testa. PL äger backlog. ADR. |

═══════════════════════════════════════════════════════
## TIDSBUDGET (kontroll)
═══════════════════════════════════════════════════════

```
Inledning        :40
Vecka 1          :50
Vecka 2-3       1:20
Vecka 4-6       1:20
Vecka 7-8       1:00
Avslutning       :30
─────────────────────
Totalt          5:40
```

═══════════════════════════════════════════════════════
## ÖVNING
═══════════════════════════════════════════════════════

1. Läs långa dokumentet en gång — fatta innehållet
2. Lägg bort. Titta bara på den här outlinen
3. Prata högt. Klockan på.
4. Andra varvet: utan outline. Notera var du fastnar
5. Tredje varvet: spela in
6. ✅
