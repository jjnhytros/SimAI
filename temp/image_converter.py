import os  
import numpy as np  
import matplotlib.pyplot as plt  
from PIL import Image  
import sys  
  
def blend_images(image_folder='./', image_extensions=('.jpg', '.jpeg', '.png', '.webp', '.gif'),   
                 blend_method='additive', resize_method='largest', intensity=1.0):  
    """  
    Fonde tutte le immagini dalla cartella specificata.  
      
    Args:  
        image_folder: Percorso della cartella contenente le immagini  
        image_extensions: Estensioni dei file immagine da considerare  
        blend_method: 'average', 'additive', 'overlay', 'screen', 'multiply'  
        resize_method: 'largest', 'smallest', 'median', 'average'  
      
    Returns:  
        L'immagine fusa, larghezza e altezza  
    """  
    # Verifica che la cartella esista  
    if not os.path.exists(image_folder):  
        print(f"Errore: La cartella '{image_folder}' non esiste.")  
        return None  
      
    # Cerca tutti i file immagine nella cartella  
    print(f"Ricerca delle immagini nella cartella: {image_folder}")  
      
    try:  
        all_files = os.listdir(image_folder)  
    except Exception as e:  
        print(f"Errore nell'accesso alla cartella: {e}")  
        return None  
      
    # Filtra solo i file immagine  
    image_files = [f for f in all_files   
                  if os.path.isfile(os.path.join(image_folder, f))   
                  and f.lower().endswith(image_extensions)]  
      
    if not image_files:  
        print(f"Nessuna immagine trovata nella cartella '{image_folder}'.")  
        print(f"Estensioni supportate: {image_extensions}")  
        print(f"File presenti nella cartella: {all_files[:10] if len(all_files) > 10 else all_files}")  
        return None  
      
    print(f"Trovate {len(image_files)} immagini potenziali.")  
      
    # Raccoglie informazioni sulle dimensioni  
    all_widths = []  
    all_heights = []  
    valid_image_paths = []  
      
    for img_file in image_files:  
        img_path = os.path.join(image_folder, img_file)  
        try:  
            with Image.open(img_path) as img:  
                width, height = img.size  
                all_widths.append(width)  
                all_heights.append(height)  
                valid_image_paths.append(img_path)  
                print(f"Immagine valida: {img_file}, Dimensioni: {width}x{height}")  
        except Exception as e:  
            print(f"Impossibile aprire {img_file}: {e}")  
      
    if not valid_image_paths:  
        print("Nessuna immagine valida trovata. Verifica che i file siano immagini leggibili.")  
        return None  
      
    print(f"Immagini valide: {len(valid_image_paths)}/{len(image_files)}")  
      
    # Determina le dimensioni target in base al metodo scelto  
    if resize_method == 'largest':  
        target_width = max(all_widths)  
        target_height = max(all_heights)  
    elif resize_method == 'smallest':  
        target_width = min(all_widths)  
        target_height = min(all_heights)  
    elif resize_method == 'median':  
        target_width = int(np.median(all_widths))  
        target_height = int(np.median(all_heights))  
    else:  # 'average' o default  
        target_width = int(sum(all_widths) / len(all_widths))  
        target_height = int(sum(all_heights) / len(all_heights))  
      
    print(f"Dimensioni target: {target_width}x{target_height}")  
      
    # Carica e processa le immagini  
    images = []  
    for img_path in valid_image_paths:  
        try:  
            with Image.open(img_path) as img:  
                # Converti in RGB se necessario  
                if img.mode != 'RGB':  
                    img = img.convert('RGB')  
                  
                # Ridimensiona l'immagine  
                img_resized = img.resize((target_width, target_height), Image.LANCZOS)  
                  
                # Converti in array numpy  
                img_array = np.array(img_resized)  
                images.append(img_array)  
        except Exception as e:  
            print(f"Errore nel processamento dell'immagine {os.path.basename(img_path)}: {e}")  
      
    if not images:  
        print("Nessuna immagine è stata processata correttamente.")  
        return None  
      
    print(f"Processate con successo {len(images)} immagini.")  
      
    # Fusione delle immagini in base al metodo scelto  
    if blend_method == 'average':  
        # Media tradizionale  
        result = np.mean(np.array(images, dtype=np.float32), axis=0).astype(np.uint8)  
      
    elif blend_method == 'additive':  
        # Somma le immagini e normalizza  
        result = np.zeros_like(images[0], dtype=np.float32)  
        for img in images:  
            result += img.astype(np.float32) * intensity  
          
        # Normalizzazione con saturazione per mantenere colori vividi  
        result = np.clip(result / (len(images) * intensity/2), 0, 255).astype(np.uint8)  
      
    elif blend_method == 'screen':  
        # Effetto screen (simile a proiettori sovrapposti)  
        result = np.ones_like(images[0], dtype=np.float32) * 255  
        for img in images:  
            img_norm = img.astype(np.float32) / 255  
            result_norm = result / 255  
            result = (1 - (1 - result_norm) * (1 - img_norm)) * 255  
        result = result.astype(np.uint8)  

    elif blend_method == 'difference':  
        # Crea effetti di differenza tra le immagini  
        result = images[0].astype(np.float32)  
        for img in images[1:]:  
            result = np.abs(result - img.astype(np.float32)) * intensity  
        result = np.clip(result, 0, 255).astype(np.uint8)  

    elif blend_method == 'multiply':  
        # Effetto multiply (simile a filtri sovrapposti)  
        result = np.ones_like(images[0], dtype=np.float32) * 255  
        for img in images:  
            img_norm = img.astype(np.float32) / 255  
            result_norm = result / 255  
            result = (result_norm * img_norm) * 255  
        result = result.astype(np.uint8)  
      
    elif blend_method == 'overlay':  
        # Overlay con maggiore contrasto  
        result = images[0].astype(np.float32)  
        for i in range(1, len(images)):  
            img = images[i].astype(np.float32)  
            mask = result > 127.5  
            result[mask] = (1 - (1 - 2*(result[mask]/255 - 0.5)) * (1 - img[mask]/255)) * 255  
            result[~mask] = (2 * result[~mask]/255 * img[~mask]/255) * 255  
        result = np.clip(result, 0, 255).astype(np.uint8)  
      
    else:  
        # Default: media  
        result = np.mean(np.array(images, dtype=np.float32), axis=0).astype(np.uint8)  
      
    return result, target_width, target_height  
  
