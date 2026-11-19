"""Exportação da HQ em PDF: uma página por quadro, do tamanho da imagem, pronta para mandar no Slack."""
from __future__ import annotations

import io
import math
import re
from pathlib import Path

from fpdf import FPDF
from PIL import Image

PAGE_WIDTH = {'landscape': 280.0, 'portrait': 190.0, 'square': 220.0}   # mm
INK = (17, 17, 17)
CAPTION = (255, 226, 122)
GOLD = (255, 205, 70)


def latin1(text: str) -> str:
    """As fontes embutidas do PDF só têm latin-1 (que cobre o português); troca o resto por equivalentes."""
    for old, new in (('“', '"'), ('”', '"'), ('‘', "'"), ('’', "'"), ('—', '-'), ('–', '-'), ('…', '...')):
        text = text.replace(old, new)
    return text.encode('latin-1', 'replace').decode('latin-1')


def image_size(path: Path) -> tuple[float, float]:
    if path.suffix.lower() == '.svg':
        head = path.read_text(encoding='utf-8', errors='ignore')[:600]
        w, h = re.search(r'width="([\d.]+)', head), re.search(r'height="([\d.]+)', head)
        return (float(w.group(1)), float(h.group(1))) if w and h else (900.0, 600.0)
    with Image.open(path) as img:
        return img.size


def page_format(width_px: float, height_px: float) -> tuple[float, float]:
    ratio = height_px / width_px
    kind = 'landscape' if ratio < 0.9 else 'portrait' if ratio > 1.1 else 'square'
    width = PAGE_WIDTH[kind]
    return width, width * ratio


def draw_image(pdf: FPDF, path: Path, w: float, h: float):
    if path.suffix.lower() == '.svg':
        # O SVG (rascunho do modo demonstração) é desenhado com as fontes embutidas: mesmo cuidado com o latin-1.
        pdf.image(io.BytesIO(latin1(path.read_text(encoding='utf-8')).encode('utf-8')), x=0, y=0, w=w, h=h)
        return
    with Image.open(path) as img:
        pdf.image(img.convert('RGB'), x=0, y=0, w=w, h=h)


def burst(x, y, w, h, n=22):
    points = []
    for i in range(n):
        a = i / n * math.tau - math.pi / 2
        r = 0.51 if i % 2 == 0 else 0.37 + (i % 3) * 0.02
        points.append((x + w / 2 + math.cos(a) * r * w * 0.98, y + h / 2 + math.sin(a) * r * h * 0.96))
    return points


def draw_balloons(pdf: FPDF, balloons: list[dict], W: float, H: float):
    """Mesmas regras visuais do editor (tamanhos em fração da largura da imagem)."""
    pdf.set_draw_color(*INK)
    pdf.set_line_width(max(0.25, W * 0.0035))
    boxes = []
    for b in balloons:
        text = latin1(b.get('text', '').strip())
        if not text:
            continue
        kind = b.get('type', 'speech')
        font_mm = W * (0.027 if kind == 'shout' else 0.023) * b.get('size', 1)
        pdf.set_font('Helvetica', 'B', font_mm * 72 / 25.4)
        bw = W * b['w'] / 100
        pad_x = bw * {'speech': 0.14, 'thought': 0.17, 'shout': 0.23}.get(kind, 0) or font_mm * 0.7
        pad_y = font_mm * {'speech': 0.9, 'thought': 1.2, 'shout': 1.7}.get(kind, 0.5)
        line_h = font_mm * 1.12
        lines = pdf.multi_cell(max(bw - 2 * pad_x, font_mm), line_h, text.upper(), dry_run=True, output='LINES')
        bh = max(len(lines) * line_h + 2 * pad_y, 0 if kind == 'caption' else font_mm * 2.6)
        boxes.append((b, kind, W * b['x'] / 100, H * b['y'] / 100, bw, bh, pad_x, line_h, lines, font_mm))
    pdf.set_fill_color(255, 255, 255)
    for b, kind, x, y, bw, bh, *_ in boxes:   # rabichos por baixo dos balões
        tail = b.get('tail')
        if not tail or kind == 'caption':
            continue
        cx, cy, tx, ty = x + bw / 2, y + bh / 2, W * tail['x'] / 100, H * tail['y'] / 100
        length = math.hypot(tx - cx, ty - cy)
        if length < 1:
            continue
        nx, ny = -(ty - cy) / length, (tx - cx) / length
        if kind == 'thought':
            edge = min(bw, bh) / 2
            for t, r in ((0.45, 0.03), (0.7, 0.022), (0.92, 0.014)):
                d = edge + (length - edge) * t
                px, py, rr = cx + (tx - cx) / length * d, cy + (ty - cy) / length * d, W * r
                pdf.ellipse(px - rr, py - rr, 2 * rr, 2 * rr, style='DF')
        else:
            half = min(bw * 0.14, W * 0.035)
            pdf.polygon([(cx + nx * half, cy + ny * half), (tx, ty), (cx - nx * half, cy - ny * half)], style='DF')
    for b, kind, x, y, bw, bh, pad_x, line_h, lines, font_mm in boxes:
        if kind == 'caption':
            pdf.set_fill_color(*CAPTION)
            pdf.rect(x, y, bw, bh, style='DF')
        else:
            pdf.set_fill_color(255, 255, 255)
            if kind == 'shout':
                pdf.polygon(burst(x, y, bw, bh), style='DF')
            else:
                pdf.ellipse(x, y, bw, bh, style='DF')
        pdf.set_font('Helvetica', 'B', font_mm * 72 / 25.4)
        pdf.set_text_color(*INK)
        top = y + (bh - len(lines) * line_h) / 2
        for i, line in enumerate(lines):
            pdf.set_xy(x + pad_x, top + i * line_h)
            pdf.cell(bw - 2 * pad_x, line_h, line, align='L' if kind == 'caption' else 'C')


