import reflex as rx
from app.components.status_panel import status_panel
from app.components.channel_grid import channel_grid
from app.components.playlist_export import playlist_export
from app.states.scraper_state import ScraperState


def index() -> rx.Component:
    return rx.el.div(
        rx.el.main(
            rx.el.div(
                rx.el.div(
                    status_panel(),
                    playlist_export(),
                    class_name="w-full lg:w-80 lg:shrink-0 flex flex-col gap-4",
                ),
                rx.el.div(channel_grid(), class_name="flex-1 w-full min-w-0"),
                class_name="flex flex-col lg:flex-row gap-4 max-w-full p-2 lg:p-4",
            ),
            class_name="min-h-screen bg-black text-zinc-400 font-mono selection:bg-green-900 selection:text-green-400",
        ),
        class_name="antialiased bg-black",
    )


app = rx.App(theme=rx.theme(appearance="light", accent_color="gray"), stylesheets=[])
app.add_page(index, route="/")