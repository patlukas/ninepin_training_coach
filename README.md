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

| Opcja                                        | Opis                             | Domyślne |
|----------------------------------------------|----------------------------------|----------|
| Przy zmianie: następny układ:                |                                  |          |
|                                              | nie zmieniaj                     |          |
|                                              | ustaw jako 000                   | Tak      |
|                                              | ustaw jako 001                   |          |
|                                              |                                  |          |
| Przy zmienie: zbite:                         |                                  | Tak      |
|                                              | nie zmieniaj                     | Tak      |
|                                              | ustaw że zbito wszystkie kręgle  |          |
|                                              | ustaw że nie zbito żadego kręgle |          |
|                                              | ustaw że zbito układ 001         |          |
|                                              |                                  |          |
| Przy zmianie: dodaj liczbę usuwanych kręgli: |                                  | Tak      |
|                                              | Nie                              | Tak      |
|                                              | Tak                              |          |
|                                              |                                  |          |
| Przyśpieszony czas                           |                                  |          |
|                                              | Nie                              | Tak      |
|                                              | Szybszy czas [0.1]               |          |
|                                              | Dużo szybszy czas [1.0]          |          |
|                                              | Ekstremalnie szybki czas [5.0]   |          |
|                                              |                                  |          |
| Próbne:                                      |                                  |          |
|                                              | Bez zmian                        | Tak      |
|                                              | Podnieś                          |          |
|                                              | Podnieś i zatrzymaj              |          |
|                                              |                                  |          |
| Czas przerwy między wiadomościami:           |                                  |          |
|                                              | 0.05s                            |          |
|                                              | 0.1s                             |          |
|                                              | 0.2s                             |          |
|                                              | 0.3s                             | Tak      |
|                                              | 0.5s                             |          |
|                                              | 0.75s                            |          |
|                                              | 1.5s                             |          |
|                                              | 3.0s                             |          |
|                                              | 5.0s                             |          |

## Tryby usawiania pełnego układu

* Edycja_wyniku - czyli przesłanie komunikatu, który odpowiednio zwiększa wynik i edytuje wyświetlany layout

| Opcja | Opis                                                                        | Minimalny czas [ms] |
| ----- | --------------------------------------------------------------------------- | ------------------- |


## 📌 Version History

| Version          | Release Date      | Commits | Changes                                                                    |
|------------------|-------------------|---------|----------------------------------------------------------------------------|
| **v1.1.6.0**     | 🚧 In the future  |         |                                                                            |
| **v1.1.5.0**     | 🚧 In development |         |                                                                            |
| **v1.1.4.0**     | 2025-11-18        | 108     | New modes and possibility to send many messages in one time                |
| **v1.1.3.0**     | 2025-11-13        | 104     | Add more new modes                                                         |
| **v1.1.2.0**     | 2025-11-13        | 103     | Add more new modes                                                         |
| **v1.1.0.1**     | 2025-11-06        | 98      | Correct func to set full layout                                            |
| **v1.1.0.0**     | 2025-11-04        | 96      | Change method to recv/send message to lane                                 |
| **v1.0.12.1**    | 2025-10-21        | 90      | Add modes form v1.0.12 to menu bar                                         |
| **v1.0.12.0**    | 2025-10-21        | 88      | New modes added - same like v1.0.11.0                                      |
| **v1.0.11.0**    | 2025-10-16        | 86      | New modes added                                                            |      
| **v1.0.10.2**    | 2025-05-14        | 83      | Reorganized options on the menu bar                                        |      
| **v1.0.10.1**    | 2025-05-11        | 80      | Add new option to set full layout in settings                              |      
| **v1.0.10.0**    | 2025-05-10        | 77      | Add option to set time between messages                                    |
| **v1.0.9.3**     | 2025-05-10        | 76      | Add option to show button to start trial                                   |
| **v1.0.9.2**     | 2025-05-09        | 74      | Fix critical bug                                                           |
| **v1.0.9.1**     | 2025-05-09        | 72      | ❌ Broken version - Fix Jenkins                                             |
| **v1.0.9.0**     | 2025-05-09        | 68      | ❌ Broken version - New modes added, fix "Optymistyczne zbierane", add icon |
| **v1.0.8.0**     | 2025-04-25        | 59      | New modes added                                                            |
| **v1.0.7.0**     | 2025-04-25        | 56      | New modes added, fixed critical bug from 1.0.6.0                           |
| **v1.0.6.0**     | 2025-04-23        | 51      | ❌ Broken version - Change modes                                            |
| **v1.0.5.1**     | 2025-04-11        | 43      | 32-bit OS compatible exe file                                              |
| **v1.0.5.0**     | 2025-04-09        | 42      | Add modes & improved result counting                                       |
| **v1.0.4.0**     | 2025-03-21        | 35      | Change the method of setting the full layout                               |
| **v1.0.3.0**     | 2025-03-11        | 24      | Added option to control trial attempts                                     |
| **v1.0.2.1**     | 2025-02-28        | 22      | Added jenkins                                                              |
| **v1.0.2**       | 2025-02-27        | 18      | Added logs table                                                           |
| **v1.0.1**       | 2025-02-26        | 9       | Added more freedom to configure                                            |
| **v1.0.0**       | 2025-02-24        | 4       | 🎉 Initial stable release                                                  |
| **First commit** | 2025-02-23        | 1       |                                                                            |

![](https://github.ct8.pl/readme/patlukas/ninepin_training_coach)
