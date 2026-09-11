with open("generate_html.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update global ICS button tooltip
old_ics_btn = '''<button @click="downloadAllIcs()" class="no-print bg-emerald-800 hover:bg-emerald-900 text-white px-3 py-1.5 rounded-lg text-xs font-semibold transition border border-emerald-700 flex items-center gap-1.5 shadow-sm">
                    <span>📅 Gesamter Spielplan als ICS</span>
                </button>'''

new_ics_btn = '''<div class="relative group inline-block no-print">
                    <button @click="downloadAllIcs()" class="bg-emerald-800 hover:bg-emerald-900 text-white px-3 py-1.5 rounded-lg text-xs font-semibold transition border border-emerald-700 flex items-center gap-1.5 shadow-sm">
                        <span>📅 Gesamter Spielplan als ICS</span>
                    </button>
                    <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1.5 hidden group-hover:block bg-gray-900 dark:bg-gray-700 text-white text-[10px] rounded px-2 py-1 whitespace-nowrap z-50 shadow-lg pointer-events-none">
                        Alle Saison-Spieltage als ICS-Kalenderdatei herunterladen
                        <div class="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
                    </div>
                </div>'''

# 2. Update Dark Mode button tooltip
old_dm_btn = '''<button @click="toggleDarkMode" class="no-print bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition border border-gray-300 dark:border-gray-600 flex items-center gap-1 shadow-sm" :title="isDarkMode ? 'Zu Hellmodus wechseln' : 'Zu Dunkelmodus wechseln'">
                    <span>[[ isDarkMode ? '\''☀️ Hell'\'' : '\''🌙 Dunkel'\'' ]]</span>
                </button>'''

new_dm_btn = '''<div class="relative group inline-block no-print">
                    <button @click="toggleDarkMode" class="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition border border-gray-300 dark:border-gray-600 flex items-center gap-1 shadow-sm">
                        <span>[[ isDarkMode ? '\''☀️ Hell'\'' : '\''🌙 Dunkel'\'' ]]</span>
                    </button>
                    <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1.5 hidden group-hover:block bg-gray-900 dark:bg-gray-700 text-white text-[10px] rounded px-2 py-1 whitespace-nowrap z-50 shadow-lg pointer-events-none">
                        [[ isDarkMode ? '\''Zu Hellmodus wechseln'\'' : '\''Zu Dunkelmodus wechseln'\'' ]]
                        <div class="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
                    </div>
                </div>'''

# 3. Update Print button tooltip
old_print_btn = '''<button @click="window.print()" class="no-print bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 text-xs font-medium transition flex items-center gap-1 shadow-sm" title="Drucken / Als PDF speichern">
                    <span>🖨️ Drucken</span>
                </button>'''

new_print_btn = '''<div class="relative group inline-block no-print">
                    <button @click="window.print()" class="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 text-xs font-medium transition flex items-center gap-1 shadow-sm">
                        <span>🖨️ Drucken</span>
                    </button>
                    <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1.5 hidden group-hover:block bg-gray-900 dark:bg-gray-700 text-white text-[10px] rounded px-2 py-1 whitespace-nowrap z-50 shadow-lg pointer-events-none">
                        Seite drucken oder als PDF speichern
                        <div class="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
                    </div>
                </div>'''

# 4. Update CSV export button tooltip
old_csv_btn = '''<button @click="exportStatsCsv()" class="no-print bg-emerald-800 hover:bg-emerald-900 text-white px-2.5 py-1 rounded text-[11px] font-semibold transition border border-emerald-700 flex items-center gap-1 shadow-xs" title="Statistik als CSV herunterladen">
                        <span>📥 CSV Export</span>
                    </button>'''

new_csv_btn = '''<div class="relative group inline-block no-print">
                        <button @click="exportStatsCsv()" class="bg-emerald-800 hover:bg-emerald-900 text-white px-2.5 py-1 rounded text-[11px] font-semibold transition border border-emerald-700 flex items-center gap-1 shadow-xs">
                            <span>📥 CSV Export</span>
                        </button>
                        <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1.5 hidden group-hover:block bg-gray-900 dark:bg-gray-700 text-white text-[10px] rounded px-2 py-1 whitespace-nowrap z-50 shadow-lg pointer-events-none">
                            Spieler-Statistik-Matrix als CSV herunterladen
                            <div class="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
                        </div>
                    </div>'''

# 5. Update Kosten info icon tooltip in JavaScript formatPlayerBadge or header
old_kosten_th = '''<th @click="sortBy(\x27kosten\x27)" class="p-2 text-center font-semibold cursor-pointer hover:bg-emerald-700 relative group" title="Klicken für Kostenformel-Details">
                                <span class="inline-flex items-center justify-center gap-1">
                                    <span>Kosten</span>
                                    <span @click.stop="showCostModal = true" class="text-[10px] bg-emerald-700 hover:bg-emerald-600 px-1.5 py-0.5 rounded cursor-pointer border border-emerald-600">ℹ️</span>
                                </span>
                                [[ sortColumn === '\''kosten'\'' ? (sortDirection === '\''asc'\'' ? '\''▲'\'' : '\''▼'\'' ) : '\''↕'\'' ]]
                            </th>'''

new_kosten_th = '''<th @click="sortBy(\x27kosten\x27)" class="p-2 text-center font-semibold cursor-pointer hover:bg-emerald-700 relative group">
                                <span class="inline-flex items-center justify-center gap-1 relative group/info">
                                    <span>Kosten</span>
                                    <span @click.stop="showCostModal = true" class="text-[10px] bg-emerald-700 hover:bg-emerald-600 px-1.5 py-0.5 rounded cursor-pointer border border-emerald-600">ℹ️</span>
                                    <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1.5 hidden group-hover/info:block bg-gray-900 dark:bg-gray-700 text-white text-[10px] rounded px-2 py-1 whitespace-nowrap z-50 shadow-lg pointer-events-none">
                                        Klick für Kostenformel-Details
                                        <div class="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
                                    </div>
                                </span>
                                [[ sortColumn === '\''kosten'\'' ? (sortDirection === '\''asc'\'' ? '\''▲'\'' : '\''▼'\'' ) : '\''↕'\'' ]]
                            </th>'''

count = 0
for old_s, new_s in [(old_ics_btn, new_ics_btn), (old_dm_btn, new_dm_btn), (old_print_btn, new_print_btn), (old_csv_btn, new_csv_btn), (old_kosten_th, new_kosten_th)]:
    if old_s in text:
        text = text.replace(old_s, new_s, 1)
        count += 1
    else:
        print(f"Warning: pattern not found!")

with open("generate_html.py", "w", encoding="utf-8") as f:
    f.write(text)

print(f"Successfully updated {count} tooltips in generate_html.py!")
