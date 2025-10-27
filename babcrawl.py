#!/usr/bin/env python3
"""
Babbel Vokabel Extraktor
Extrahiert deutsch-portugiesische Vokabelpaare aus kopierten Babbel-Texten.
"""

import argparse
import csv
import re
from pathlib import Path


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
            
            # Muster: Portugiesisch (erste Zeile) → Deutsch (zweite Zeile)
            # Portugiesisch beginnt meist mit Kleinbuchstaben (außer Eigennamen)
            # oder hat portugiesische Artikel (a, o, as, os)
            is_portuguese = (
                line.startswith(('a ', 'o ', 'as ', 'os ', 'um ', 'uma ')) or
                line[0].islower() or
                any(char in line for char in ['ã', 'õ', 'ç', 'á', 'é', 'í', 'ó', 'ú'])
            )
            
            # Deutsch beginnt meist mit Großbuchstaben (Substantive)
            # oder hat deutsche Artikel (der, die, das, den, dem, ein, eine)
            is_german = next_line.startswith(('der ', 'die ', 'das ', 'den ', 'dem ', 
                                               'ein ', 'eine ', 'einen ', 'einem ',
                                               'Der ', 'Die ', 'Das '))
            
            # Wenn wir ein Paar gefunden haben
            if is_portuguese or (not line[0].isupper() and next_line[0].isupper()):
                portuguese = line
                german = next_line
                vocabulary.append((german, portuguese))
                i += 2  # Überspringe beide Zeilen
                continue
        
        i += 1
    
    return vocabulary


def save_to_csv(vocabulary, output_file):
    """
    Speichert Vokabeln in CSV-Datei.
    
    Args:
        vocabulary: Liste von Tupeln (deutsch, portugiesisch)
        output_file: Pfad zur Ausgabedatei
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Deutsch', 'Portugiesisch'])
        writer.writerows(vocabulary)
    
    print(f"✓ {len(vocabulary)} Vokabelpaare wurden in '{output_file}' gespeichert.")


def main():
    parser = argparse.ArgumentParser(
        description='Extrahiert deutsch-portugiesische Vokabeln aus kopierten Babbel-Texten.'
    )
    parser.add_argument(
        'input_file',
        help='Pfad zur Text-Eingabedatei (kopierter Inhalt von Babbel)'
    )
    parser.add_argument(
        '-o', '--output',
        default='vokabeln.csv',
        help='Name der CSV-Ausgabedatei (Standard: vokabeln.csv)'
    )
    
    args = parser.parse_args()
    
    # Eingabedatei lesen
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"✗ Fehler: Datei '{args.input_file}' wurde nicht gefunden.")
        return 1
    
    print(f"Lese Datei: {args.input_file}")
    with open(input_path, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    # Vokabeln extrahieren
    vocabulary = extract_vocabulary(text_content)
    
    if not vocabulary:
        print("⚠ Warnung: Keine Vokabeln gefunden!")
        return 1
    
    # CSV speichern
    save_to_csv(vocabulary, args.output)
    
    # Zeige erste 5 Einträge als Vorschau
    print("\nVorschau (erste 5 Einträge):")
    for i, (german, portuguese) in enumerate(vocabulary[:5], 1):
        print(f"{i}. {german} | {portuguese}")
    
    return 0


if __name__ == '__main__':
    exit(main())