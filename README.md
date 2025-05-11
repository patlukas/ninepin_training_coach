![GitHub release (latest by date)](https://img.shields.io/github/v/release/patlukas/ninepin_training_coach?label=Latest%20Release)
![GitHub file count](https://img.shields.io/github/directory-file-count/patlukas/ninepin_training_coach)
![GitHub issues](https://img.shields.io/github/issues/patlukas/ninepin_training_coach)

# Ninepin Training Coach

## Opis projektu

**Ninepin Training Coach** to aplikacja napisana w Pythonie 3.4, zaprojektowana do działania na systemie Windows XP. Program umożliwia uruchomienie dostosowanych trybów treningowych na kręgielni klasycznej, pozwalając na manipulację ustawieniami toru oraz warunkami gry.

## Wymagania systemowe

- System operacyjny: **Windows XP** lub nowszy
- Python: **3.4.3**
- Biblioteki: Brak zewnętrznych zależności

## Instalacja i uruchomienie

1. Pobierz i zainstaluj **Python 3.4.3** na Windows XP (jeśli jeszcze nie jest zainstalowany).
2. Pobierz pliki projektu.
3. Uruchom program w wierszu poleceń:
   ```sh
   python ninepin_training_coach.py
   ```

## Opcje dostępne w programie

Program oferuje następujące tryby i modyfikacje gry:

| Opcja | Opis                                                  | Domyślne |
|-------|-------------------------------------------------------|----------|
| 1.a   | Przy zmianie: następny układ: nie zmieniaj            |          |
| 1.b   | Przy zmienie: następny układ: ustaw jako 000          | Tak      |
|       |                                                       |          |
| 2.a   | Przy zmienie: zbite: nie zmieniaj                     | Tak      |
| 2.b   | Przy zmienie: zbite: ustaw że zbito wszystkie kręgle  |          |
| 2.c   | Przy zmienie: zbite: ustaw że nie zbito żadego kręgle |          |
| 2.d   | Przy zmienie: zbite: ustaw że zbito układ 001         |          |
|       |                                                       |          |
| 3.a   | Przy zmianie: dodaj liczbę usuwanych kręgli: Nie      | Tak      |
| 3.b   | Przy zmianie: dodaj liczbę usuwanych kręgli: Tak      |          |
|       |                                                       |          |
| 4.a   | Normalny czas                                         | Tak      |
| 4.b   | Przyspieszony czas [0.1]                              |          |
| 4.c   | Dużo szybszy czas [1.0]                               |          |
| 4.d   | Ekstremalnie szybki czas [5.0]                        |          |
|       |                                                       |          |
| 5.a   | Próbne: Bez zmian                                     | Tak      |
| 5.b   | Próbne: Podnieś                                       |          |
| 5.c   | Próbne: Podnieś i zatrzymaj                           |          |
|       |                                                       |          |
| 6.a   | Czas przerwy między wiadomościami: 0.05               |          |
| 6.b   | Czas przerwy między wiadomościami: 0.1                |          |
| 6.c   | Czas przerwy między wiadomościami: 0.2                |          |
| 6.d   | Czas przerwy między wiadomościami: 0.3 (default)      | Tak      |
| 6.e   | Czas przerwy między wiadomościami: 0.5                |          |
| 6.f   | Czas przerwy między wiadomościami: 0.75               |          |
| 6.g   | Czas przerwy między wiadomościami: 1.5                |          |
| 6.h   | Czas przerwy między wiadomościami: 3.0                |          |
| 6.i   | Czas przerwy między wiadomościami: 5.0                |          |

## Tryby usawiania pełnego układu

* Korekta układu - czyli kombinacja przycisków: "B_Korekta układu" -> "Clear" -> "Enter"
* Czas stop - czyli kliknięcie przycisku do zatrzymywania czasu
* Podnieś - czyli kliknięcie przycisku do podnoszenia
* Stop - czyli kliknięcie przycisku do zatrzymywania
* Edycja wyniku - czyli przesłanie komunikatu, który odpowiednio zwiększa wynik i edytuje wyświetlany layout

| Opcja | Opis                                                             | Ilość komunikatów |
|-------|------------------------------------------------------------------|-------------------|
| 1     | Stop -> Korekta układu -> Edycja wyniku -> Podnieś               | 6                 |
| 2     | Stop -> Korekta układu -> Podnieś -> Edycja wyniku               | 6                 |
| 3     | Edycja wyniku -> Stop -> Korekta układu -> Podnieś               | 6                 |
| 4     | Stop -> Edycja wyniku -> Korekta układu -> Podnieś               | 6                 |
| 5     | Stop -> Czas stop -> Korekta układu -> Edycja wyniku -> Podnieś  | 7                 |
| 6     | Stop -> Czas stop -> Korekta układu -> Podnieś -> Edycja wyniku  | 7                 |
| 7     | Stop -> Edycja wyniku  -> B_Korekta układu -> Enter -> Podnieś   | 5                 |



## 📌 Version History

| Version          | Release Date     | Commits | Changes                                                                    |
|------------------|------------------|---------|----------------------------------------------------------------------------|
| **v1.0.11.0**    | 🚧 In the future |         |                                                                            |
| **v1.0.10.0**    | 2025-05-10       | 77      | Add option to set time between messages                                    |
| **v1.0.9.3**     | 2025-05-10       | 76      | Add option to show button to start trial                                   |
| **v1.0.9.2**     | 2025-05-09       | 74      | Fix critical bug                                                           |
| **v1.0.9.1**     | 2025-05-09       | 72      | ❌ Broken version - Fix Jenkins                                             |
| **v1.0.9.0**     | 2025-05-09       | 68      | ❌ Broken version - New modes added, fix "Optymistyczne zbierane", add icon |
| **v1.0.8.0**     | 2025-04-25       | 59      | New modes added                                                            |
| **v1.0.7.0**     | 2025-04-25       | 56      | New modes added, fixed critical bug from 1.0.6.0                           |
| **v1.0.6.0**     | 2025-04-23       | 51      | ❌ Broken version - Change modes                                            |
| **v1.0.5.1**     | 2025-04-11       | 43      | 32-bit OS compatible exe file                                              |
| **v1.0.5.0**     | 2025-04-09       | 42      | Add modes & improved result counting                                       |
| **v1.0.4.0**     | 2025-03-21       | 35      | Change the method of setting the full layout                               |
| **v1.0.3.0**     | 2025-03-11       | 24      | Added option to control trial attempts                                     |
| **v1.0.2.1**     | 2025-02-28       | 22      | Added jenkins                                                              |
| **v1.0.2**       | 2025-02-27       | 18      | Added logs table                                                           |
| **v1.0.1**       | 2025-02-26       | 9       | Added more freedom to configure                                            |
| **v1.0.0**       | 2025-02-24       | 4       | 🎉 Initial stable release                                                  |
| **First commit** | 2025-02-23       | 1       |                                                                            |

![](https://github.ct8.pl/readme/patlukas/ninepin_training_coach)