def draw_credits(pdf: FPDF, title: str, credits: dict):
    w, h = PAGE_WIDTH['portrait'], PAGE_WIDTH['portrait'] * 1.5
    pdf.add_page(format=(w, h))
    pdf.set_fill_color(20, 17, 15)
    pdf.rect(0, 0, w, h, style='F')
    lines = credits.get('lines', [])
    size = 15 if len(lines) <= 12 else 12 if len(lines) <= 20 else 10
    # Altura aproximada do bloco, para centralizar na página quando o elenco é curto.
    block = 20 + 10 + sum(size * (0.85 if line.get('role') else 0.5) + size * 0.35 for line in lines) + (20 if credits.get('footer') else 0)
    pdf.set_text_color(*GOLD)
    pdf.set_font('Helvetica', 'B', 30)
    pdf.set_xy(15, max(22, (h - block) / 2))
    pdf.multi_cell(w - 30, 13, latin1((credits.get('heading') or 'Elenco').upper()), align='C')
    if title:
        pdf.set_font('Helvetica', 'I', 13)
        pdf.set_text_color(220, 214, 200)
        pdf.set_x(15)
        pdf.multi_cell(w - 30, 7, latin1(title), align='C')
    pdf.ln(10)
    for line in lines:
        pdf.set_x(20)
        pdf.set_font('Helvetica', 'B', size)
        pdf.set_text_color(*GOLD)
        pdf.multi_cell(w - 40, size * 0.5, latin1(line.get('name', '')), align='C')
        if line.get('role'):
            pdf.set_x(20)
            pdf.set_font('Helvetica', '', size * 0.85)
            pdf.set_text_color(235, 230, 220)
            pdf.multi_cell(w - 40, size * 0.45, latin1(line['role']), align='C')
        pdf.ln(size * 0.35)
    if credits.get('footer'):
        pdf.ln(6)
        pdf.set_x(20)
        pdf.set_font('Helvetica', 'B', 13)
        pdf.set_text_color(255, 255, 255)
        pdf.multi_cell(w - 40, 7, latin1(credits['footer']), align='C')


def build_pdf(title: str, frames: list[dict], media_file, overlay_balloons: bool) -> tuple[bytes, int]:
    """Devolve o PDF e quantos quadros ficaram de fora por ainda não terem imagem."""
    pdf = FPDF(unit='mm')
    pdf.set_auto_page_break(False)
    pdf.set_margin(0)
    pdf.set_title(latin1(title))
    pdf.set_creator('HQ Studio')
    skipped = 0
    for frame in frames:
        if frame.get('kind') == 'credits':
            draw_credits(pdf, title, frame.get('credits') or {})
            continue
        path = media_file(frame.get('image_path'))
        if not path:
            skipped += 1
            continue
        w, h = page_format(*image_size(path))
        pdf.add_page(format=(w, h))
        draw_image(pdf, path, w, h)
        if overlay_balloons:
            draw_balloons(pdf, frame.get('balloons') or [], w, h)
    if not pdf.pages:
        raise ValueError('Nenhum quadro com imagem para exportar ainda.')
    return bytes(pdf.output()), skipped
