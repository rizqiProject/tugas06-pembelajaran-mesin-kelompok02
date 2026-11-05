"""Tangkapan layar dari aplikasi Streamlit yang benar-benar berjalan."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent;out=ROOT/'evidence/screenshots';out.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1380,'height':1150},device_scale_factor=1.5,locale='id-ID')
    page.goto('http://127.0.0.1:8505',wait_until='networkidle',timeout=60000)
    page.get_by_role('button',name='Periksa risiko',exact=True).wait_for(timeout=60000)
    page.screenshot(path=str(out/'ui_form_full.png'),full_page=True)
    # Dua kolom terluar berisi form dan hasil; tangkapan per kolom menjaga keterbacaan.
    columns=page.locator('[data-testid="stHorizontalBlock"]').first.locator(':scope > [data-testid="stColumn"]')
    if columns.count()<2:raise RuntimeError('Dua kolom aplikasi tidak ditemukan.')
    columns.nth(0).screenshot(path=str(out/'ui_form.png'))
    page.get_by_role('button',name='Periksa risiko',exact=True).click()
    page.get_by_text('18.75%',exact=True).wait_for(timeout=60000)
    page.get_by_text('Fitur yang membentuk skor',exact=True).wait_for(timeout=60000)
    columns.nth(1).screenshot(path=str(out/'ui_result.png'))
    page.screenshot(path=str(out/'ui_result_full.png'),full_page=True)
    result_text=columns.nth(1).inner_text()
    slider=page.get_by_role('slider').first
    slider.focus();slider.press('Home')
    for _ in range(24):slider.press('ArrowRight')
    page.get_by_role('button',name='Periksa risiko',exact=True).click()
    page.get_by_text('Tidak terpicu alarm',exact=True).wait_for(timeout=30000)
    columns.nth(1).screenshot(path=str(out/'ui_threshold_025.png'))
    page.get_by_role('textbox',name='ID berkas',exact=True).fill('')
    page.get_by_role('button',name='Periksa risiko',exact=True).click()
    page.get_by_text('Masukan belum dapat diproses. Periksa ID, tanggal, angka, dan format histori.',exact=True).wait_for(timeout=30000)
    columns.nth(0).screenshot(path=str(out/'ui_validation.png'))
    (out/'capture_metadata.json').write_text(json.dumps({'browser':browser.version,'source_url':'http://127.0.0.1:8505',
        'actual_browser_capture':True,'viewport':{'width':1380,'height':1150},'device_scale_factor':1.5,
        'case_id':'BRK_0024','score':.1875,'initial_threshold':.11,'changed_threshold':.25,
        'dynamic_threshold_ui_verified':True,'invalid_id_ui_verified':True,'result_text':result_text},indent=2,ensure_ascii=False))
    browser.close()
print(out)
