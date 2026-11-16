import streamlit as st
import numpy as np
import time

# Nastavení stránky pro pohodlné zobrazení na mobilu i PC
st.set_page_config(page_title="Conway's Game of Life", layout="centered")

st.title("Conway's Game of Life (50×50)")

# Velikost mřížky
GRID_SIZE = 50

# Inicializace stavu aplikace
if 'grid' not in st.session_state:
    st.session_state.grid = np.random.choice([0, 1], size=(GRID_SIZE, GRID_SIZE), p=[0.8, 0.2])
if 'generation' not in st.session_state:
    st.session_state.generation = 0
if 'running' not in st.session_state:
    st.session_state.running = False

# Výpočet další generace podle pravidel Game of Life
def next_generation(grid):
    # Počítání sousedů pomocí posunu matic (rychlé vektorizované řešení)
    neighbors = (
        np.roll(np.roll(grid, 1, 0), 1, 1) +
        np.roll(np.roll(grid, 1, 0), 0, 1) +
        np.roll(np.roll(grid, 1, 0), -1, 1) +
        np.roll(np.roll(grid, 0, 0), 1, 1) +
        np.roll(np.roll(grid, 0, 0), -1, 1) +
        np.roll(np.roll(grid, -1, 0), 1, 1) +
        np.roll(np.roll(grid, -1, 0), 0, 1) +
        np.roll(np.roll(grid, -1, 0), -1, 1)
    )
    # Pravidla přežití a zrození
    return ((neighbors == 3) | ((grid == 1) & (neighbors == 2))).astype(int)

# Funkce pro vložení známých vzorů
def load_pattern(pattern_name):
    g = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    mid = GRID_SIZE // 2
    if pattern_name == "Glider (Kluzák)":
        g[mid, mid+1] = 1
        g[mid+1, mid+2] = 1
        g[mid+2, mid:mid+3] = 1
    elif pattern_name == "Pulsar":
        coords = [
            (2,4),(2,5),(2,6),(2,10),(2,11),(2,12),
            (7,4),(7,5),(7,6),(7,10),(7,11),(7,12),
            (9,4),(9,5),(9,6),(9,10),(9,11),(9,12),
            (14,4),(14,5),(14,6),(14,10),(14,11),(14,12),
            (4,2),(5,2),(6,2),(10,2),(11,2),(12,2),
            (4,7),(5,7),(6,7),(10,7),(11,7),(12,7),
            (4,9),(5,9),(6,9),(10,9),(11,9),(12,9),
            (4,14),(5,14),(6,14),(10,14),(11,14),(12,14)
        ]
        for r, c in coords:
            g[mid - 8 + r, mid - 8 + c] = 1
    st.session_state.grid = g
    st.session_state.generation = 0
    st.session_state.running = False

# --- Ovládací panel (responzivní pro mobil) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("▶️ Start" if not st.session_state.running else "⏸️ Pauza", use_container_width=True):
        st.session_state.running = not st.session_state.running
        st.rerun()

with col2:
    if st.button("⏭️ Krok", use_container_width=True):
        st.session_state.running = False
        st.session_state.grid = next_generation(st.session_state.grid)
        st.session_state.generation += 1

with col3:
    if st.button("🎲 Náhodně", use_container_width=True):
        st.session_state.running = False
        st.session_state.grid = np.random.choice([0, 1], size=(GRID_SIZE, GRID_SIZE), p=[0.8, 0.2])
        st.session_state.generation = 0

with col4:
    if st.button("🗑️ Vymazat", use_container_width=True):
        st.session_state.running = False
        st.session_state.grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        st.session_state.generation = 0

# Výběr vzorů a rychlosti
c_pat, c_spd = st.columns(2)
with c_pat:
    vzor = st.selectbox("Vložit vzor:", ["Vyberte...", "Glider (Kluzák)", "Pulsar"])
    if vzor != "Vyberte...":
        if st.button("Načíst vybraný vzor"):
            load_pattern(vzor)
            st.rerun()

with c_spd:
    rychlost = st.slider("Rychlost (zpoždění v s):", 0.05, 1.0, 0.15, 0.05)

# Ruční přidání/odebrání buňky (ideální na mobil, kde se hůře kliká do malého plátna)
with st.expander("✏️ Přidat / smazat konkrétní buňku (X, Y)"):
    cx, cy = st.columns(2)
    x_coord = cx.number_input("Sloupec X (0–49):", min_value=0, max_value=GRID_SIZE-1, value=25)
    y_coord = cy.number_input("Řádek Y (0–49):", min_value=0, max_value=GRID_SIZE-1, value=25)
    if st.button("Přepnout buňku (Živá / Mrtvá)"):
        st.session_state.grid[y_coord, x_coord] = 1 - st.session_state.grid[y_coord, x_coord]
        st.rerun()

# Statistiky
zive_bunky = int(np.sum(st.session_state.grid))
st.caption(f"**Generace:** {st.session_state.generation} | **Živé buňky:** {zive_bunky}")

# Vykreslení mřížky jako obrázku (zvětšeného pro ostré pixely bez rozmazání)
zvetsena_mrizka = np.kron(st.session_state.grid, np.ones((10, 10)))
st.image(zvetsena_mrizka * 255, clamp=True, use_container_width=True)

# Smyčka při spuštěné simulaci
if st.session_state.running:
    time.sleep(rychlost)
    st.session_state.grid = next_generation(st.session_state.grid)
    st.session_state.generation += 1
    st.rerun()