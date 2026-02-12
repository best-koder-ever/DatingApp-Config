"""🤖 DatingApp Bot Dashboard — NiceGUI web UI on port 9090."""
import asyncio

from nicegui import ui, app

from . import config
from .seeder import seed_bots, reset_bots, state as seeder_state
from .simulator import run_simulation, stop_simulation, state as sim_state

# ─── Shared State ────────────────────────────────────────────────────────────

_seed_task: asyncio.Task | None = None
_sim_task: asyncio.Task | None = None


# ─── Dashboard Page ──────────────────────────────────────────────────────────

@ui.page("/")
def dashboard():
    """Build the full dashboard UI."""

    # ── Header ──
    with ui.header().classes("bg-indigo-700 text-white items-center justify-between"):
        ui.label("🤖 DatingApp Bot Dashboard").classes("text-xl font-bold")
        with ui.row().classes("gap-4"):
            lbl_bots = ui.label("Bots: 0")
            lbl_swipes = ui.label("Swipes: 0")
            lbl_matches = ui.label("Matches: 0")
            lbl_msgs = ui.label("Msgs: 0")

    # ── Status timer — updates header counters every second ──
    def update_counters():
        lbl_bots.text = f"Bots: {seeder_state.created}"
        lbl_swipes.text = f"Swipes: {sim_state.swipes}"
        lbl_matches.text = f"Matches: {sim_state.matches}"
        lbl_msgs.text = f"Msgs: {sim_state.messages_sent}"

    ui.timer(1.0, update_counters)

    # ── Tabs ──
    with ui.tabs().classes("w-full") as tabs:
        tab_seed = ui.tab("🌱 Seed", label="🌱 Seed Profiles")
        tab_sim = ui.tab("🎮 Simulate", label="🎮 Simulate")
        tab_load = ui.tab("📊 Load Test", label="📊 Load Test")
        tab_logs = ui.tab("📋 Logs", label="📋 All Logs")

    with ui.tab_panels(tabs, value=tab_seed).classes("w-full flex-grow"):

        # ════════════════════════════════════════════════════════════════════
        # TAB 1: SEED PROFILES
        # ════════════════════════════════════════════════════════════════════
        with ui.tab_panel(tab_seed):
            seed_log = ui.log(max_lines=200).classes("w-full h-64")

            with ui.row().classes("w-full items-end gap-4 mt-4"):
                bot_count = ui.number("Bot count", value=config.DEFAULT_BOT_COUNT, min=1, max=500, step=10).classes("w-32")
                seed_mode = ui.select(
                    ["keycloak", "local"],
                    value="local",
                    label="Mode",
                ).classes("w-40")

                async def on_seed():
                    global _seed_task
                    if seeder_state.running:
                        seed_log.push("⚠️  Seeder already running!")
                        return
                    seed_log.push("─" * 50)
                    _seed_task = asyncio.create_task(
                        seed_bots(
                            count=int(bot_count.value),
                            log_callback=seed_log.push,
                            mode=seed_mode.value,
                        )
                    )

                async def on_reset():
                    seed_log.push("─" * 50)
                    await reset_bots(log_callback=seed_log.push)

                def on_cancel_seed():
                    seeder_state.cancelled = True
                    seed_log.push("⛔ Cancelling...")

                ui.button("🚀 Seed Bots", on_click=on_seed, color="green")
                ui.button("⛔ Cancel", on_click=on_cancel_seed, color="orange")
                ui.button("🗑️ Reset All", on_click=on_reset, color="red")

            # Progress bar
            seed_progress = ui.linear_progress(value=0, show_value=False).classes("w-full mt-2")
            ui.timer(0.5, lambda: seed_progress.set_value(seeder_state.progress))

        # ════════════════════════════════════════════════════════════════════
        # TAB 2: SIMULATE
        # ════════════════════════════════════════════════════════════════════
        with ui.tab_panel(tab_sim):
            sim_log = ui.log(max_lines=300).classes("w-full h-64")

            # Startup phase banner (visible during service bring-up)
            startup_banner = ui.label("").classes(
                "w-full text-center text-lg font-semibold text-orange-600 py-2"
            )
            startup_banner.set_visibility(False)

            def update_startup_phase():
                phase = sim_state.startup_phase
                if phase:
                    startup_banner.text = f"⏳ {phase}"
                    startup_banner.set_visibility(True)
                else:
                    startup_banner.set_visibility(False)

            ui.timer(0.5, update_startup_phase)

            with ui.row().classes("w-full items-end gap-4 mt-4"):
                sim_mode = ui.select(
                    ["live", "dry-run"],
                    value="dry-run",
                    label="Mode",
                ).classes("w-40")
                sim_cycles = ui.number("Cycles (0=∞)", value=0, min=0, max=10000, step=1).classes("w-32")
                speed_slider = ui.slider(min=0.1, max=5.0, value=1.0, step=0.1).classes("w-48")
                ui.label().bind_text_from(speed_slider, "value", backward=lambda v: f"Speed: {v:.1f}x")

                def on_speed_change():
                    sim_state.speed = speed_slider.value

                speed_slider.on("update:model-value", on_speed_change)

                async def on_start_sim():
                    global _sim_task
                    if sim_state.running:
                        sim_log.push("⚠️  Simulator already running!")
                        return
                    sim_log.push("─" * 50)
                    _sim_task = asyncio.create_task(
                        run_simulation(
                            log_callback=sim_log.push,
                            mode=sim_mode.value,
                            cycles=int(sim_cycles.value),
                        )
                    )

                def on_stop_sim():
                    stop_simulation()
                    sim_log.push("⛔ Stopping simulation...")

                def on_reset_sim():
                    stop_simulation()
                    sim_state.reset()
                    sim_log.push("🧹 Simulator state reset")

                ui.button("▶️ Start", on_click=on_start_sim, color="green")
                ui.button("⏹️ Stop", on_click=on_stop_sim, color="orange")
                ui.button("🔄 Reset", on_click=on_reset_sim, color="red")

            # Live stats
            with ui.row().classes("w-full gap-8 mt-4"):
                with ui.card().classes("p-4"):
                    ui.label("Active Bots").classes("text-sm text-gray-500")
                    stat_bots = ui.label("0").classes("text-3xl font-bold text-indigo-600")
                with ui.card().classes("p-4"):
                    ui.label("Swipes").classes("text-sm text-gray-500")
                    stat_swipes = ui.label("0").classes("text-3xl font-bold text-blue-600")
                with ui.card().classes("p-4"):
                    ui.label("Matches").classes("text-sm text-gray-500")
                    stat_matches = ui.label("0").classes("text-3xl font-bold text-pink-600")
                with ui.card().classes("p-4"):
                    ui.label("Messages").classes("text-sm text-gray-500")
                    stat_msgs = ui.label("0").classes("text-3xl font-bold text-green-600")
                with ui.card().classes("p-4"):
                    ui.label("Errors").classes("text-sm text-gray-500")
                    stat_errors = ui.label("0").classes("text-3xl font-bold text-red-600")

            def update_sim_stats():
                stat_bots.text = str(sim_state.active_bots)
                stat_swipes.text = str(sim_state.swipes)
                stat_matches.text = str(sim_state.matches)
                stat_msgs.text = str(sim_state.messages_sent)
                stat_errors.text = str(sim_state.errors)

            ui.timer(1.0, update_sim_stats)

        # ════════════════════════════════════════════════════════════════════
        # TAB 3: LOAD TESTING
        # ════════════════════════════════════════════════════════════════════
        with ui.tab_panel(tab_load):
            ui.label("📊 Load Testing").classes("text-xl font-bold mb-4")

            with ui.card().classes("w-full p-4"):
                ui.label("Locust (built-in)").classes("text-lg font-semibold")
                ui.markdown(
                    "Start Locust from the command line:\n\n"
                    "```bash\n"
                    "cd bot-service && python -m locust -f bot_service/locust_tests/locustfile.py\n"
                    "```\n\n"
                    "Then open **http://localhost:8089** for the Locust web UI."
                )

                async def launch_locust():
                    import subprocess
                    subprocess.Popen(
                        ["python", "-m", "locust", "-f", "bot_service/locust_tests/locustfile.py"],
                        cwd="/home/m/development/DatingApp/bot-service",
                    )
                    ui.notify("🚀 Locust started on http://localhost:8089", type="positive")

                ui.button("🚀 Launch Locust Web UI", on_click=launch_locust, color="teal")

            with ui.card().classes("w-full p-4 mt-4"):
                ui.label("k6 (external)").classes("text-lg font-semibold")
                ui.markdown(
                    "Run k6 load tests:\n\n"
                    "```bash\n"
                    "k6 run bot-service/bot_service/load_tests/smoke.js\n"
                    "k6 run bot-service/bot_service/load_tests/spike.js\n"
                    "```"
                )

        # ════════════════════════════════════════════════════════════════════
        # TAB 4: ALL LOGS
        # ════════════════════════════════════════════════════════════════════
        with ui.tab_panel(tab_logs):
            ui.label("📋 Combined Activity Log").classes("text-xl font-bold mb-4")
            all_log = ui.log(max_lines=500).classes("w-full h-96")
            all_log.push("Dashboard started. Use the tabs above to seed bots and run simulations.")

            with ui.row().classes("mt-4"):
                ui.button("🧹 Clear Log", on_click=lambda: all_log.clear(), color="gray")

    # ── Footer ──
    with ui.footer().classes("bg-gray-100 text-gray-600 text-sm"):
        ui.label(f"Bot Dashboard v1.0 • Services: Gateway {config.GATEWAY_URL} • Keycloak {config.KEYCLOAK_URL}")


# ─── Entry Point ─────────────────────────────────────────────────────────────

ui.run(
    title="🤖 DatingApp Bot Dashboard",
    port=config.DASHBOARD_PORT,
    reload=False,
    show=False,
)
