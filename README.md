# YADRO_project
This project develops an algorithm combining soft decisions from GSM demodulators across multiple base station sectors. Processing the same signal from different angles, it intelligently merges soft bit streams to maximize SNR and significantly improve demodulation reliability in challenging environments with interference or fading.

Пояснения к архитектуре проекта: 

Project/
│
├── main.py  - файл для сборки всей системы в едино
│
├── core/ - папка для слежбных компоненотов 
│   ├── __init__.py
│   ├── block.py - класс наследования(обеспечивает единый интерфейс для всех блоков)
│   └── pipeline.py - соединяет все блоки в систему передачи
│
├── transmitter/ - приёмник 
│   ├── __init__.py
│   ├── source.py
│   ├── channel_coder.py
│   ├── interleaver.py
│   └── modulator.py
│
└── receiver/ - передатчик 
│   ├── __init__.py
│   ├── demodulator.py
│   └── decoder.py
│
└── drawber/ - графики для контроля качества 
    ├── __init__.py
    └── ber.py
