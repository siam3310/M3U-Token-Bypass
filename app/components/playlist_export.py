import reflex as rx
from app.states.scraper_state import ScraperState


def playlist_export() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "// EXPORT",
                class_name="text-[10px] font-bold text-zinc-500 font-mono uppercase tracking-widest",
            ),
            rx.el.div(
                rx.el.button(
                    "COPY",
                    on_click=rx.set_clipboard(ScraperState.m3u_content),
                    class_name="flex items-center justify-center px-2 py-0.5 bg-black text-zinc-500 text-[9px] font-mono font-bold border border-zinc-800 uppercase active:text-green-500 active:border-green-900 cursor-pointer",
                ),
                rx.el.button(
                    "SAVE_M3U",
                    on_click=ScraperState.download_playlist,
                    class_name="flex items-center justify-center px-2 py-0.5 bg-black text-green-700 text-[9px] font-mono font-bold border border-green-900 uppercase active:bg-green-900/20 cursor-pointer",
                ),
                class_name="flex gap-2",
            ),
            class_name="flex justify-between items-center mb-2",
        ),
        rx.el.div(
            rx.el.textarea(
                read_only=True,
                class_name="w-full h-16 bg-black text-zinc-700 font-mono text-[9px] p-2 border border-zinc-900 focus:outline-none resize-none custom-scrollbar",
                default_value=ScraperState.m3u_content,
                key=ScraperState.m3u_content,
            ),
            class_name="mb-2",
        ),
        rx.el.div(
            rx.el.span(
                "NOTE: TOKENS EXPIRE", class_name="text-zinc-700 font-bold mr-2"
            ),
            rx.el.span("ENABLE AUTO_REFRESH", class_name="text-zinc-800"),
            class_name="text-[8px] font-mono uppercase flex items-center",
        ),
        class_name="w-full bg-black border border-zinc-900 p-3 h-fit",
    )