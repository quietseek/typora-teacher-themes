"""Build standalone Typora themes and an offline/GitHub Pages preview."""
from pathlib import Path
import argparse
import importlib.util
import json
import markdown

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('palettes', ROOT / 'src/palettes.py')
palettes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(palettes)
PALETTES = palettes.PALETTES

LAYOUTS = {
    '备课': ':root { --qm-size: 16px; --qm-leading: 1.85; --qm-section: 1.8em; }',
    '讲义': ':root { --qm-body: "SimSun", "Songti SC", "Noto Serif CJK SC", serif; --qm-size: 17px; --qm-leading: 1.8; --qm-paragraph: .65em; --qm-section: 1.6em; }',
    '作业': ':root { --qm-size: 16px; --qm-leading: 1.7; --qm-paragraph: .55em; --qm-section: 1.4em; --qm-print-leading: 1.55; }',
}


def generated_files():
    base = (ROOT / 'src/base.css').read_text(encoding='utf-8')
    files = {}
    for palette in PALETTES:
        for mode, layout in LAYOUTS.items():
            files[f'themes/{palette["name"]}{mode}.css'] = base.replace(
                '/* VARIANT */', layout + '\n' + palettes.palette_css(palette))
    for mode, layout in LAYOUTS.items():
        # Keep the original Qingmo filenames compatible with existing installations.
        if mode == '作业':
            layout = layout[:-2] + '--qm-accent: #354a45; --qm-tint: #f4f6f5; }'
        files[f'themes/青墨{mode}.css'] = base.replace('/* VARIANT */', layout)

    sections = [markdown.markdown((ROOT / 'examples' / f'{name}.md').read_text(encoding='utf-8'),
                extensions=['tables', 'fenced_code', 'footnotes', 'sane_lists'])
                for name in ['lesson', 'handout', 'worksheet']]
    buttons = ''.join(
        f'<button type="button" data-palette="{i}" aria-pressed="false">'
        f'<span class="swatch" style="--swatch:{p["accent"]}" aria-hidden="true"></span>{p["name"]}</button>'
        for i, p in enumerate(PALETTES))
    html = (ROOT / 'src/preview.html').read_text(encoding='utf-8')
    html = html.replace('__PALETTE_BUTTONS__', buttons)
    html = html.replace('__PAGES__', json.dumps(sections, ensure_ascii=False).replace('</script', '<\\/script'))
    files['index.html'] = html.replace('__PALETTES__', json.dumps(PALETTES, ensure_ascii=False))
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if committed generated files are stale.')
    args = parser.parse_args()
    expected = generated_files()
    stale = []
    for filename, content in expected.items():
        path = ROOT / filename
        if args.check:
            if not path.is_file() or path.read_text(encoding='utf-8') != content:
                stale.append(filename)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8', newline='\n')
    extra = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'themes').glob('*.css')} - set(expected)
    if stale or extra:
        raise SystemExit('Generated files differ; run python scripts/build.py:\n' + '\n'.join(stale + sorted(extra)))
    print(f'{"Checked" if args.check else "Built"} 18 themes and index.html.')


if __name__ == '__main__':
    main()
