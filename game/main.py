# simai/game/main.py

import pygame
import sys  # Lo useremo per chiudere il programma in modo pulito

# --- Costanti e Configurazioni Iniziali ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WINDOW_TITLE = "Simulatore di Vita AI"
FPS = 60  # Frames Per Second

# Colori (formato RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
# Aggiungi altri colori se necessario qui
# es. GREY = (128, 128, 128)


def main():
    """
    Funzione principale del gioco.
    Inizializza Pygame, crea la finestra e gestisce il game loop.
    """
    # 1.a [] Creare il file principale del gioco (es. main.py in simai/game). (Sei qui!)
    # (Implicitamente fatto creando questo file)

    # Inizializzazione di Pygame
    pygame.init()

    # 1.b [] Implementare la finestra di gioco base di Pygame (inizializzazione, dimensioni, titolo).
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    # 1.e [] Impostare un clock per controllare il framerate (FPS).
    clock = pygame.time.Clock()

    # Variabile per controllare il game loop
    running = True

    # --- Variabili di Gioco (da inizializzare qui se necessario) ---
    # (Per ora nessuna, le aggiungeremo in seguito)

    # 1.c [] Creare il loop di gioco principale (gestione eventi, aggiornamento logica, rendering).
    while running:
        # --- Gestione Eventi ---
        # 1.d [] Gestire l'evento di chiusura della finestra.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Qui puoi aggiungere la gestione di altri eventi (tastiera, mouse, ecc.)
            # Esempio:
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_ESCAPE:
            #         running = False

        # --- Aggiornamento Logica di Gioco ---
        # (Qui andrà la logica per aggiornare lo stato del gioco,
        #  muovere i personaggi, far passare il tempo, ecc.)
        # Per ora, non c'è logica da aggiornare.

        # --- Rendering (Disegno) ---
        # Diciamo a Pygame di riempire lo schermo con un colore.
        # Questo "pulisce" il frame precedente.
        screen.fill(BLACK)  # Scegli un colore di sfondo, es. NERO

        # Qui disegneremo tutti gli elementi del gioco (personaggi, UI, ecc.)
        # Esempio: pygame.draw.rect(screen, WHITE, (100, 100, 50, 50)) # Disegna un quadrato bianco

        # Aggiorna l'intero schermo per mostrare ciò che è stato disegnato.
        pygame.display.flip()  # o pygame.display.update()

        # Controlla il framerate
        clock.tick(FPS)

    # Uscita da Pygame
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
