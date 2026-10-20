# SimAI 1.0.0 — Muse Core

SimAI è il motore di simulazione della vita di Anthalys. La 1.0
dimostra che il nucleo della simulazione funziona end-to-end:
avvio, simulazione autonoma, interazione, salvataggio e ripresa.

Il mondo iniziale è il **Quartiere delle Muse**: 3 location (casa,
piazza, caffè), 5 personaggi (4 NPC autonomi + 1 Sim giocabile).

## Requisiti

- Python 3.13
- [`uv`](https://docs.astral.sh/uv/) (consigliato) oppure `pip`

## Installazione

```bash
git clone <repo-url> SimAI
cd SimAI
uv sync --all-extras
