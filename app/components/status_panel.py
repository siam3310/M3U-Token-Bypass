import reflex as rx
from app.states.scraper_state import ScraperState


def log_item(message: str):
    return rx.el.div(
        rx.el.span(">", class_name="text-green-700 mr-1.5 font-bold"),
        rx.el.span(message, class_name="text-zinc-600"),
        class_name="text-[9px] font-mono py-0.5",
    )


def status_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "// CONTROL",
                    class_name="text-[10px] font-bold text-zinc-500 font-mono uppercase tracking-widest",
                ),
                rx.el.div(
                    rx.el.span(
                        rx.cond(ScraperState.is_scanning, "[BUSY]", "[IDLE]"),
                        class_name=rx.cond(
                            ScraperState.is_scanning,
                            "text-green-600 font-mono text-[9px] font-bold",
                            "text-zinc-700 font-mono text-[9px] font-bold",
                        ),
                    )
                ),
                class_name="flex justify-between items-center mb-3",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        class_name="bg-green-800 h-0.5",
                        style={"width": f"{ScraperState.scan_progress}%"},
                    ),
                    class_name="w-full bg-zinc-900 h-0.5 mb-1",
                ),
                rx.el.div(
                    rx.el.span(
                        ScraperState.scan_status_message,
                        class_name="text-zinc-600 text-[9px] font-mono uppercase truncate mr-2",
                    ),
                    rx.el.span(
                        f"{ScraperState.scan_progress}%",
                        class_name="text-green-700 text-[9px] font-mono font-bold",
                    ),
                    class_name="flex justify-between items-center",
                ),
                class_name="mb-3",
            ),
            rx.el.div(
                rx.el.button(
                    rx.cond(ScraperState.is_scanning, "ABORT", "EXECUTE_SCAN"),
                    on_click=ScraperState.start_scan,
                    disabled=ScraperState.is_scanning,
                    class_name="w-full flex items-center justify-center bg-black disabled:text-zinc-800 border border-green-900 text-green-600 py-1.5 font-mono font-bold text-[9px] uppercase tracking-widest mb-2 active:bg-green-900/20 cursor-pointer",
                ),
                rx.el.div(
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            on_change=ScraperState.toggle_auto_refresh,
                            checked=ScraperState.auto_refresh,
                            class_name="sr-only peer",
                        ),
                        rx.el.div(
                            class_name="w-5 h-2.5 bg-zinc-900 peer-focus:outline-none border border-zinc-800 peer peer-checked:border-green-900 peer-checked:bg-green-900/20 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-zinc-700 after:h-1.5 after:w-1.5 peer-checked:after:translate-x-full peer-checked:after:bg-green-700"
                        ),
                        class_name="relative inline-flex items-center cursor-pointer",
                    ),
                    rx.el.span(
                        "AUTO_REFRESH",
                        class_name="text-[9px] text-zinc-600 ml-2 font-mono uppercase",
                    ),
                    class_name="flex items-center justify-center",
                ),
                class_name="flex flex-col",
            ),
            class_name="p-3 border-b border-zinc-900",
        ),
        rx.el.div(
            rx.el.h3(
                "> LOGS",
                class_name="text-[9px] font-bold text-zinc-600 font-mono uppercase tracking-widest mb-1 px-3 pt-2",
            ),
            rx.el.div(
                rx.foreach(ScraperState.logs, log_item),
                class_name="flex flex-col h-32 overflow-y-auto px-3 pb-3 custom-scrollbar",
            ),
            class_name="flex-1 bg-black",
        ),
        class_name="w-full lg:w-full bg-black border border-zinc-900 flex flex-col h-fit",
    )