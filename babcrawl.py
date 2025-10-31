import tkinter as tk
from tkinter import filedialog
import csv
import re

def extract_vocabulary_pairs(text):
    """
    Extrahiert Vokabelpaare aus dem Text zwischen den Markierungen.
    """
    # Finde den Bereich zwischen den beiden Markierungen
    start_marker = "Speichere Wörter und Sätze, damit du sie jederzeit wiederholen kannst."
    end_marker = "Vokabeln pro Seite"
    
    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("Warnung: Marker nicht gefunden!")
        return []
    
    # Extrahiere den relevanten Teil
    vocab_section = text[start_idx + len(start_marker):end_idx].strip()
    
    # Teile in Zeilen auf
    lines = vocab_section.split('\n')
    
    vocab_pairs = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Überspringe leere Zeilen
        if not line:
            i += 1
            continue
        
        # Portugiesische Zeile (kann mehrere Wörter haben)
        portuguese = line
        
        # Nächste Zeile sollte die deutsche Übersetzung sein
        if i + 1 < len(lines):
            german = lines[i + 1].strip()
            
            # Füge das Paar hinzu, wenn beide vorhanden sind
            if portuguese and german:
                vocab_pairs.append((portuguese, german))
            
            i += 2  # Springe zum nächsten Paar
        else:
            i += 1
    
    return vocab_pairs

def convert_txt_to_csv():
    """
    Hauptfunktion: Öffnet Dateidialog, verarbeitet Dateien und erstellt CSV.
    """
    # Erstelle ein verstecktes Tkinter-Fenster
    root = tk.Tk()
    root.withdraw()
    
    # Öffne Dateidialog zur Auswahl mehrerer TXT-Dateien
    file_paths = filedialog.askopenfilenames(
        title="Wähle Babbel Vokabel-Dateien aus",
        filetypes=[("Text-Dateien", "*.txt"), ("Alle Dateien", "*.*")]
    )
    
    if not file_paths:
        print("Keine Dateien ausgewählt.")
        return
    
    # Sammle alle Vokabelpaare
    all_vocab_pairs = []
    
    for file_path in file_paths:
        print(f"Verarbeite: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                pairs = extract_vocabulary_pairs(text)
                all_vocab_pairs.extend(pairs)
                print(f"  → {len(pairs)} Vokabelpaare gefunden")
        except Exception as e:
            print(f"Fehler beim Verarbeiten von {file_path}: {e}")
    
    if not all_vocab_pairs:
        print("Keine Vokabelpaare gefunden!")
        return
    
    # Frage nach Speicherort für CSV
    csv_path = filedialog.asksaveasfilename(
        title="CSV-Datei speichern unter",
        defaultextension=".csv",
        filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")]
    )
    
    if not csv_path:
        print("Kein Speicherort ausgewählt.")
        return
    
    # Schreibe CSV-Datei
    try:
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            
            # Schreibe Header
            # writer.writerow(['Portugiesisch', 'Deutsch'])
            
            # Schreibe Vokabelpaare
            writer.writerows(all_vocab_pairs)
        
        print(f"\n✓ CSV erfolgreich erstellt: {csv_path}")
        print(f"✓ Insgesamt {len(all_vocab_pairs)} Vokabelpaare exportiert")
        
    except Exception as e:
        print(f"Fehler beim Schreiben der CSV: {e}")

if __name__ == "__main__":
    print("Babbel Vokabel-Konverter")
    print("=" * 50)
    convert_txt_to_csv()
    print("\nFertig!")