#!/usr/bin/env python3
"""
Babbel Batch Vokabel Extraktor
Extrahiert Vokabeln aus mehreren Textdateien und erstellt eine CSV.
"""

import argparse
import csv
from pathlib import Path
from tkinter import Tk, filedialog


def extract_vocabulary(text_content):
    """
    Extrahiert Vokabelpaare aus dem kopierten Babbel-Text.
    
    Args:
        text_content: Der Text-Inhalt als String
        
    Returns:
        Liste von Tupeln (deutsch, portugiesisch)
    """
    vocabulary = []
    lines = text_content.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Überspringe leere Zeilen und Überschriften
        if not line or line in ['Home', 'Üben', 'Entdecken', 'Alle Vokabeln', 
                                 'Auswählen', 'Alle', 'Schwach', 'Mittel', 'Stark']:
            i += 1
            continue
        
        # Überspringe Footer-Bereiche
        if 'Lernen mit Babbel' in line or 'Babbel-App' in line or 'Imprint' in line:
            break
        
        # Überspringe Beschreibungstexte
        if line.endswith('.') and any(x in line for x in ['Alle Wörter', 'Speichere', 'Vokabeln pro Seite']):
            i += 1
            continue
        
        # Überspringe Zahlen am Anfang (wie "508")
        if line.isdigit():
            i += 1
            continue
        
        # Prüfe ob die nächste Zeile existiert
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            
            # Skip wenn beide Zeilen leer oder zu kurz sind
            if not next_line or len(line) < 2:
                i += 1
                continue
            
            # Deutsche Indikatoren
            has_german_article = next_line.startswith(('der ', 'die ', 'das ', 'den ', 'dem ', 
                                                        'ein ', 'eine ', 'einen ', 'einem ',
                                                        'Der ', 'Die ', 'Das '))
            has_german_chars = any(char in next_line for char in ['ä', 'ö', 'ü', 'ß'])
            
            # Portugiesische Indikatoren
            has_portuguese_article = line.startswith(('a ', 'o ', 'as ', 'os ', 'um ', 'uma '))
            has_portuguese_chars = any(char in line for char in ['ã', 'õ', 'ç', 'á', 'é', 'í', 'ó', 'ú'])
            starts_lowercase = line[0].islower()
            
            # Heuristik: Ist es wahrscheinlich ein Vokabelpaar?
            # Fall 1: Klare portugiesische und deutsche Merkmale
            if (has_portuguese_article or has_portuguese_chars or starts_lowercase) and \
               (has_german_article or has_german_chars):
                vocabulary.append((next_line, line))
                i += 2
                continue
            
            # Fall 2: Keine speziellen Merkmale, aber strukturell passend
            # (z.B. "Oi!" und "Hallo!" - beide kurze Ausrufe)
            # Prüfe ob es aussieht wie ein Vokabelpaar (ähnliche Länge, keine Footer-Keywords)
            is_not_navigation = not any(keyword in line for keyword in 
                                       ['Lernen mit', 'Babbel', 'Karriere', 'Imprint', 'AGB'])
            is_not_navigation2 = not any(keyword in next_line for keyword in 
                                        ['Lernen mit', 'Babbel', 'Karriere', 'Imprint', 'AGB'])
            
            # Wenn beide Zeilen kurz sind (unter 50 Zeichen) und keine Navigation
            if len(line) < 50 and len(next_line) < 50 and is_not_navigation and is_not_navigation2:
                # Annahme: Erste Zeile = Portugiesisch, Zweite = Deutsch
                vocabulary.append((next_line, line))
                i += 2
                continue
        
        i += 1
    
    return vocabulary


