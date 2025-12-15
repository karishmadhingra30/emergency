# Emergency Shelter & First Aid Assistant - Development Flowchart

## Table of Contents
1. [High-Level System Architecture](#1-high-level-system-architecture)
2. [Application Startup Flow](#2-application-startup-flow)
3. [User Request Flow](#3-user-request-flow)
4. [Chatbot Processing Flow](#4-chatbot-processing-flow)
5. [Shelter Search Flow](#5-shelter-search-flow)
6. [Map Rendering Flow](#6-map-rendering-flow)
7. [Development Workflow](#7-development-workflow)
8. [Data Flow Diagram](#8-data-flow-diagram)
9. [Component Interaction Diagram](#9-component-interaction-diagram)

---

## 1. High-Level System Architecture

```mermaid
graph TB
    User[User Browser] --> Frontend[Frontend Layer<br/>HTML/JS/CSS]
    Frontend --> API[Flask REST API<br/>app.py]

    API --> Routes{Route Handler}

    Routes -->|/map| MapPage[Serve Map Page]
    Routes -->|/chat| ChatAPI[Chat Endpoint]
    Routes -->|/shelters| ShelterAPI[Shelter Endpoint]
    Routes -->|/nearest-shelter| NearestAPI[Nearest Shelter]

    ChatAPI --> GemmaChat[GemmaEmergencyChat<br/>gemma_chat.py]
    ShelterAPI --> ShelterMgr[ShelterManager<br/>app.py]
    NearestAPI --> ShelterMgr

    GemmaChat --> KnowledgeCheck{Query Type?}
    KnowledgeCheck -->|Shelter Query| ShelterMgr
    KnowledgeCheck -->|Medical Query| KnowledgeRetrieval[Knowledge Retrieval]

    KnowledgeRetrieval --> FirstAid[first_aid_knowledge.py<br/>Static Knowledge]
    KnowledgeRetrieval --> VectorDB[Vector DB<br/>PDF RAG - Optional]

    KnowledgeRetrieval --> OllamaAPI[Ollama API<br/>Gemma 2 Model]

    ShelterMgr --> ExcelData[shelters_downloaded.xlsx<br/>In-Memory Data]

    OllamaAPI --> Response[AI Response]
    ShelterMgr --> ShelterResponse[Shelter List]

    Response --> Frontend
    ShelterResponse --> Frontend

    Frontend --> LeafletMap[Leaflet.js Map<br/>OpenStreetMap]
    Frontend --> ChatWidget[Chat Interface]

    style Frontend fill:#e1f5ff
    style API fill:#fff4e1
    style GemmaChat fill:#ffe1f5
    style ShelterMgr fill:#e1ffe1
    style OllamaAPI fill:#f5e1ff
    style ExcelData fill:#ffffcc
```

---

## 2. Application Startup Flow

```mermaid
flowchart TD
    Start([Application Start]) --> LoadEnv[Load .env Configuration<br/>GOOGLE_MAPS_API_KEY]
    LoadEnv --> ImportModules[Import Dependencies<br/>Flask, pandas, gemma_chat]

    ImportModules --> InitFlask[Initialize Flask App<br/>Configure CORS]
    InitFlask --> InitShelterMgr[Create ShelterManager Instance]

    InitShelterMgr --> LoadExcel{shelters_downloaded.xlsx<br/>exists?}
    LoadExcel -->|Yes| ReadExcel[Load Excel into Memory<br/>pandas.read_excel]
    LoadExcel -->|No| EmptyData[Initialize Empty Shelter List]

    ReadExcel --> ParseShelters[Parse Shelter Data<br/>name, type, lat, lon, address]
    ParseShelters --> StoreMem[Store in shelter_manager.shelters<br/>List of Dictionaries]

    EmptyData --> StoreMem
    StoreMem --> InitGemma[Initialize GemmaEmergencyChat<br/>gemma_chat.py]

    InitGemma --> CheckOllama{Ollama Service<br/>Running?}
    CheckOllama -->|Yes| LoadModel[Load Gemma 2 Model<br/>2B Parameters]
    CheckOllama -->|No| FallbackMode[Enable Fallback Mode<br/>Rule-based responses]

    LoadModel --> CheckVectorDB{Vector DB<br/>Available?}
    FallbackMode --> CheckVectorDB

    CheckVectorDB -->|Yes| LoadFAISS[Load FAISS Index<br/>vectordb.pkl + faiss.index]
    CheckVectorDB -->|No| SkipRAG[Skip PDF RAG<br/>Use Static Knowledge Only]

    LoadFAISS --> RegisterRoutes
    SkipRAG --> RegisterRoutes[Register Flask Routes<br/>/, /map, /chat, /shelters]

    RegisterRoutes --> StartServer[Start Flask Dev Server<br/>Port 8080]
    StartServer --> Ready([Application Ready<br/>Listening on :8080])

    style Start fill:#90EE90
    style Ready fill:#90EE90
    style LoadExcel fill:#FFE4B5
    style CheckOllama fill:#FFE4B5
    style CheckVectorDB fill:#FFE4B5
```

---

## 3. User Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Flask as Flask Server<br/>(app.py)
    participant ShelterMgr as ShelterManager
    participant Gemma as GemmaChat
    participant Ollama

    User->>Browser: Open http://localhost:8080/map
    Browser->>Flask: GET /map
    Flask->>Browser: Return map_with_chat.html
    Browser->>User: Display Map Interface

    Note over Browser: Page loads Leaflet.js
    Browser->>Flask: GET /shelters
    Flask->>ShelterMgr: get_all_shelters()
    ShelterMgr->>Flask: JSON Array of Shelters
    Flask->>Browser: Shelter Data
    Browser->>Browser: Plot Shelter Markers on Map
    Browser->>User: Display Interactive Map

    User->>Browser: Enter Location<br/>"30.324329, 78.0418"
    Browser->>Browser: Parse Coordinates
    Browser->>Browser: Place Orange User Marker
    Browser->>User: Show User Location on Map

    User->>Browser: Type Message<br/>"nearest shelter"
    Browser->>Flask: POST /chat<br/>{message, location}
    Flask->>Gemma: gemma_chat(message, location)

    alt Shelter Query Detected
        Gemma->>ShelterMgr: find_nearest_shelters(location)
        ShelterMgr->>ShelterMgr: Calculate Distances<br/>(Haversine Formula)
        ShelterMgr->>ShelterMgr: Sort by Distance
        ShelterMgr->>Gemma: Top 5 Shelters
        Gemma->>Flask: Formatted Response
    else Medical Query
        Gemma->>Gemma: retrieve_relevant_knowledge()
        Gemma->>Ollama: Query with Context
        Ollama->>Gemma: AI Generated Response
        Gemma->>Flask: Medical Advice
    end

    Flask->>Browser: JSON Response
    Browser->>Browser: Display in Chat Widget
    Browser->>User: Show Response
```

---

## 4. Chatbot Processing Flow

```mermaid
flowchart TD
    Start([User Sends Message]) --> Receive[POST /chat Endpoint<br/>app.py]
    Receive --> Extract[Extract Data<br/>message, user_location]

    Extract --> CallGemma[Call gemma_chat.chat<br/>gemma_chat.py]
    CallGemma --> DetectType{Query Type<br/>Detection}

    DetectType -->|"nearest shelter"<br/>"find shelter"| ShelterQuery[Shelter Query Detected]
    DetectType -->|Medical Keywords| MedicalQuery[Medical Query Detected]
    DetectType -->|General| GeneralQuery[General Query]

    ShelterQuery --> HasLocation{User Location<br/>Provided?}
    HasLocation -->|Yes| ImportShelterMgr[Import shelter_manager<br/>from app.py]
    HasLocation -->|No| NoLocationError[Return Error:<br/>"Please provide location"]

    ImportShelterMgr --> FindNearest[find_nearest_shelters<br/>latitude, longitude]
    FindNearest --> CalcDistance[Calculate Distance for Each Shelter<br/>Haversine Formula]

    CalcDistance --> SortShelters[Sort Shelters by Distance<br/>Ascending Order]
    SortShelters --> Top5[Select Top 5 Shelters]
    Top5 --> FormatShelter[Format Response:<br/>Name, Type, Distance, Address]
    FormatShelter --> ReturnShelter[Return Shelter List]

    MedicalQuery --> KeywordExtract[Extract Medical Keywords<br/>bleeding, burn, CPR, etc.]
    KeywordExtract --> SearchKnowledge{Search Knowledge<br/>Sources}

    SearchKnowledge --> StaticKnowledge[Search first_aid_knowledge.py<br/>FIRST_AID_DATA Dictionary]
    SearchKnowledge --> VectorSearch{Vector DB<br/>Available?}

    VectorSearch -->|Yes| FAISSSearch[FAISS Semantic Search<br/>vectordb.pkl]
    VectorSearch -->|No| SkipVector[Skip Vector Search]

    StaticKnowledge --> CombineContext[Combine Knowledge Contexts]
    FAISSSearch --> CombineContext
    SkipVector --> CombineContext

    CombineContext --> BuildPrompt[Build Ollama Prompt<br/>System + User + Context]
    BuildPrompt --> CheckOllama{Ollama<br/>Available?}

    CheckOllama -->|Yes| QueryOllama[POST http://localhost:11434/api/chat<br/>Model: gemma2:2b]
    CheckOllama -->|No| FallbackResponse[Return Static Knowledge<br/>Rule-based Response]

    QueryOllama --> StreamResponse[Stream Response Chunks]
    StreamResponse --> ParseAI[Parse AI Response]
    ParseAI --> FormatMedical[Format Medical Advice]

    GeneralQuery --> BuildPrompt

    FormatMedical --> ReturnResponse[Return to Flask Endpoint]
    FallbackResponse --> ReturnResponse
    ReturnShelter --> ReturnResponse
    NoLocationError --> ReturnResponse

    ReturnResponse --> SendJSON[Send JSON to Frontend]
    SendJSON --> End([Display in Chat Widget])

    style Start fill:#90EE90
    style End fill:#90EE90
    style DetectType fill:#FFD700
    style HasLocation fill:#FFD700
    style SearchKnowledge fill:#FFD700
    style VectorSearch fill:#FFE4B5
    style CheckOllama fill:#FFE4B5
```

---

## 5. Shelter Search Flow

```mermaid
flowchart TD
    Start([Shelter Search Request]) --> Input[Input: User Location<br/>latitude, longitude]
    Input --> GetShelters[Get All Shelters<br/>shelter_manager.shelters]

    GetShelters --> CheckEmpty{Shelters<br/>List Empty?}
    CheckEmpty -->|Yes| NoShelters[Return: No shelters available]
    CheckEmpty -->|No| IterateShelters[Iterate Through Each Shelter]

    IterateShelters --> LoopStart{For Each<br/>Shelter}
    LoopStart --> ExtractCoords[Extract Shelter Coordinates<br/>shelter_lat, shelter_lon]

    ExtractCoords --> Haversine[Calculate Distance<br/>Haversine Formula]

    Haversine --> Formula[Formula Steps:<br/>1. Convert degrees to radians<br/>2. Calculate Δlat, Δlon<br/>3. Calculate a = sin²(Δlat/2)<br/>   + cos(lat1) * cos(lat2) * sin²(Δlon/2)<br/>4. Calculate c = 2 * atan2(√a, √(1-a))<br/>5. Distance = R * c<br/>R = 6371 km Earth radius]

    Formula --> StoreDistance[Store Distance with Shelter Data<br/>shelter['distance'] = distance_km]
    StoreDistance --> MoreShelters{More<br/>Shelters?}

    MoreShelters -->|Yes| LoopStart
    MoreShelters -->|No| SortByDistance[Sort Shelters by Distance<br/>Ascending Order]

    SortByDistance --> SelectTop[Select Top N Shelters<br/>Default: 5]
    SelectTop --> FormatResponse[Format Each Shelter:<br/>- Name<br/>- Type<br/>- Distance km<br/>- Address<br/>- Rating<br/>- Status]

    FormatResponse --> ReturnList[Return Shelter List<br/>JSON Array]
    NoShelters --> ReturnList
    ReturnList --> End([Response to User])

    style Start fill:#90EE90
    style End fill:#90EE90
    style Haversine fill:#FFB6C1
    style Formula fill:#FFE4E1
```

---

## 6. Map Rendering Flow

```mermaid
flowchart TD
    Start([Page Load: map_with_chat.html]) --> LoadHTML[Load HTML Content]
    LoadHTML --> LoadCSS[Load CSS Styles<br/>Leaflet CSS from CDN]
    LoadCSS --> LoadJS[Load JavaScript<br/>Leaflet.js 1.9.4]

    LoadJS --> InitMap[Initialize Leaflet Map<br/>L.map'map']
    InitMap --> SetView[Set Default View<br/>Center: 30.3165, 78.0322<br/>Zoom: 13]

    SetView --> AddTiles[Add OpenStreetMap Tiles<br/>L.tileLayer]
    AddTiles --> TileURL[Tile URL:<br/>https://tile.openstreetmap.org/&#123;z&#125;/&#123;x&#125;/&#123;y&#125;.png]

    TileURL --> FetchShelters[Fetch Shelters<br/>GET /shelters]
    FetchShelters --> WaitResponse{API<br/>Response?}

    WaitResponse -->|Success| ParseJSON[Parse JSON Response<br/>Array of Shelter Objects]
    WaitResponse -->|Error| ShowError[Show Error in Console<br/>Continue with Empty Map]

    ParseJSON --> IterateShelters[Iterate Through Shelters]
    IterateShelters --> LoopStart{For Each<br/>Shelter}

    LoopStart --> ExtractData[Extract Shelter Data:<br/>- name<br/>- type<br/>- latitude<br/>- longitude<br/>- address]

    ExtractData --> DetermineColor{Determine<br/>Marker Color}
    DetermineColor -->|type = 'school'| BlueMarker[Color: Blue]
    DetermineColor -->|type = 'police'| GreenMarker[Color: Green]
    DetermineColor -->|type = 'fire_station'| RedMarker[Color: Red]
    DetermineColor -->|other| GrayMarker[Color: Gray]

    BlueMarker --> CreateMarker[Create Leaflet Marker<br/>L.marker[lat, lon]]
    GreenMarker --> CreateMarker
    RedMarker --> CreateMarker
    GrayMarker --> CreateMarker

    CreateMarker --> AddIcon[Add Custom Icon<br/>L.divIcon with color]
    AddIcon --> CreatePopup[Create Popup Content<br/>HTML with shelter details]
    CreatePopup --> BindPopup[Bind Popup to Marker<br/>marker.bindPopup]
    BindPopup --> AddToMap[Add Marker to Map<br/>marker.addTo(map)]

    AddToMap --> MoreShelters{More<br/>Shelters?}
    MoreShelters -->|Yes| LoopStart
    MoreShelters -->|No| EnableInteraction[Enable Map Interactions<br/>Pan, Zoom, Click]

    ShowError --> EnableInteraction

    EnableInteraction --> WaitUser{User<br/>Interaction?}

    WaitUser -->|Click Marker| ShowPopup[Display Shelter Popup<br/>with Details]
    WaitUser -->|Enter Location| SetUserLocation[Place Orange User Marker<br/>Center Map on Location]
    WaitUser -->|Zoom/Pan| UpdateView[Update Map View<br/>Load New Tiles if Needed]

    ShowPopup --> WaitUser
    SetUserLocation --> WaitUser
    UpdateView --> WaitUser

    style Start fill:#90EE90
    style DetermineColor fill:#FFD700
    style CreateMarker fill:#87CEEB
```

---

## 7. Development Workflow

```mermaid
flowchart TD
    Start([New Feature/Bug Request]) --> Analyze[Analyze Requirements]
    Analyze --> Branch{Task Type?}

    Branch -->|New Feature| FeatureDev[Feature Development]
    Branch -->|Bug Fix| BugFix[Bug Fix]
    Branch -->|Enhancement| Enhancement[Enhancement]

    FeatureDev --> IdentifyFiles[Identify Affected Files]
    BugFix --> IdentifyFiles
    Enhancement --> IdentifyFiles

    IdentifyFiles --> FileCategories{Component<br/>Category?}

    FileCategories -->|Backend Logic| BackendFiles[Modify:<br/>- app.py<br/>- gemma_chat.py<br/>- shelter_locator.py]
    FileCategories -->|Frontend UI| FrontendFiles[Modify:<br/>- map_with_chat.html<br/>- CSS/JavaScript]
    FileCategories -->|Knowledge Base| KnowledgeFiles[Modify:<br/>- first_aid_knowledge.py]
    FileCategories -->|Data Processing| DataFiles[Modify:<br/>- Excel files<br/>- pdf_processor.py]

    BackendFiles --> MakeChanges[Implement Changes]
    FrontendFiles --> MakeChanges
    KnowledgeFiles --> MakeChanges
    DataFiles --> MakeChanges

    MakeChanges --> LocalTest[Local Testing]
    LocalTest --> StartApp[Start Application<br/>python app.py]
    StartApp --> TestBrowser[Test in Browser<br/>localhost:8080]

    TestBrowser --> TestCases{Test<br/>Results?}
    TestCases -->|Pass| CodeReview[Code Review]
    TestCases -->|Fail| Debug[Debug Issues]

    Debug --> CheckLogs[Check Console Logs<br/>Flask output, Browser console]
    CheckLogs --> FixIssue[Fix Identified Issues]
    FixIssue --> LocalTest

    CodeReview --> GitCommit[Git Commit]
    GitCommit --> GitPush[Git Push to Branch<br/>claude/create-app-flowchart-SR9nE]

    GitPush --> CreatePR[Create Pull Request]
    CreatePR --> PRReview{PR<br/>Review?}

    PRReview -->|Approved| MergeMain[Merge to Main Branch]
    PRReview -->|Changes Requested| AddressComments[Address Review Comments]

    AddressComments --> MakeChanges

    MergeMain --> Deploy{Deploy<br/>Type?}
    Deploy -->|Development| DevDeploy[Flask Dev Server<br/>python app.py]
    Deploy -->|Production| ProdDeploy[Production Deployment<br/>Gunicorn + Nginx]

    DevDeploy --> Monitor[Monitor Application]
    ProdDeploy --> Monitor

    Monitor --> End([Feature Complete])

    style Start fill:#90EE90
    style End fill:#90EE90
    style TestCases fill:#FFD700
    style PRReview fill:#FFD700
    style Deploy fill:#FFE4B5
```

---

## 8. Data Flow Diagram

```mermaid
flowchart LR
    subgraph External Sources
        GoogleMaps[Google Maps API<br/>Shelter Data Source]
        OSM[OpenStreetMap<br/>Map Tiles]
        OllamaService[Ollama Service<br/>Gemma 2 Model]
    end

    subgraph Data Ingestion
        GoogleMaps -->|API Call| ShelterLocator[shelter_locator.py]
        ShelterLocator -->|Write Excel| ExcelFile[shelters_downloaded.xlsx]
    end

    subgraph Application Runtime
        ExcelFile -->|Load at Startup| ShelterManager[ShelterManager<br/>In-Memory Data]
        PDFDocs[PDF Documents] -->|Process| PDFProcessor[pdf_processor.py]
        PDFProcessor -->|Generate| VectorDB[vectordb.pkl<br/>faiss.index]

        StaticKnowledge[first_aid_knowledge.py<br/>FIRST_AID_DATA] --> GemmaChat
        VectorDB -->|Optional RAG| GemmaChat[GemmaEmergencyChat]

        ShelterManager --> FlaskAPI[Flask API<br/>app.py]
        GemmaChat --> FlaskAPI
        OllamaService -->|LLM Inference| GemmaChat
    end

    subgraph Frontend
        FlaskAPI -->|JSON Data| JavaScript[JavaScript<br/>Frontend Logic]
        OSM -->|Map Tiles| LeafletMap[Leaflet.js Map]
        JavaScript -->|Render Markers| LeafletMap
        JavaScript -->|Display Messages| ChatUI[Chat Widget]
    end

    subgraph User Interface
        LeafletMap --> Browser[User Browser]
        ChatUI --> Browser
    end

    Browser -->|User Interactions| JavaScript
    JavaScript -->|HTTP Requests| FlaskAPI

    style ExcelFile fill:#FFFACD
    style VectorDB fill:#FFFACD
    style StaticKnowledge fill:#FFFACD
    style Browser fill:#E1F5FF
```

---

## 9. Component Interaction Diagram

```mermaid
graph TB
    subgraph Frontend Components
        MapHTML[map_with_chat.html]
        LeafletJS[Leaflet.js Library]
        ChatWidget[Chat Interface]
        MapDisplay[Map Display]
    end

    subgraph Flask Backend
        AppPy[app.py<br/>Flask Server]
        ShelterMgr[ShelterManager Class]
        Routes[Route Handlers]
    end

    subgraph AI Components
        GemmaChat[gemma_chat.py<br/>GemmaEmergencyChat]
        FirstAid[first_aid_knowledge.py<br/>Knowledge Base]
        PDFProc[pdf_processor.py<br/>RAG System]
    end

    subgraph Data Storage
        ExcelData[shelters_downloaded.xlsx]
        VectorData[Vector Database<br/>FAISS + Pickle]
    end

    subgraph External Services
        OllamaAPI[Ollama API<br/>localhost:11434]
        GoogleAPI[Google Maps API]
        OSMTiles[OpenStreetMap Tiles]
    end

    MapHTML --> LeafletJS
    MapHTML --> ChatWidget
    LeafletJS --> MapDisplay

    MapDisplay <-->|HTTP/JSON| Routes
    ChatWidget <-->|HTTP/JSON| Routes

    Routes --> AppPy
    AppPy --> ShelterMgr
    Routes --> GemmaChat

    ShelterMgr <-->|Read/Write| ExcelData
    GemmaChat --> FirstAid
    GemmaChat --> PDFProc
    GemmaChat --> ShelterMgr

    PDFProc <-->|Read/Write| VectorData
    GemmaChat <-->|API Calls| OllamaAPI
    ShelterMgr <-->|Fetch Shelters| GoogleAPI
    LeafletJS <-->|Load Tiles| OSMTiles

    style MapHTML fill:#E1F5FF
    style AppPy fill:#FFF4E1
    style GemmaChat fill:#FFE1F5
    style ExcelData fill:#FFFACD
    style VectorData fill:#FFFACD
```

---

## Development Quick Reference

### Key Files by Function

| Function | Primary Files | Secondary Files |
|----------|--------------|-----------------|
| **Frontend UI** | `map_with_chat.html` | `index.html`, `medical_info.html` |
| **Backend API** | `app.py` | - |
| **AI Chatbot** | `gemma_chat.py` | `chatbot.py` (deprecated) |
| **Knowledge Base** | `first_aid_knowledge.py` | - |
| **Shelter Management** | `app.py` (ShelterManager) | `shelter_locator.py` |
| **Data Storage** | `shelters_downloaded.xlsx` | `shelters_01.xlsx` |
| **Vector Search** | `pdf_processor.py` | `vectordb.pkl`, `faiss.index` |
| **Map Generation** | `offline_map_plotter.py` | - |

### Common Development Tasks

1. **Add New Medical Knowledge**
   - Edit: `first_aid_knowledge.py`
   - Add entry to `FIRST_AID_DATA` dictionary
   - Restart application

2. **Update Shelter Data**
   - Run: `python shelter_locator.py`
   - Updates: `shelters_downloaded.xlsx`
   - Restart application to reload

3. **Modify Chat Behavior**
   - Edit: `gemma_chat.py`
   - Modify `detect_shelter_query()` or `chat()` method
   - Test with various queries

4. **Change Map Appearance**
   - Edit: `map_with_chat.html`
   - Modify Leaflet initialization
   - Update marker colors/icons

5. **Add New API Endpoint**
   - Edit: `app.py`
   - Add route with `@app.route()`
   - Update frontend to call new endpoint

### Testing Checklist

- [ ] Application starts without errors
- [ ] Map loads with shelter markers
- [ ] User location can be set
- [ ] Chatbot responds to medical queries
- [ ] Shelter search returns nearest locations
- [ ] Distance calculations are accurate
- [ ] Ollama integration works (if available)
- [ ] Vector search works (if enabled)
- [ ] All routes return proper responses
- [ ] CORS is configured correctly

---

## Deployment Flow

```mermaid
flowchart TD
    Start([Code Ready]) --> LocalTest[Local Testing Complete]
    LocalTest --> GitCommit[Git Commit & Push]

    GitCommit --> DeployChoice{Deployment<br/>Environment?}

    DeployChoice -->|Development| DevSetup[Development Setup]
    DeployChoice -->|Production| ProdSetup[Production Setup]

    DevSetup --> DevSteps[1. Set .env variables<br/>2. python app.py<br/>3. Access localhost:8080]
    DevSteps --> DevMonitor[Monitor Flask Console]

    ProdSetup --> ProdSteps[1. Install Gunicorn<br/>2. Configure Nginx<br/>3. Setup SSL HTTPS<br/>4. Configure systemd service]
    ProdSteps --> StartGunicorn[gunicorn -w 4 -b 0.0.0.0:8080 app:app]
    StartGunicorn --> ProdMonitor[Monitor Logs & Metrics]

    DevMonitor --> End([Application Running])
    ProdMonitor --> End

    style Start fill:#90EE90
    style End fill:#90EE90
```

---

## Notes

- All flowcharts use Mermaid syntax for rendering in GitHub and compatible viewers
- Diagrams are organized by functional areas for easy reference
- Color coding indicates different component types:
  - 🟢 Green: Start/End states
  - 🟡 Yellow: Decision points
  - 🔵 Blue: Frontend components
  - 🟠 Orange: Backend components
  - 🟣 Purple: AI/ML components
  - 🟤 Tan: Data storage

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md)
