#!/usr/bin/env python3
"""
Main Execution Script for Checklist API Automation Framework.
Executes Scenario 1, Scenario 2, Scenario 3, Scenario 4, and Scenario 5 sequentially.
"""

import sys
import json

# Force UTF-8 output encoding for Windows terminal compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from utils.logger import logger
from utils.api_client import APIClient
from services.auth_service import AuthService
from services.checklist_service import ChecklistService

def run_all_scenarios():
    print("=" * 70)
    print("      CHECKLIST API AUTOMATION FRAMEWORK - SCENARIO EXECUTION")
    print("=" * 70)

    api_client = APIClient()
    auth_service = AuthService(api_client=api_client)
    checklist_service = ChecklistService(api_client=api_client)

    # -------------------------------------------------------------------------
    # SCENARIO 1: Authentication Token
    # -------------------------------------------------------------------------
    print("\n[STEP 1/5] Executing Scenario 1: Authentication Token...")
    try:
        token = auth_service.get_auth_token()
        print("[SUCCESS] SCENARIO 1 PASSED: Auth Token generated successfully!")
        print(f"  Token Preview: {token[:40]}...")
    except Exception as e:
        print(f"[FAILED] SCENARIO 1 FAILED: {e}")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # SCENARIO 2: Get all checklist items for the site
    # -------------------------------------------------------------------------
    print("\n[STEP 2/5] Executing Scenario 2: Get Checklist Items...")
    try:
        total_records, items, raw_res, site_id = checklist_service.get_all_checklist_items(token=token, page=1, page_size=30)
        print("[SUCCESS] SCENARIO 2 PASSED: Checklist items fetched successfully!")
        print("--------------------------------------------------")
        print(f"  SITE ID                 : {site_id}")
        print(f"  TOTAL NUMBER OF RECORDS : {total_records}")
        print("--------------------------------------------------")
    except Exception as e:
        print(f"[FAILED] SCENARIO 2 FAILED: {e}")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # SCENARIO 3: Update First 10 Articles (True) & Next 10 Articles (False + Tatkal API)
    # -------------------------------------------------------------------------
    print("\n[STEP 3/5] Executing Scenario 3: Update ALL Articles (Compliant, Refill, Priceboard) Based on Total Count...")
    try:
        s3_res = checklist_service.update_articles_scenario3(token=token)
        print("[SUCCESS] SCENARIO 3 PASSED!")
        print("-----------------------------------------------------------------------------------------------------------------------------")
        print(f"  SITE ID                                : {s3_res.get('site_id')}")
        print(f"  TOTAL NO OF ARTICLES COUNT             : {s3_res.get('total_no_of_articles_count')}")
        print(f"  NO OF REFILL EXCEPTION                 : {s3_res.get('no_of_refill_exception')}")
        print(f"  NO OF PRICEBOARD EXCEPTION             : {s3_res.get('no_of_priceboard_exception')}")
        print(f"  BATCH 1: COMPLIANT ARTICLES (ON SHELF) : {len(s3_res['compliant_articles'])}")
        print(f"  BATCH 2: REFILL ARTICLES (OFF SHELF)   : {len(s3_res['refill_articles'])}")
        print(f"  BATCH 3: PRICEBOARD ARTICLES (SP NON-C): {len(s3_res['priceboard_articles'])}")
        print(f"  TATKAL REFILL TASKS CREATED (OPEN)     : {len(s3_res['tatkal_refill_records'])}")
        print(f"  TATKAL PRICEBOARD TASKS CREATED (OPEN) : {len(s3_res['tatkal_priceboard_records'])}")
        print("-----------------------------------------------------------------------------------------------------------------------------")
        print("BATCH 2: TATKAL REFILL TASKS (is_article_on_shelf = False):")
        print(f"  {'#':<4} | {'Article Code':<12} | {'EAN (Catalog)':<15} | {'Category Code':<15} | {'Tatkal Task ID':<38} | {'Status'}")
        print("-----------------------------------------------------------------------------------------------------------------------------")
        for idx, rec in enumerate(s3_res['tatkal_refill_records'], start=1):
            resp = rec.get("response", [])
            t_id = resp[0].get("taskId", "N/A") if isinstance(resp, list) and resp else "N/A"
            t_st = resp[0].get("Status", "OPEN") if isinstance(resp, list) and resp else "Created"
            print(f"  {idx:<4} | {rec.get('article_code'):<12} | {str(rec.get('ean')):<15} | {str(rec.get('categoryCode')):<15} | {t_id:<38} | {t_st}")
        print("-----------------------------------------------------------------------------------------------------------------------------")
        print("BATCH 3: TATKAL PRICEBOARD TASKS (is_priceboard_sp_compliant = False):")
        print(f"  {'#':<4} | {'Article Code':<12} | {'EAN (Catalog)':<15} | {'Price Board Name':<28} | {'Tatkal Task ID':<38} | {'Status'}")
        print("-----------------------------------------------------------------------------------------------------------------------------")
        for idx, pb_rec in enumerate(s3_res['tatkal_priceboard_records'], start=1):
            resp = pb_rec.get("response", [])
            t_id = resp[0].get("taskId", "N/A") if isinstance(resp, list) and resp else "N/A"
            t_st = resp[0].get("Status", "OPEN") if isinstance(resp, list) and resp else "Created"
            pb_list = pb_rec.get("priceBoards", [])
            pb_name = pb_list[0].get("priceBoard", "A4/20 - Ticket price board") if pb_list else "A4/20"
            print(f"  {idx:<4} | {pb_rec.get('article_code'):<12} | {str(pb_rec.get('ean')):<15} | {pb_name:<28} | {t_id:<38} | {t_st}")
        print("-----------------------------------------------------------------------------------------------------------------------------")



    except Exception as e:
        print(f"[FAILED] SCENARIO 3 FAILED: {e}")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # SCENARIO 4: Get all articles and display
    # -------------------------------------------------------------------------
    print("\n[STEP 4/5] Executing Scenario 4: Get All Articles and Display...")
    try:
        all_articles = checklist_service.get_all_articles_detail(token=token, page=1, page_size=30)
        print("[SUCCESS] SCENARIO 4 PASSED: All articles retrieved successfully!")
        print("--------------------------------------------------")
        print(f"  TOTAL ARTICLES DISPLAYED : {len(all_articles)}")
        print("--------------------------------------------------")
        for idx, art in enumerate(all_articles, start=1):
            code = art.get("article_code", "N/A")
            name = art.get("article_name", "N/A")
            print(f"\n  --- [{idx:03d}/{len(all_articles)}] Code: {code} | Name: {name} ---")
            for key, val in art.items():
                print(f"    {key:<22} : {val}")
        print("\n--------------------------------------------------")
    except Exception as e:
        print(f"[FAILED] SCENARIO 4 FAILED: {e}")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # SCENARIO 5: Arrange all articles by store_rank (ascending order) & display
    # -------------------------------------------------------------------------
    print("\n[STEP 5/5] Executing Scenario 5: Get All Articles, Arrange by store_rank (Ascending Order) & Display All Items...")
    try:
        sorted_articles = checklist_service.get_articles_sorted_by_store_rank(token=token, page=1, page_size=30)
        print("[SUCCESS] SCENARIO 5 PASSED: Articles arranged by store_rank ascending successfully!")
        print("--------------------------------------------------")
        print(f"  TOTAL SORTED ARTICLES DISPLAYED : {len(sorted_articles)}")
        print("--------------------------------------------------")
        for idx, art in enumerate(sorted_articles, start=1):
            rank = art.get("store_rank", "N/A")
            code = art.get("article_code", "N/A")
            name = art.get("article_name", "N/A")
            print(f"\n  --- Article [{idx:03d}/{len(sorted_articles)}] Store Rank: {rank} | Code: {code} | Name: {name} ---")
            for k, v in art.items():
                print(f"    {k:<22} : {v}")
        print("--------------------------------------------------")
    except Exception as e:
        print(f"[FAILED] SCENARIO 5 FAILED: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("      ALL 5 SCENARIOS EXECUTED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_all_scenarios()
