# Checklist API Automation Framework (Python)

A modular, scalable, and robust Python API Automation Framework built using `pytest`, `requests`, and `pydantic` to validate Checklist services.

---

## 🚀 Scenarios Automated

### **Scenario 1: Authentication Token**
- **Endpoint:** `POST https://dev.api.meradmart.com/iam/authenticate/v1`
- **Credentials:** `username: 4035404`, `password: Dmart@123`
- **Functionality:** Authenticates user via headers and generates a valid JWT Bearer access token.

### **Scenario 2: Get Checklist Items**
- **Endpoint:** `GET https://dev.api.meradmart.com/api/checklist/facade/article/v1?page=1&pageSize=30`
- **Functionality:** Passes Authorization Token, retrieves all checklist article records for the site, and displays the **Total Number of Batches** and **Total Count of Article Codes**.

### **Scenario 3: Full Run Across All Article Codes & Tatkal Triggers (REFILL & PRICEBOARD)**
- **Checklist Endpoint:** `POST https://dev.api.meradmart.com/api/checklist/facade/article/v1`
- **Catalog Endpoint:** `GET https://dev.api.meradmart.com/api/catalog/article/all/v1?pageSize=2000&pageNumber=3&siteId=NDAxMQ%3D%3D`
- **Tatkal API Endpoint:** `POST https://dev.api.meradmart.com/api/tatkal/v1`
- **Functionality:** 
  - **Total Article Count:** Reads the total number of article codes in the checklist (no random picking) and executes all items deterministically.
  - **Catalog Lookup:** Queries Catalog Article All API for target articles to fetch genuine `EAN`, `categoryCode` (`subCategoryCode1` e.g., `4DB`), `caselot`, `sp`, `mrp`, `uom`, and `stockQty`.
  - **Batch 1 (1/3 of total articles):** Compliant on shelf (`is_article_on_shelf: true`, `is_priceboard_sp_compliant: true`). No Tatkal task created.
  - **Batch 2 (1/3 of total articles):** Not on shelf (`is_article_on_shelf: false`). Automatically triggers Tatkal task `taskType = "REFILL"` (`requestedQuantity: 9`, real SP, catalog details).
  - **Batch 3 (Remaining 1/3 of total articles):** Priceboard SP non-compliant (`is_priceboard_sp_compliant: false`, `priceBoards: [{"priceBoard": "A4/20 - Ticket price board", "pbStatus": true}]`). Automatically triggers Tatkal task `taskType = "PRICEBOARD"` (`requestedQuantity: 0`, `sp: "0"`, and `priceBoards: [...]`).
  - **Metrics Printed & Asserted:**
    - `Site ID`: Active Site ID (e.g. `4011`).
    - `Total no of articles count`: Total number of article codes executed.
    - `No of Refill exception`: Count of articles triggering Refill tasks.
    - `No of priceboard exception`: Count of articles triggering Priceboard tasks.




### **Scenario 4: Get All Articles & Display**
- **Endpoint:** `GET https://dev.api.meradmart.com/api/checklist/facade/article/v1?page=1&pageSize=30`
- **Functionality:** Takes the Authorization token, fetches all 510 checklist articles, and displays each article's details (`article_code`, `article_name`, `group`, `sub_group`, `mrp`, `recommended_sp`, `seamless_qty`).

### **Scenario 5: Arrange Articles by Store Rank (Ascending Order) & Display**
- **Endpoint:** `GET https://dev.api.meradmart.com/api/checklist/facade/article/v1?page=1&pageSize=30`
- **Functionality:** Takes all retrieved articles, sorts them in **ascending order by `store_rank`** column, and displays the ordered article list.

---

## 📁 Framework Architecture

```
c:\Automation\Checklist\
├── config/
│   └── config.py               # Central environment variables & endpoint configuration
├── utils/
│   ├── api_client.py           # Custom REST API client wrapper with request/response logging
│   └── logger.py               # Logging configuration (Console & file logger)
├── models/
│   └── article_model.py        # Pydantic schemas for Auth & Article API payloads
├── services/
│   ├── auth_service.py         # Service layer for Scenario 1 (IAM Authentication)
│   └── checklist_service.py    # Service layer for Scenarios 2, 3, 4 & 5 (Checklist operations)
├── tests/
│   ├── conftest.py             # Pytest fixtures (api_client, auth_token, services)
│   ├── test_scenario1_auth.py  # Pytest test for Scenario 1
│   ├── test_scenario2_get_checklist.py # Pytest test for Scenario 2
│   ├── test_scenario3_update_article.py # Pytest test for Scenario 3
│   ├── test_scenario4_get_all_articles.py # Pytest test for Scenario 4
│   └── test_scenario5_sequence_sort.py # Pytest test for Scenario 5
├── main.py                     # Standalone CLI execution script
├── pytest.ini                  # Pytest configuration & HTML reporting settings
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation guide
```

---

## 🏃 Execution Commands

### **Option 1: Run All Scenarios via CLI Script**
Executes all 5 scenarios sequentially:
```bash
python main.py
```

### **Option 2: Run All Scenarios via Pytest**
Executes pytest suite and generates an HTML test report at `reports/report.html`:
```bash
pytest
```

### **Option 3: Run Specific Scenario**
```bash
pytest -m scenario1    # Run Scenario 1
pytest -m scenario2    # Run Scenario 2
pytest -m scenario3    # Run Scenario 3
pytest -m scenario4    # Run Scenario 4
pytest -m scenario5    # Run Scenario 5
```