def main():  
    # Ottieni la cartella delle immagini  
    if len(sys.argv) > 1:  
        image_folder = sys.argv[1]  
    else:  
        image_folder = input("Inserisci il percorso della cartella contenente le immagini (premi Invio per usare la cartella corrente): ").strip()  
        if not image_folder:  
            image_folder = './'  
      
    # Ottieni il metodo di fusione  
    blend_method = 'additive'  # default  
    if len(sys.argv) > 2:  
        method_arg = sys.argv[2].lower()  
        if method_arg in ['average', 'additive', 'screen', 'multiply', 'overlay']:  
            blend_method = method_arg  
    else:  
        print("Metodi di fusione disponibili:")  
        print("1. additive - Somma le immagini (default)")  
        print("2. average - Media tradizionale")  
        print("3. screen - Simile a proiettori sovrapposti")  
        print("4. multiply - Simile a filtri sovrapposti")  
        print("5. overlay - Fusione con maggiore contrasto")  
        print("6. difference - Fusione con differenza")  
        choice = input("Scegli un metodo (1-6): ").strip()  
        methods = ['additive', 'average', 'screen', 'multiply', 'overlay', 'difference']  
        if choice.isdigit() and 1 <= int(choice) <= 6:  
            blend_method = methods[int(choice)-1]  
      
    # Calcola l'immagine fusa  
    result = blend_images(image_folder, blend_method=blend_method)  
      
    if result is not None:  
        fused_image, width, height = result  
          
        # Salva l'immagine fusa  
        output_path = os.path.join(image_folder, f'immagine_fusa_{blend_method}.png')  
        Image.fromarray(fused_image).save(output_path)  
        print(f"Immagine fusa salvata come: {output_path}")  
          
        # Visualizza l'immagine  
        plt.figure(figsize=(10, 8))  
        plt.imshow(fused_image)  
        plt.title(f'Immagine Fusa - Metodo: {blend_method} ({width}x{height})')  
        plt.axis('off')  
        plt.show()  
    else:  
        print("Impossibile creare l'immagine fusa.")  
  
if __name__ == "__main__":  
    main()  