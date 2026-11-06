from playwright.sync_api import sync_playwright

def test_ui_add_task():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://127.0.0.1:8000")
        page.fill("#taskTitle", "UI Тест")
        page.click("text=Добавить")
        page.wait_for_selector("text=UI Тест")
        assert "UI Тест" in page.content()
        browser.close()