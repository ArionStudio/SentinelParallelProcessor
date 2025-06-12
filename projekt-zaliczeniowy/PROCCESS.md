# POBIERANIE DANYCH Z SENTINEL 2

Do wykonania tego zadania użyliśmy API którego dokumentacja znajduje się

https://docs.sentinel-hub.com/api/latest/data/sentinel-2-l2a/

Do pozyskiwania danych wymagane jest założenie konta.
Następnie musimy utworzyc OAuth clienta i przy pomocy zapytania zautoryzować się
Dokładne kroki które trzeba wykonać są opisane tutaj.
https://docs.sentinel-hub.com/api/latest/api/overview/authentication/

W zakładce https://docs.sentinel-hub.com/api/latest/api/overview/rate-limiting/ możemy dowiedzieć się
o ograniczeniach dostępu ustawionych dla API. Z tego też powodu dla naszego zadania najlepszym rozwiązaniem będzie zapisywanie pobieranych danych trwale i uzyskiwanie do nich dostępu a jeśli nie ma oczekiwanych przez nas danych w tym wypadku pobieranie ich z api.

Ważne jest by zapisane dane nie trafiały do repozytorium by go nie zaśmiecać.

Dla uproszczenia korzystania z aplikacji nasze dane dostępowe będziemy trzymać lokalnie zaszyfrowane.
Interfejs więc powinien pozwolić nam uzyskać dostęp do tych danych po ich uzupełnieniu a później po wpisaniu hasła dostępu je wykorzystać. Hasło jest tu istotne ponieważ przechowujemy wrażliwe dane i nie chcemy by były przechowywane w plaintext

By przeprowadzić ten proces potrzebujemy stworzyć wstępny ekran aplikacji który pobierze od nas dane dostępu oraz hasło 
