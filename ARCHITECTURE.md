# Invoice Command Studio - Architecture

## System Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        MW[Main Window]
        CB[Command Bar]
        IL[Invoice List Panel]
        ID[Invoice Detail Panel]
    end
    
    subgraph "Business Logic Layer"
        CP[Command Parser]
        CE[Command Executor]
        IM[Invoice Model]
        VAL[Validators]
        FMT[Formatters]
    end
    
    subgraph "Data Access Layer"
        DBM[Database Manager]
        TH[Template Handler]
        MC[Mapping Config]
    end
    
    subgraph "Storage"
        DB[(SQLite Database)]
        TMPL[Excel Template]
        CFG[JSON Config]
        OUT[Output Files]
    end
    
    MW --> CB
    MW --> IL
    MW --> ID
    
    CB --> CP
    CP --> CE
    CE --> IM
    CE --> DBM
    
    ID --> IM
    ID --> VAL
    ID --> FMT
    
    IL --> DBM
    
    IM --> VAL
    IM --> FMT
    
    DBM --> DB
    TH --> TMPL
    TH --> MC
    MC --> CFG
    
    CE --> TH
    ID --> TH
    TH --> OUT
    
    style MW fill:#e1f5ff
    style CB fill:#e1f5ff
    style IL fill:#e1f5ff
    style ID fill:#e1f5ff
    
    style CP fill:#fff4e1
    style CE fill:#fff4e1
    style IM fill:#fff4e1
    style VAL fill:#fff4e1
    style FMT fill:#fff4e1
    
    style DBM fill:#e8f5e9
    style TH fill:#e8f5e9
    style MC fill:#e8f5e9
    
    style DB fill:#f3e5f5
    style TMPL fill:#f3e5f5
    style CFG fill:#f3e5f5
    style OUT fill:#f3e5f5
```

## Component Interaction Flow

### 1. Command Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant CommandBar
    participant Parser
    participant Executor
    participant Database
    participant DetailPanel
    
    User->>CommandBar: Enter command
    CommandBar->>Parser: Parse command string
    Parser->>Parser: Extract type & parameters
    Parser-->>CommandBar: Parsed command dict
    CommandBar->>Executor: Execute command
    Executor->>Database: Query/Insert data
    Database-->>Executor: Result
    Executor->>DetailPanel: Load invoice
    DetailPanel-->>User: Display invoice
    Executor-->>CommandBar: Success message
    CommandBar-->>User: Show result
```

### 2. Excel Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant DetailPanel
    participant Invoice
    participant TemplateHandler
    participant Excel
    participant FileSystem
    
    User->>DetailPanel: Click "Generate Excel"
    DetailPanel->>Invoice: Get invoice data
    Invoice->>Invoice: Validate
    Invoice-->>DetailPanel: Valid invoice
    DetailPanel->>TemplateHandler: Generate invoice
    TemplateHandler->>Excel: Load template
    TemplateHandler->>Excel: Fill data
    TemplateHandler->>Excel: Apply formatting
    TemplateHandler->>FileSystem: Save file
    FileSystem-->>TemplateHandler: File path
    TemplateHandler-->>DetailPanel: Success
    DetailPanel-->>User: Show success dialog
```

### 3. Invoice Save Flow

```mermaid
sequenceDiagram
    participant User
    participant DetailPanel
    participant Invoice
    participant Validator
    participant Database
    
    User->>DetailPanel: Click "Save"
    DetailPanel->>Invoice: Get form data
    Invoice->>Invoice: Calculate totals
    Invoice->>Validator: Validate data
    Validator-->>Invoice: Valid
    Invoice-->>DetailPanel: Invoice object
    DetailPanel->>Database: Save invoice
    Database->>Database: Insert/Update
    Database-->>DetailPanel: Invoice ID
    DetailPanel-->>User: Success message
```

## Data Model

```mermaid
erDiagram
    INVOICES ||--o{ INVOICE_ITEMS : contains
    INVOICES }o--|| CUSTOMERS : "billed to"
    INVOICE_ITEMS }o--|| ITEMS : references
    
    INVOICES {
        int id PK
        string invoice_no UK
        date date
        string type
        int customer_id FK
        string customer_name
        string currency
        float subtotal
        float vat
        float total
        string file_path
        text notes
        datetime created_at
        datetime updated_at
    }
    
    CUSTOMERS {
        int id PK
        string name UK
        string contact_person
        string address
        string email
        string phone
        datetime created_at
        datetime updated_at
    }
    
    ITEMS {
        int id PK
        string name UK
        string description
        float default_price
        string unit
        datetime created_at
        datetime updated_at
    }
    
    INVOICE_ITEMS {
        int id PK
        int invoice_id FK
        int item_id FK
        string description
        float quantity
        float unit_price
        float amount
        int line_order
    }
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **GUI Framework** | PySide6 (Qt6) | Native Windows interface |
| **Database** | SQLite3 | Lightweight data storage |
| **Excel Processing** | openpyxl | Read/write .xlsx files |
| **PDF Generation** | reportlab | Future PDF export |
| **Language** | Python 3.11+ | Application logic |
| **Style** | Fusion | Modern Qt style |

## Design Patterns Used

1. **MVC (Model-View-Controller)**
   - Models: `Invoice`, `Customer`, `Item`
   - Views: GUI widgets (`MainWindow`, panels)
   - Controllers: `CommandExecutor`, `DatabaseManager`

2. **Singleton**
   - `CommandParser` instance
   - `DatabaseManager` connection

3. **Observer (Signal/Slot)**
   - Qt signals for component communication
   - Event-driven architecture

4. **Strategy**
   - Different VAT calculation strategies for Tax/Normal invoices

5. **Template Method**
   - Excel template filling process

## File Organization

```
invoice_studio/
├── database/          # Data persistence
├── commands/          # Command processing
├── excel/            # Excel operations
├── gui/              # User interface
├── models/           # Business entities
└── utils/            # Helper functions
```

Each module has clear responsibilities and minimal coupling.
