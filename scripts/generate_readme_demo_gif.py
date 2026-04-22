from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT_DIR / "docs" / "assets" / "hybrid-demo.gif"

WIDTH = 1440
HEIGHT = 820


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


TITLE_FONT = load_font(46, bold=True)
SUBTITLE_FONT = load_font(28)
SECTION_FONT = load_font(24, bold=True)
CARD_TITLE_FONT = load_font(30, bold=True)
CARD_BODY_FONT = load_font(19)
SMALL_FONT = load_font(18)


BOXES = {
    "client": (84, 326, 250, 450),
    "gateway": (292, 296, 552, 480),
    "forecast": (600, 296, 860, 480),
    "research": (908, 296, 1168, 480),
    "execution": (1196, 296, 1368, 480),
}


STEPS = [
    {
        "active": "forecast",
        "headline": "Step 1 · Run a real Kronos forecast",
        "copy": "OHLCV history enters the hub and is executed through an isolated Kronos worker runtime.",
        "color": "#12b3a6",
    },
    {
        "active": "forecast",
        "headline": "Step 2 · Build a forecast signal contract",
        "copy": "The hub turns raw forecast output into direction, return, horizon, and action bias.",
        "color": "#e89b2d",
    },
    {
        "active": "research",
        "headline": "Step 3 · Inject forecast into TradingAgents",
        "copy": "Analysts, researchers, trader, risk agents, and portfolio manager all receive forecast context in-prompt.",
        "color": "#3b82f6",
    },
    {
        "active": "execution",
        "headline": "Step 4 · Expand into execution or backtest",
        "copy": "When dates and credentials are available, hybrid can continue into AI Hedge Fund execution/backtesting.",
        "color": "#1dbf73",
    },
]


def rounded_rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], *, fill: str, outline: str, width: int = 2, radius: int = 28) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str, width: int = 6) -> None:
    draw.line([start, end], fill=color, width=width)
    ex, ey = end
    draw.polygon([(ex, ey), (ex - 16, ey - 10), (ex - 16, ey + 10)], fill=color)


def draw_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    title: str,
    body: str,
    active: bool,
    color: str,
) -> None:
    rounded_rect(
        draw,
        box,
        fill="#0f1d1a" if active else "#122522",
        outline=color if active else "#29423c",
        width=4 if active else 2,
        radius=26,
    )
    x1, y1, x2, y2 = box
    draw.text(((x1 + x2) / 2, y1 + 44), title, fill="#f3fbf8", font=CARD_TITLE_FONT, anchor="ma")
    draw.text(((x1 + x2) / 2, y1 + 92), body, fill="#9dc0b8", font=CARD_BODY_FONT, anchor="ma")


def draw_chip(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], *, label: str, sublabel: str, accent: str) -> None:
    rounded_rect(draw, box, fill="#101816", outline=accent, width=2, radius=20)
    x1, y1, x2, _ = box
    draw.text(((x1 + x2) / 2, y1 + 24), label, fill="#f3fbf8", font=SECTION_FONT, anchor="ma")
    draw.text(((x1 + x2) / 2, y1 + 52), sublabel, fill="#89a79f", font=SMALL_FONT, anchor="ma")


def build_frame(step: dict) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), "#081311")
    draw = ImageDraw.Draw(image)

    # Background
    draw.rounded_rectangle((18, 18, WIDTH - 18, HEIGHT - 18), radius=34, fill="#081311", outline="#1e3430", width=2)
    draw.ellipse((-160, -120, 360, 360), fill="#0d2a26")
    draw.ellipse((WIDTH - 400, HEIGHT - 320, WIDTH + 120, HEIGHT + 100), fill="#0d201b")

    draw.text((84, 74), "Kronos Hub", fill="#2dd4bf", font=SUBTITLE_FONT)
    draw.text((84, 124), "Forecast · Research · Execution", fill="#f3fbf8", font=TITLE_FONT)
    draw.text((84, 182), "One API hub for modern quant flows", fill="#f3fbf8", font=TITLE_FONT)
    draw.text((84, 258), "A cleaner way to connect Kronos forecasting, TradingAgents research, and AI Hedge Fund execution.", fill="#89a79f", font=SUBTITLE_FONT)

    active = step["active"]
    color = step["color"]

    # Core flow
    draw_card(draw, BOXES["client"], title="Clients", body="scripts / future UI", active=active == "client", color=color)
    draw_card(draw, BOXES["gateway"], title="FastAPI Gateway", body="one API surface", active=active == "gateway", color=color)
    draw_card(draw, BOXES["forecast"], title="Forecast Layer", body="Kronos + signal bridge", active=active == "forecast", color=color)
    draw_card(draw, BOXES["research"], title="Research Layer", body="forecast-aware TradingAgents", active=active == "research", color=color)
    draw_card(draw, BOXES["execution"], title="Execution", body="AIHF shell", active=active == "execution", color=color)

    arrow(draw, (250, 388), (280, 388), "#2dd4bf")
    arrow(draw, (552, 388), (584, 388), "#2dd4bf")
    arrow(draw, (860, 388), (892, 388), "#2dd4bf")
    arrow(draw, (1168, 388), (1200, 388), "#2dd4bf")

    # Bottom chips
    draw.text((84, 556), "Powered by real upstream runtimes", fill="#f3fbf8", font=SECTION_FONT)
    draw_chip(draw, (84, 590, 320, 668), label="Kronos", sublabel="forecast engine", accent="#12b3a6")
    draw_chip(draw, (360, 590, 686, 668), label="TradingAgents", sublabel="analysts · debate · trader · risk", accent="#3b82f6")
    draw_chip(draw, (726, 590, 1030, 668), label="AI Hedge Fund", sublabel="execution + backtest shell", accent="#1dbf73")

    # Status rail
    rounded_rect(draw, (84, 704, WIDTH - 84, 780), fill="#0f1d1a", outline="#243a35", width=2, radius=26)
    draw.text((112, 724), step["headline"], fill="#f3fbf8", font=SECTION_FONT)
    draw.text((112, 752), step["copy"], fill="#a4c4bc", font=CARD_BODY_FONT)
    draw.rounded_rectangle((WIDTH - 250, 720, WIDTH - 92, 760), radius=18, fill=color)
    draw.text((WIDTH - 171, 730), "live hybrid", fill="#081311", font=SECTION_FONT, anchor="ma")

    return image.convert("P", palette=Image.ADAPTIVE)


def main() -> None:
    frames = [build_frame(step) for step in STEPS]
    expanded: list[Image.Image] = []
    for frame in frames:
        expanded.extend([frame] * 2)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    expanded[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=expanded[1:],
        duration=900,
        loop=0,
        disposal=2,
    )
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
