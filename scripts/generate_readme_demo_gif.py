from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT_DIR / "docs" / "assets" / "hybrid-demo.gif"

WIDTH = 1440
HEIGHT = 860


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates: list[str] = []
    if bold:
        candidates.extend(
            [
                r"C:\Windows\Fonts\segoeuib.ttf",
                r"C:\Windows\Fonts\arialbd.ttf",
            ]
        )
    else:
        candidates.extend(
            [
                r"C:\Windows\Fonts\segoeui.ttf",
                r"C:\Windows\Fonts\arial.ttf",
            ]
        )

    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


TITLE_FONT = load_font(44, bold=True)
SUBTITLE_FONT = load_font(28)
LABEL_FONT = load_font(30, bold=True)
BODY_FONT = load_font(22)
SMALL_FONT = load_font(18)


BOXES = {
    "client": (86, 320, 260, 435),
    "gateway": (338, 280, 604, 474),
    "hybrid": (338, 132, 564, 236),
    "registry": (670, 164, 964, 300),
    "services": (670, 344, 964, 484),
    "workers": (670, 524, 964, 644),
    "kronos": (1032, 110, 1302, 234),
    "tradingagents": (1032, 304, 1302, 428),
    "aihf": (1032, 498, 1302, 622),
    "signal": (1014, 214, 1324, 286),
}


FRAME_STEPS = [
    {
        "highlight": ["gateway", "registry", "services", "workers", "kronos"],
        "headline": "Step 1 · Run a real Kronos forecast",
        "copy": "The hub sends OHLCV history into an isolated worker and gets back structured forecast output.",
        "accent": "#0f766e",
    },
    {
        "highlight": ["gateway", "registry", "services", "workers", "kronos", "signal"],
        "headline": "Step 2 · Build a reusable forecast signal",
        "copy": "Hybrid synthesizes direction, expected return, horizon, and action bias into a clean bridge contract.",
        "accent": "#c97318",
    },
    {
        "highlight": ["gateway", "registry", "services", "workers", "signal", "tradingagents"],
        "headline": "Step 3 · Inject forecast into research",
        "copy": "TradingAgents analysts, researchers, trader, and portfolio manager all receive the forecast context in-prompt.",
        "accent": "#1f6feb",
    },
    {
        "highlight": ["gateway", "registry", "services", "workers", "signal", "tradingagents", "aihf"],
        "headline": "Step 4 · Fan out into execution or backtest",
        "copy": "When credentials and dates are available, hybrid can continue into AI Hedge Fund execution or backtesting.",
        "accent": "#8b5cf6",
    },
]


def rounded_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, outline: str, width: int = 2) -> None:
    draw.rounded_rectangle(box, radius=28, fill=fill, outline=outline, width=width)


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str, width: int = 6) -> None:
    draw.line([start, end], fill=color, width=width)
    ex, ey = end
    draw.polygon([(ex, ey), (ex - 14, ey - 8), (ex - 14, ey + 8)], fill=color)


def draw_box(draw: ImageDraw.ImageDraw, key: str, title: str, subtitle: str, *, active: bool = False, accent: str = "#0f766e") -> None:
    box = BOXES[key]
    if active:
        fill = "#fffdf8"
        outline = accent
        glow = accent
    else:
        fill = "#fffaf0"
        outline = "#d6cfbc"
        glow = None

    rounded_box(draw, box, fill=fill, outline=outline, width=4 if active else 2)

    if glow:
        x1, y1, x2, y2 = box
        draw.rounded_rectangle((x1 - 8, y1 - 8, x2 + 8, y2 + 8), radius=32, outline=glow, width=3)

    x1, y1, x2, y2 = box
    cx = (x1 + x2) / 2
    draw.text((cx, y1 + 26), title, fill="#102018", font=LABEL_FONT, anchor="ma")
    draw.text((cx, y1 + 68), subtitle, fill="#566458", font=BODY_FONT, anchor="ma")


