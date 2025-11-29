import reflex as rx
from app.states.scraper_state import ScraperState, Channel


def status_badge(status: str) -> rx.Component:
    return rx.match(
        status,
        (
            "success",
            rx.el.span(
                "[OK]", class_name="text-green-600 text-[9px] font-mono font-bold"
            ),
        ),
        (
            "error",
            rx.el.span(
                "[ERR]", class_name="text-red-700 text-[9px] font-mono font-bold"
            ),
        ),
        (
            "pending",
            rx.el.span(
                "[...]", class_name="text-zinc-700 text-[9px] font-mono font-bold"
            ),
        ),
        rx.el.span("[?]", class_name="text-zinc-700 text-[9px] font-mono font-bold"),
    )


def channel_card(channel: Channel) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.image(
                src=rx.cond(channel["logo"] != "", channel["logo"], "/placeholder.svg"),
                class_name="h-4 w-auto object-contain opacity-40 grayscale",
                loading="lazy",
            ),
            status_badge(channel["status"]),
            class_name="flex justify-between items-start mb-2",
        ),
        rx.el.div(
            rx.el.h3(
                channel["name"],
                class_name="font-bold text-zinc-400 text-[10px] truncate mb-0.5 font-mono uppercase tracking-wide",
            ),
            rx.el.div(
                rx.el.span("ID:", class_name="text-zinc-700 mr-1"),
                rx.el.span(channel["stream_path"], class_name="text-zinc-600"),
                class_name="text-[9px] font-mono truncate mb-2",
            ),
            rx.el.div(
                rx.cond(
                    channel["m3u8_url"] != "",
                    rx.el.button(
                        "> COPY_LINK",
                        on_click=rx.set_clipboard(channel["m3u8_url"]),
                        class_name="flex items-center justify-center w-full px-2 py-1 bg-black text-zinc-500 text-[9px] font-mono border border-zinc-800 uppercase active:bg-zinc-900 active:text-green-500 active:border-green-900 cursor-pointer",
                    ),
                    rx.el.div(
                        "SCANNING...",
                        class_name="flex items-center justify-center w-full px-2 py-1 bg-black text-zinc-800 text-[9px] font-mono border border-zinc-900 uppercase",
                    ),
                )
            ),
            class_name="flex flex-col",
        ),
        class_name="bg-black border border-zinc-900 p-2 flex flex-col justify-between h-full",
    )


def channel_grid() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "// TARGETS",
                class_name="text-[10px] font-bold text-zinc-500 font-mono uppercase tracking-widest mb-2 lg:mb-0",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.input(
                        placeholder="SEARCH...",
                        on_change=ScraperState.set_search_query.debounce(500),
                        class_name="w-full sm:w-40 bg-black text-zinc-400 text-[10px] px-2 py-1 border border-zinc-800 focus:border-green-900 focus:ring-0 outline-none placeholder-zinc-800 font-mono uppercase",
                    ),
                    class_name="relative",
                ),
                rx.el.div(
                    rx.el.select(
                        rx.el.option("ALL", value="All"),
                        rx.foreach(
                            ScraperState.unique_tags,
                            lambda tag: rx.el.option(tag, value=tag),
                        ),
                        value=ScraperState.selected_tag,
                        on_change=ScraperState.set_selected_tag,
                        class_name="bg-black text-zinc-400 text-[10px] px-2 py-1 border border-zinc-800 focus:border-green-900 outline-none appearance-none cursor-pointer font-mono uppercase w-full sm:w-auto rounded-none",
                    ),
                    class_name="relative",
                ),
                rx.el.span(
                    f"[{ScraperState.total_channels}]",
                    class_name="hidden sm:inline-block text-[10px] text-zinc-600 bg-black px-2 py-1 border border-zinc-800 font-mono h-full uppercase",
                ),
                class_name="flex flex-col sm:flex-row gap-2 w-full sm:w-auto",
            ),
            class_name="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-2 pb-2 border-b border-zinc-900",
        ),
        rx.cond(
            ScraperState.channels.length() > 0,
            rx.el.div(
                rx.foreach(ScraperState.filtered_channels, channel_card),
                class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-2",
            ),
            rx.el.div(
                rx.el.p(
                    "[NO_DATA]", class_name="text-zinc-800 font-mono text-[10px] mb-1"
                ),
                rx.el.p(
                    "> AWAITING_SCAN", class_name="text-zinc-800 font-mono text-[10px]"
                ),
                class_name="flex flex-col items-center justify-center h-64 bg-black border border-zinc-900 border-dashed",
            ),
        ),
        class_name="w-full",
    )