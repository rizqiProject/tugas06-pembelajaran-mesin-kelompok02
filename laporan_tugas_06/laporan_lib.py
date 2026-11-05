"""Helper pembentuk dokumen laporan Tugas 06 (python-docx)."""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

BIRU = RGBColor(0x1F, 0x38, 0x64)
ABU = RGBColor(0x59, 0x59, 0x59)
HITAM = RGBColor(0x1A, 0x1A, 0x1A)


def f(x, n=3):
    """Angka desimal dengan koma Indonesia."""
    return f"{float(x):.{n}f}".replace('.', ',')


def pct(x, n=1):
    return f"{100 * float(x):.{n}f}".replace('.', ',') + '%'


def n(x):
    return f"{int(round(float(x))):,}".replace(',', '.')


class Laporan:
    def __init__(self, template: Path):
        self.doc = Document(str(template))
        self._bersihkan()
        self._gaya()
        self._header_footer()

    # ------------------------------------------------------------------
    def _bersihkan(self):
        body = self.doc.element.body
        for child in list(body):
            if child.tag == qn('w:sectPr'):
                continue
            body.remove(child)

    def _gaya(self):
        styles = self.doc.styles
        normal = styles['Normal']
        normal.font.name = 'Calibri'
        normal.font.size = Pt(11)
        normal.font.color.rgb = HITAM
        normal.paragraph_format.space_after = Pt(6)
        normal.paragraph_format.line_spacing = 1.15
        normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        rpr = normal.element.get_or_add_rPr()
        rfonts = rpr.get_or_add_rFonts()
        rfonts.set(qn('w:eastAsia'), 'Calibri')

        for nama, ukuran in [('Heading 1', 14), ('Heading 2', 12),
                             ('Heading 3', 11)]:
            st = styles[nama]
            st.font.name = 'Calibri'
            st.font.size = Pt(ukuran)
            st.font.bold = True
            st.font.color.rgb = BIRU
            st.paragraph_format.space_before = Pt(12)
            st.paragraph_format.space_after = Pt(6)
            st.paragraph_format.keep_with_next = True
            st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

        for nama in ['List Bullet', 'List Number']:
            st = styles[nama]
            st.font.name = 'Calibri'
            st.font.size = Pt(11)
            st.paragraph_format.space_after = Pt(3)

    def _header_footer(self):
        for section in self.doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            section.different_first_page_header_footer = True
            for hf in (section.first_page_header, section.first_page_footer):
                hf.is_linked_to_previous = False
                for p in hf.paragraphs:
                    for r in list(p.runs):
                        r._element.getparent().remove(r._element)
            header = section.header
            header.is_linked_to_previous = False
            hp = header.paragraphs[0]
            hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            hr = hp.add_run('Tugas 06 — Kelompok 02 — Kantor Notaris & PPAT Aries Buwana')
            hr.font.size = Pt(8)
            hr.font.color.rgb = ABU

            footer = section.footer
            footer.is_linked_to_previous = False
            fp = footer.paragraphs[0]
            fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            fr = fp.add_run('Pembelajaran Mesin | Semester Gasal 2026/2027  |  Halaman ')
            fr.font.size = Pt(8)
            fr.font.color.rgb = ABU
            self._nomor_halaman(fp)

    def _nomor_halaman(self, paragraph):
        run = paragraph.add_run()
        run.font.size = Pt(8)
        run.font.color.rgb = ABU
        for tipe, teks in [('begin', None), ('instr', ' PAGE '), ('separate', None),
                           ('text', '1'), ('end', None)]:
            if tipe == 'instr':
                el = OxmlElement('w:instrText')
                el.set(qn('xml:space'), 'preserve')
                el.text = teks
            elif tipe == 'text':
                el = OxmlElement('w:t')
                el.text = teks
            else:
                el = OxmlElement('w:fldChar')
                el.set(qn('w:fldCharType'), tipe)
            run._r.append(el)

    # ------------------------------------------------------------------
    def judul(self, teks, ukuran=18, space_before=0, space_after=6):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        r = p.add_run(teks)
        r.bold = True
        r.font.size = Pt(ukuran)
        r.font.color.rgb = BIRU
        return p

    def subjudul(self, teks, ukuran=12, italic=False, space_after=6):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(space_after)
        r = p.add_run(teks)
        r.font.size = Pt(ukuran)
        r.italic = italic
        return p

    def h1(self, teks):
        return self.doc.add_heading(teks, level=1)

    def h2(self, teks):
        return self.doc.add_heading(teks, level=2)

    def h3(self, teks):
        return self.doc.add_heading(teks, level=3)

    def par(self, teks, bold=False, italic=False, ukuran=None, rata='justify',
            space_after=6, indent=None, keep=False):
        p = self.doc.add_paragraph()
        p.alignment = {'justify': WD_ALIGN_PARAGRAPH.JUSTIFY,
                       'left': WD_ALIGN_PARAGRAPH.LEFT,
                       'center': WD_ALIGN_PARAGRAPH.CENTER,
                       'right': WD_ALIGN_PARAGRAPH.RIGHT}[rata]
        p.paragraph_format.space_after = Pt(space_after)
        if indent is not None:
            p.paragraph_format.first_line_indent = Inches(indent)
        if keep:
            p.paragraph_format.keep_with_next = True
        r = p.add_run(teks)
        r.bold = bold
        r.italic = italic
        if ukuran:
            r.font.size = Pt(ukuran)
        return p

    def lead(self, awal, sisa, space_after=6):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(space_after)
        r = p.add_run(awal)
        r.bold = True
        p.add_run(sisa)
        return p

    def bullet(self, teks, space_after=3):
        p = self.doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(space_after)
        p.add_run(teks)
        return p

    def nomor(self, nomor, teks, space_after=3):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.22)
        p.paragraph_format.space_after = Pt(space_after)
        awalan = f'{nomor} ' if str(nomor).startswith('[') else f'{nomor}. '
        p.add_run(awalan).bold = True
        p.add_run(teks)
        return p

    def rumus(self, teks):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(teks)
        r.italic = True
        r.font.name = 'Cambria Math'
        r.font.size = Pt(11)
        return p

    def kode(self, teks):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.0
        shd = OxmlElement('w:shd')
        shd.set(qn('w:fill'), 'F2F2F2')
        p._p.get_or_add_pPr().append(shd)
        for i, baris in enumerate(teks.split('\n')):
            if i:
                p.add_run().add_break()
            r = p.add_run(baris)
            r.font.name = 'Consolas'
            r.font.size = Pt(8)
            r._element.rPr.rFonts.set(qn('w:eastAsia'), 'Consolas')
        return p

    def caption(self, teks, atas=False):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2 if not atas else 6)
        p.paragraph_format.space_after = Pt(8 if not atas else 3)
        p.paragraph_format.keep_with_next = bool(atas)
        r = p.add_run(teks)
        r.italic = True
        r.font.size = Pt(9)
        r.font.color.rgb = ABU
        return p

    def gambar(self, path, lebar, caption):
        self.doc.add_picture(str(path), width=Inches(lebar))
        p = self.doc.paragraphs[-1]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        self.caption(caption)

    def _shading(self, cell, fill):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:fill'), fill)
        tcPr.append(shd)

    def tabel(self, headers, rows, widths=None, font=8.5, aligns=None,
              caption=None, header_fill='1F3864'):
        if caption:
            self.caption(caption, atas=True)
        t = self.doc.add_table(rows=1, cols=len(headers))
        t.style = 'Table Grid'
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        if widths:
            for i, w in enumerate(widths):
                t.columns[i].width = Inches(w)

        hdr = t.rows[0]
        trPr = hdr._tr.get_or_add_trPr()
        th = OxmlElement('w:tblHeader')
        th.set(qn('w:val'), 'true')
        trPr.append(th)
        cs = OxmlElement('w:cantSplit')
        trPr.append(cs)
        for i, h in enumerate(headers):
            c = hdr.cells[i]
            c.width = Inches(widths[i]) if widths else c.width
            c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            self._shading(c, header_fill)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(str(h))
            r.bold = True
            r.font.size = Pt(font)
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        for row in rows:
            cells = t.add_row().cells
            trPr = t.rows[-1]._tr.get_or_add_trPr()
            cs = OxmlElement('w:cantSplit')
            trPr.append(cs)
            for i, val in enumerate(row):
                c = cells[i]
                if widths:
                    c.width = Inches(widths[i])
                c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = c.paragraphs[0]
                a = (aligns[i] if aligns else ('l' if i == 0 else 'c'))
                p.alignment = {'l': WD_ALIGN_PARAGRAPH.LEFT,
                               'c': WD_ALIGN_PARAGRAPH.CENTER,
                               'r': WD_ALIGN_PARAGRAPH.RIGHT,
                               'j': WD_ALIGN_PARAGRAPH.JUSTIFY}[a]
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.0
                r = p.add_run('' if val is None else str(val))
                r.font.size = Pt(font)
        return t

    def halaman_putus(self):
        self.doc.add_page_break()

    def simpan(self, path: Path):
        cp = self.doc.core_properties
        cp.title = ('Tugas 06 Pembelajaran Mesin - Kelompok 02 - '
                    'Kantor Notaris & PPAT Aries Buwana')
        cp.subject = ('Evaluasi Kinerja Model, Kalibrasi Ambang Batas, Optimasi '
                      'Hiperparameter, dan Integrasi Proposal UTS')
        cp.author = 'Kelompok 02'
        cp.last_modified_by = 'Kelompok 02'
        cp.keywords = ('Pembelajaran Mesin; Decision Tree; Threshold Tuning; '
                       'Optuna; Notaris PPAT')
        cp.comments = ('Laporan Tugas 06 Kelompok 02. Seluruh angka berasal dari '
                       'eksperimen yang dijalankan dan disertakan dalam paket.')
        cp.category = 'Laporan Akademik'
        self.doc.save(str(path))
