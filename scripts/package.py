"""Package an installable ZIP and a minimal GitHub Pages site."""
from pathlib import Path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED
from build import ROOT, generated_files


def main():
    for name, expected in generated_files().items():
        if not (ROOT / name).is_file() or (ROOT / name).read_text(encoding='utf-8') != expected:
            raise SystemExit('Run python scripts/build.py before packaging.')
    dist = ROOT / 'dist'
    site = dist / 'site'
    site.mkdir(parents=True, exist_ok=True)
    files = [ROOT / name for name in ['README.md', 'LICENSE', 'index.html']]
    for folder in ['themes', 'templates', 'examples', 'docs']:
        files.extend(sorted(p for p in (ROOT / folder).rglob('*') if p.is_file()))
    archive = dist / 'typora-teacher-themes.zip'
    with ZipFile(archive, 'w', ZIP_DEFLATED) as z:
        for path in files:
            z.write(path, Path('typora-teacher-themes') / path.relative_to(ROOT))
    # This allowlist keeps teacher answers and development files out of the website.
    shutil.copy2(ROOT / 'index.html', site / 'index.html')
    (site / 'themes').mkdir(exist_ok=True)
    for path in (ROOT / 'themes').glob('*.css'):
        shutil.copy2(path, site / 'themes' / path.name)
    (site / '.nojekyll').write_text('', encoding='utf-8')
    print(f'Packaged {len(files)} files: {archive.name}; Pages site: dist/site/')


if __name__ == '__main__':
    main()