def process_files(file_paths):
    """
    Verarbeitet mehrere Textdateien und extrahiert alle Vokabeln.
    
    Args:
        file_paths: Liste von Pfaden zu Textdateien
        
    Returns:
        Liste von eindeutigen Tupeln (deutsch, portugiesisch)
    """
    all_vocabulary = []
    
    for file_path in file_paths:
        print(f"Verarbeite: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            vocab = extract_vocabulary(text_content)
            all_vocabulary.extend(vocab)
            print(f"  → {len(vocab)} Vokabelpaare gefunden")
        except Exception as e:
            print(f"  ✗ Fehler: {e}")
    
    # Entferne Duplikate und sortiere alphabetisch
    unique_vocabulary = sorted(set(all_vocabulary), key=lambda x: x[0].lower())
    
    duplicates_removed = len(all_vocabulary) - len(unique_vocabulary)
    
    print(f"\nGesamt: {len(all_vocabulary)} Vokabelpaare")
    print(f"Duplikate entfernt: {duplicates_removed}")
    print(f"Eindeutige Vokabeln: {len(unique_vocabulary)}")
    
    return unique_vocabulary


def save_to_csv(vocabulary, output_file):
    """
    Speichert Vokabeln in CSV-Datei.
    
    Args:
        vocabulary: Liste von Tupeln (deutsch, portugiesisch)
        output_file: Pfad zur Ausgabedatei
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Deutsch', 'Portugiesisch'])
        writer.writerows(vocabulary)
    
    print(f"\n✓ {len(vocabulary)} Vokabeln wurden in '{output_file}' gespeichert.")


def select_files_dialog():
    """
    Öffnet einen Dateiauswahl-Dialog.
    
    Returns:
        Liste von ausgewählten Dateipfaden
    """
    root = Tk()
    root.withdraw()  # Verstecke das Hauptfenster
    root.attributes('-topmost', True)  # Bringe Dialog nach vorne
    
    file_paths = filedialog.askopenfilenames(
        title='Wähle Babbel-Textdateien aus',
        filetypes=[
            ('Textdateien', '*.txt'),
            ('Alle Dateien', '*.*')
        ]
    )
    
    root.destroy()
    return list(file_paths)


def main():
    parser = argparse.ArgumentParser(
        description='Extrahiert Vokabeln aus mehreren Babbel-Textdateien und erstellt eine CSV.'
    )
    parser.add_argument(
        'input_files',
        nargs='*',
        help='Textdateien zum Verarbeiten (optional, ohne Angabe öffnet sich ein Dialog)'
    )
    parser.add_argument(
        '-o', '--output',
        default='alle_vokabeln.csv',
        help='Name der CSV-Ausgabedatei (Standard: alle_vokabeln.csv)'
    )
    parser.add_argument(
        '-g', '--gui',
        action='store_true',
        help='Dateiauswahl-Dialog öffnen (auch wenn Dateien angegeben wurden)'
    )
    
    args = parser.parse_args()
    
    # Bestimme welche Dateien verarbeitet werden sollen
    if args.gui or not args.input_files:
        print("Öffne Dateiauswahl-Dialog...")
        file_paths = select_files_dialog()
        if not file_paths:
            print("Keine Dateien ausgewählt. Abbruch.")
            return 1
    else:
        file_paths = args.input_files
    
    # Prüfe ob Dateien existieren
    valid_files = []
    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            print(f"✗ Warnung: Datei '{file_path}' nicht gefunden, wird übersprungen.")
        else:
            valid_files.append(path)
    
    if not valid_files:
        print("✗ Fehler: Keine gültigen Dateien gefunden.")
        return 1
    
    print(f"\nVerarbeite {len(valid_files)} Datei(en)...\n")
    
    # Verarbeite alle Dateien
    vocabulary = process_files(valid_files)
    
    if not vocabulary:
        print("✗ Fehler: Keine Vokabeln gefunden.")
        return 1
    
    # Speichere das Ergebnis
    save_to_csv(vocabulary, args.output)
    
    # Zeige erste 5 Einträge als Vorschau
    print("\nVorschau (erste 5 Einträge):")
    for i, (german, portuguese) in enumerate(vocabulary[:5], 1):
        print(f"{i}. {german} | {portuguese}")
    
    return 0


if __name__ == '__main__':
    exit(main())