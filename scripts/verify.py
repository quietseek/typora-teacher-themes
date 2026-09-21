"""Check theme switching, responsive layout and the printed table-border regression."""
from pathlib import Path
import shutil
import subprocess
from PIL import Image
from playwright.sync_api import sync_playwright
import tinycss2
from build import ROOT, PALETTES

ARTIFACTS = ROOT / 'artifacts'
ARTIFACTS.mkdir(exist_ok=True)


def edge_ratio(pdf, dpi):
    prefix = ARTIFACTS / f'{pdf.stem}-{dpi}'
    subprocess.run(['pdftoppm', '-f', '1', '-singlefile', '-r', str(dpi), '-png',
                    str(pdf), str(prefix)], check=True, capture_output=True)
    with Image.open(prefix.with_suffix('.png')).convert('L') as im:
        w, h = im.size
        # The isolated A4 fixture has a 17mm margin and three 12mm data rows.
        # Sample inside the table, independent of Chinese font metrics.
        y0, y1 = round(h * 35 / 297), round(h * 55 / 297)
        radius = max(4, round(w * 4 / 1240))
        def ink(center):
            return sum(max(255-im.getpixel((x, y)) for x in range(center-radius, center+radius+1))
                       for y in range(y0, y1))/(y1-y0)
        left, right = ink(round(w*17/210)), ink(round(w*193/210))
        assert left > 50, 'Fixture must contain a visible left table edge.'
        return right/left


def main():
    if not shutil.which('pdftoppm'):
        raise SystemExit('Install Poppler and put pdftoppm on PATH; see README.md.')
    files = list((ROOT / 'themes').glob('*.css'))
    assert len(files) == 18
    for path in files:
        rules = tinycss2.parse_stylesheet(path.read_text(encoding='utf-8'), skip_comments=True, skip_whitespace=True)
        assert not [r for r in rules if r.type == 'error'], path.name
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1100})
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto((ROOT / 'index.html').as_uri())
        try:
            for palette in PALETTES:
                page.get_by_role('button', name=palette['name'], exact=True).click()
                for mode_index, mode in enumerate(['备课', '讲义', '作业']):
                    page.get_by_role('button', name=mode, exact=True).click()
                    page.wait_for_function('''([accent, leading]) => {
                      const s = getComputedStyle(document.documentElement);
                      return s.getPropertyValue('--qm-accent').trim() === accent &&
                             s.getPropertyValue('--qm-leading').trim() === leading;
                    }''', arg=[palette['accent'], ['1.85', '1.8', '1.7'][mode_index]])
                    page.set_viewport_size({'width': 390, 'height': 844})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (palette['name'], mode)
                    page.set_viewport_size({'width': 1440, 'height': 1100})
            assert not errors, errors
            page.screenshot(path=str(ARTIFACTS / 'preview.png'))

            fixture = ARTIFACTS / 'border.html'
            fixture.write_text('''<!doctype html><html><head><meta charset="utf-8">
            <link rel="stylesheet" href="../themes/雾蓝作业.css">
            <style>body{margin:0}#write td{height:12mm}</style></head><body>
            <main id="write"><table><thead><tr><th>Group</th><th>Value</th></tr></thead>
            <tbody><tr><td>A</td><td>1</td></tr><tr><td>B</td><td>2</td></tr>
            <tr><td>C</td><td>3</td></tr></tbody></table></main></body></html>''', encoding='utf-8')
            page.goto(fixture.as_uri())
            fixed = ARTIFACTS / 'border-fixed.pdf'
            page.pdf(path=str(fixed), prefer_css_page_size=True, print_background=False)
            for dpi in [150, 300]:
                ratio = edge_ratio(fixed, dpi)
                assert .8 <= ratio <= 1.25, f'Clipped right border at {dpi} DPI: ratio={ratio:.3f}'
                print(f'PASS print edge at {dpi} DPI: right/left darkness={ratio:.3f}')
            # Demonstrate that the test rejects the historical full-width bug.
            page.add_style_tag(content='@media print {#write table {width:100%;max-width:100%;}}')
            old = ARTIFACTS / 'border-old-full-width.pdf'
            page.pdf(path=str(old), prefer_css_page_size=True, print_background=False)
            old_ratio = edge_ratio(old, 150)
            assert old_ratio < .8, f'Regression fixture did not reproduce clipping: {old_ratio:.3f}'
            print(f'PASS regression sensitivity: old right/left darkness={old_ratio:.3f}')
        except Exception:
            page.screenshot(path=str(ARTIFACTS / 'failure.png'), full_page=True)
            raise
        finally:
            browser.close()
    print('PASS 18 CSS files; 15 palette/layout combinations; 390px viewport; print regression.')


if __name__ == '__main__':
    main()
