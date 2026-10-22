"""Capture crisp, high-resolution screenshots for each of the 5 supply-chain entities in AnnaSutra.
Uses Playwright with local Chrome browser at 2x device scale factor.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGET_URL = "https://annasutra.vercel.app"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def run_capture():
    print(f"Connecting to {TARGET_URL} via Chrome at {CHROME_PATH}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 960},
            device_scale_factor=2
        )
        page = context.new_page()
        
        # 1. Load Homepage
        print("Loading homepage...")
        page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
        time.sleep(2)

        # 2. Capture 5-Tier Supply Chain Flow Showcase
        print("Capturing 01_flow_showcase.png...")
        flow_sec = page.locator("#flowShowcaseSection")
        if flow_sec.count() > 0:
            flow_sec.scroll_into_view_if_needed()
            time.sleep(1)
            flow_sec.screenshot(path=os.path.join(OUTPUT_DIR, "01_flow_showcase.png"))
        
        # 3. Capture Universal Entity Portal Selection Modal
        print("Capturing 02_entity_portal_modal.png...")
        page.evaluate("if(window.openEntityPortalModal) window.openEntityPortalModal();")
        time.sleep(1)
        portal_modal = page.locator("#entityPortalModal .portal-modal-box")
        if portal_modal.count() > 0:
            portal_modal.screenshot(path=os.path.join(OUTPUT_DIR, "02_entity_portal_modal.png"))
        page.evaluate("if(window.closeEntityPortalModal) window.closeEntityPortalModal();")
        time.sleep(0.5)

        # 4. Capture 5 Entity Consoles from the Live Simulator
        entities = [
            ("PRODUCER", "03_producer_console.png"),
            ("AGGREGATOR", "04_aggregator_console.png"),
            ("WHOLESALER", "05_wholesaler_console.png"),
            ("DISTRIBUTOR", "06_distributor_console.png"),
            ("RETAILER", "07_retailer_console.png"),
        ]

        dash_wrap = page.locator("#entityDashPreviewWrap")
        if dash_wrap.count() > 0:
            dash_wrap.scroll_into_view_if_needed()
            time.sleep(1)
            for role, filename in entities:
                print(f"Capturing simulator for {role} -> {filename}...")
                page.evaluate(f"if(window.switchPreviewEntity) window.switchPreviewEntity('{role}');")
                time.sleep(1)
                dash_wrap.screenshot(path=os.path.join(OUTPUT_DIR, filename))

        # 5. Capture Entity Login Modal (Official OTP Dispatch Step)
        print("Capturing 08_producer_login_modal.png...")
        page.evaluate("if(window.openLoginModal) window.openLoginModal('PRODUCER');")
        time.sleep(1)
        login_box = page.locator("#loginModal .modal-box")
        if login_box.count() > 0:
            login_box.screenshot(path=os.path.join(OUTPUT_DIR, "08_producer_login_modal.png"))
        page.evaluate("if(window.closeLoginModal) window.closeLoginModal();")
        time.sleep(0.5)

        # 6. Capture Verified Produce Lot Timeline (Sample Lot 7K3Q9XMD4T2B)
        print("Capturing 09_lot_summary_timeline.png...")
        try:
            page.goto(f"{TARGET_URL}/?code=7K3Q9XMD4T2B", wait_until="networkidle", timeout=20000)
            time.sleep(2)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "09_lot_summary_timeline.png"), full_page=True)
        except Exception as e:
            print("Notice on lot summary capture:", e)

        browser.close()
        print("All screenshots successfully captured in:", OUTPUT_DIR)

if __name__ == "__main__":
    run_capture()
