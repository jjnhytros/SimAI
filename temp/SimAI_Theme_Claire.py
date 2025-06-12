from midiutil import MIDIFile

# Crea un oggetto MIDI con 1 traccia
track = 0
channel = 0
time = 0      # Inizio a 0
tempo = 68    # BPM
volume = 100

mf = MIDIFile(1)  # una traccia
mf.addTempo(track, time, tempo)

# NOTE MIDI (A = 69, G = 67, F = 65, E = 64, D = 62, C = 60)

# Intro – Risveglio Digitale
intro_notes = [69, 65, 62]
for i, note in enumerate(intro_notes):
    mf.addNote(track, channel, note, time + i * 2, 1.5, volume)

# Sezione B – Empatia Simulata
section_b_notes = [67, 64, 69, 70, 65]
for i, note in enumerate(section_b_notes):
    mf.addNote(track, channel, note, time + 8 + i * 1.5, 1.5, volume)

# Sezione B' – Il Conflitto Interiore
loop_notes = [64, 65, 69, 63]
loop_start = 16
for loop in range(2):
    for i, note in enumerate(loop_notes):
        mf.addNote(track, channel, note, loop_start + loop * 4 + i * 1, 1.0, volume)

# Sezione C – Claire’s Voice (sospesa)
section_c_chords = [(62,), (70,), (69, 71)]
chord_start = 25
for i, chord in enumerate(section_c_chords):
    for note in chord:
        mf.addNote(track, channel, note, chord_start + i * 2, 2.0, volume)

# Finale – Il Mondo che Resta
final_notes = [69, 65, 62]
final_start = 32
for i, note in enumerate(final_notes):
    mf.addNote(track, channel, note, final_start + i * 2, 1.5, volume)

# Salvataggio
with open("SimAI_Theme_Claire.mid", "wb") as output_file:
    mf.writeFile(output_file)

print("🎼 Tema salvato come 'SimAI_Theme_Claire.mid'")
