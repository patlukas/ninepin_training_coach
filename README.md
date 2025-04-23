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

| Opcja | Opis                                            |
| ----- | ----------------------------------------------- |
| 1     | Przy zmianie ustaw następny układ jako 000      |
| 2     | Przy zmianie ustaw, że zbito wszystkie kręgle   |
| 3     | Przy zmianie ustaw, że nie zbito żadnego kręgla |
| 4     | Podnoś po zmianie                               |
| 5     | Przyspieszony czas                              |
| 6     | Dużo szybszy czas                               |
| 7     | Podnieś po ustawieniu próbnych                  |
| 8     | Podnieś i zatrzymaj po ustawieniu próbnych      |

## Tryby usawiania pełnego układu

* Korekta układu - czyli kombinacja przycisków: "Korekta układu" -> "Clear" -> "Enter"
* Czas stop - czyli kliknięcie przycisku do zatrzymywania czasu
* Podnieś - czyli kliknięcie przycisku do podnoszenia
* Stop - czyli kliknięcie przycisku do zatrzymywania
* Edycja wyniku - czyli przesłanie komunikatu, który odpowiednio zwiększa wynik i edytuje wyświetlany layout

| Opcja | Opis                                                | Ilość komunikatów |
|-------|-----------------------------------------------------|-------------------|
| 1     | Korekta układu -> Edycja wyniku                     | 4                 |
| 2     | Edycja wyniku -> Korekta układu                     | 4                 |
| 3     | Czas stop -> Korekta układu -> Edycja wyniku        | 5                 |
| 4     | Czas stop -> Edycja wyniku -> Korekta układu        | 5                 |
| 5     | Stop -> Korekta układu -> Edycja wyniku -> Podnieś  | 6                 |
| 6     | Stop -> Korekta układu -> Podnieś -> Edycja wyniku  | 6                 |



## 📌 Version History

| Version          | Release Date      | Commits | Changes                                      |
|------------------|-------------------|---------|----------------------------------------------|
| **v1.0.8.0**     | 🚧 In the future  |         |                                              |
| **v1.0.7.0**     | 🚧 In development |         |                                              |
| **v1.0.6.0**     | 2025-04-23        | 50      | Change modes                                 |
| **v1.0.5.1**     | 2025-04-11        | 43      | 32-bit OS compatible exe file                |
| **v1.0.5.0**     | 2025-04-09        | 42      | Add modes & improved result counting         |
| **v1.0.4.0**     | 2025-03-21        | 35      | Change the method of setting the full layout |
| **v1.0.3.0**     | 2025-03-11        | 24      | Added option to control trial attempts       |
| **v1.0.2.1**     | 2025-02-28        | 22      | Added jenkins                                |
| **v1.0.2**       | 2025-02-27        | 18      | Added logs table                             |
| **v1.0.1**       | 2025-02-26        | 9       | Added more freedom to configure              |
| **v1.0.0**       | 2025-02-24        | 4       | 🎉 Initial stable release                    |
| **First commit** | 2025-02-23        | 1       |                                              |

![](https://github.ct8.pl/readme/patlukas/ninepin_training_coach)
