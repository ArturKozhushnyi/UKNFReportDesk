# Specyfikacja Ustandaryzowanego Procesu Wytwarzania Oprogramowania z Wykorzystaniem Modeli AI

## Cel Dokumentu:
Niniejszy dokument standaryzuje proces wytwarzania oprogramowania przy wsparciu modeli AI. Celem jest zdefiniowanie spójnych ram proceduralnych, które zapewnią wysoką efektywność, powtarzalność, jakość i bezpieczeństwo w cyklu życia oprogramowania.

## 1. Wymagania Wstępne

1.1. Środowisko Technologiczne

### Zintegrowane Środowisko Programistyczne (IDE): 
Standardowym środowiskiem jest Cursor AI. Pełni ono rolę platformy dla Egzekutora Promptów, zapewniając automatyczne zarządzanie kontekstem projektu.

### Wersjonowanie Narzędzi: 
Wymagane jest stosowanie najnowszych, stabilnych wersji narzędzi wchodzących w skład zdefiniowanego stosu technologicznego.

### Konfiguracja Modeli Językowych (LLM): 
Standard zakłada wykorzystanie metodologii "double prompting", która separuje role i odpowiedzialności dwóch modeli AI:

### Kreator Promptów (Prompt Creator): 
Rola ta przypisana jest modelowi Google Gemini Pro. Jego zadaniem jest generowanie precyzyjnych, technicznych promptów na podstawie wysoko-poziomowych założeń dostarczonych przez dewelopera.

### Egzekutor Promptów (Prompt Executor): 
Rola ta przypisana jest modelowi Claude 3.5 Sonnet, zintegrowanemu ze środowiskiem Cursor AI. Jego odpowiedzialnością jest interpretacja i wykonanie promptów otrzymanych od Kreatora w celu generowania kodu, testów i dokumentacji.

## 2. Metodologia Promptowania

Proces opiera się na metodyce "divide and conquer". Złożone zadania programistyczne są dekomponowane na mniejsze, zarządzalne jednostki. Kluczowym punktem kontroli jakości jest weryfikacja prompta pośredniego (wygenerowanego przez Kreatora), a nie finalnego kodu, co znacząco optymalizuje pracę dewelopera.

### 2.1. Architektura Interakcji z AI

Zarządzanie Kontekstem: 
Integralną częścią procesu jest zapewnienie modelom AI pełnego kontekstu sytuacyjnego. Kontekst dla Kreatora Promptów jest dostarczany manualnie przez dewelopera i może obejmować fragmenty kodu, definicje schematów baz danych (DDL), diagramy architektury (w formie graficznej) lub poprzez zlecenie pełnej analizy repozytorium kodu. Egzekutor Promptów otrzymuje kontekst z IDE (Cursor AI) w sposób zautomatyzowany.

Przepływ Zadania: Cykl przetwarzania pojedynczego zadania przebiega według schematu:

Deweloper definiuje cel biznesowy lub techniczny.

Kreator Promptów transformuje cel w szczegółową, techniczną instrukcję (prompt).

Deweloper weryfikuje i akceptuje wygenerowany prompt.

Egzekutor Promptów wykonuje prompt, tworząc artefakty programistyczne.

2.2. Przykładowe Prompty Wejściowe (dla Kreatora)

Przykład 1 (Migracja Bazy Danych):
```
# codebase was attached
analyze the code, after analisys finish assignment

Create a prompt for cursor ai, that will create new migration script with 002 number as prefix. This migration script contains resource id and group, resource id is randomly generated (I will provide uuid for it) for each resource, one resource is for example one endpoint in this case like fetch user. Also in this migration script must be group called administrator, this group must be in resource allow list with all new created resources, create this prompt. The prompt should be runnable multiple times without adding new duplicate records
```
   
Przykład 2 (Nowy Endpoint):
```
# context was previosly provided
Create a prompt that will create new endpoint that adds users to groups, this new endpoint needs to have administration group access.

This endpoint should also add new resource id and add this resource id to administrator group

Create prompt 
```

## 3. Integracja z Etapami Cyklu Życia Oprogramowania

### 3.1. Planowanie i Analiza

Metodologia wspiera dekompozycję wymagań. Kreator Promptów może być wykorzystany do generowania sformalizowanych historyjek użytkownika (User Stories) lub zadań do backlogu na podstawie ogólnego opisu funkcjonalności.

### 3.2. Projektowanie Architektoniczne

Na podstawie dostarczonych założeń (np. diagramów, opisu wzorców projektowych), Kreator Promptów generuje instrukcje dla Egzekutora w celu stworzenia szkieletów kodu, schematów klas, definicji baz danych lub całej struktury projektu zgodnie z przyjętą architekturą (np. DDD, mikroserwisy).

### 3.3. Implementacja (Kodowanie)

Faza implementacji przebiega iteracyjnie zgodnie z opisanym w sekcji 2.1 przepływem zadania. Ciągłość pracy i spójność kodu są zapewnione przez mechanizm "odświeżania pamięci" modeli, polegający na regularnym dostarczaniu aktualnego stanu bazy kodowej.

### 3.4. Testowanie i Zapewnienie Jakości

Generowanie testów jest nieodłącznym elementem cyklu. Każde zadanie implementacyjne pociąga za sobą zlecenie Kreatorowi Promptów stworzenia instrukcji dla Egzekutora w celu wyprodukowania adekwatnych testów jednostkowych lub komponentowych. Testy te stanowią formalny mechanizm weryfikacji poprawności kodu generowanego przez AI.

### 3.5. Dokumentacja

Proces zakłada tworzenie dokumentacji równolegle z kodem. Egzekutor jest zobligowany do generowania opisów technicznych dla nowo powstałych funkcjonalności. Dokumentacja ta jest składowana w dedykowanej lokalizacji (/docs) i stanowi część kontekstu dla przyszłych zadań, tworząc samodoskonalącą się bazę wiedzy o projekcie.

### 3.6. Refaktoryzacja i Utrzymanie

Zadania refaktoryzacyjne i utrzymaniowe są realizowane przy użyciu tej samej metodologii.

Procedura obsługi limitu kontekstu: W przypadku osiągnięcia limitu tokenów w sesji z modelem AI, standardową procedurą jest inicjalizacja nowej sesji. Musi być ona obligatoryjnie poprzedzona ponowną, pełną analizą repozytorium kodu w celu odbudowy bazy wiedzy modelu.