def draw_signal_banner(draw: ImageDraw.ImageDraw, *, active: bool, accent: str) -> None:
    box = BOXES["signal"]
    rounded_box(
        draw,
        box,
        fill="#fff8ec" if active else "#f4efe3",
        outline=accent if active else "#d7d0be",
        width=4 if active else 2,
    )
    x1, y1, x2, _ = box
    draw.text(((x1 + x2) / 2, y1 + 20), "Forecast Signal", fill="#754515", font=LABEL_FONT, anchor="ma")
    draw.text((x1 + 24, y1 + 58), "direction · return · horizon · action bias", fill="#8a5a25", font=SMALL_FONT)


def build_frame(step: dict) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), "#f4efe3")
    draw = ImageDraw.Draw(image)

    # Background
    draw.rounded_rectangle((24, 24, WIDTH - 24, HEIGHT - 24), radius=36, fill="#f8f4ea", outline="#d7d0be", width=2)
    draw.ellipse((-60, -80, 440, 320), fill="#d6efe7")
    draw.ellipse((WIDTH - 460, HEIGHT - 300, WIDTH + 40, HEIGHT + 120), fill="#f4dcc2")

    draw.text((84, 82), "Kronos Hub", fill="#0f766e", font=SUBTITLE_FONT)
    draw.text((84, 124), "Forecast · Research · Execution", fill="#102018", font=TITLE_FONT)
    draw.text((84, 186), "One hub for modern quant workflows", fill="#102018", font=TITLE_FONT)
    draw.text((84, 250), "A lightweight orchestration layer for Kronos, TradingAgents, and AI Hedge Fund.", fill="#546256", font=SUBTITLE_FONT)

    # Arrows
    arrow(draw, (260, 378), (328, 378), "#0f766e")
    arrow(draw, (604, 378), (658, 378), "#0f766e")
    arrow(draw, (818, 230), (1022, 170), "#c97318")
    arrow(draw, (964, 378), (1022, 378), "#1f6feb")
    arrow(draw, (964, 584), (1022, 560), "#8b5cf6")
    arrow(draw, (564, 184), (658, 220), "#c97318")

    active = set(step["highlight"])
    accent = step["accent"]

    draw_box(draw, "client", "Clients", "scripts / future UI", active="client" in active, accent=accent)
    draw_box(draw, "gateway", "FastAPI Gateway", "one API surface", active="gateway" in active, accent=accent)
    draw_box(draw, "hybrid", "Hybrid", "forecast-aware bridge", active="hybrid" in active, accent=accent)
    draw_box(draw, "registry", "Engine Registry", "kronos · tradingagents · aihf", active="registry" in active, accent=accent)
    draw_box(draw, "services", "Service Layer", "payloads · config · contracts", active="services" in active, accent=accent)
    draw_box(draw, "workers", "JSON Workers", "subprocess isolation", active="workers" in active, accent=accent)
    draw_box(draw, "kronos", "Kronos", "forecast engine", active="kronos" in active, accent=accent)
    draw_box(draw, "tradingagents", "TradingAgents", "research + debate", active="tradingagents" in active, accent=accent)
    draw_box(draw, "aihf", "AI Hedge Fund", "execution + backtest shell", active="aihf" in active, accent=accent)
    draw_signal_banner(draw, active="signal" in active, accent=accent)

    # Bottom caption
    draw.rounded_rectangle((72, 690, WIDTH - 72, 804), radius=28, fill="#102018", outline="#102018")
    draw.text((104, 720), step["headline"], fill="#f8f4ea", font=LABEL_FONT)
    draw.text((104, 762), step["copy"], fill="#c6d7cf", font=BODY_FONT)

    return image.convert("P", palette=Image.ADAPTIVE)


def expand_frames(frames: Iterable[Image.Image], hold: int = 2) -> list[Image.Image]:
    expanded: list[Image.Image] = []
    for frame in frames:
        expanded.extend([frame] * hold)
    return expanded


def main() -> None:
    frames = [build_frame(step) for step in FRAME_STEPS]
    frames = expand_frames(frames, hold=2)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=850,
        loop=0,
        disposal=2,
    )
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
