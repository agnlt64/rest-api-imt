# UE-AD-A1-REST

Application de gestion d'un cinéma découpée en quatre micro-services REST écrits en Python avec Flask. Chaque service gère ses propres données et communique avec les autres par HTTP.

Projet réalisé dans le cadre de l'UE Architecture distribuée (IMT).

## Fonctionnalités

- **Movie** : catalogue des films (ajout, suppression, recherche par id ou par titre, mise à jour de la note).
- **Schedule** : programmation des films par date. Seul un administrateur peut ajouter ou retirer des films d'une date.
- **Booking** : réservations des utilisateurs. Une réservation n'est acceptée que si les films demandés sont bien programmés à la date choisie.
- **User** : gestion des utilisateurs et de leur rôle (`user` ou `admin`).

## Architecture

```
                 ┌──────────────┐
                 │   Booking    │ :3201
                 └──────┬───────┘
                        │ vérifie la programmation
                        ▼
┌──────────────┐  ┌──────────────┐  vérifie les films  ┌──────────────┐
│     User     │◄─┤   Schedule   ├────────────────────►│    Movie     │
│    :3203     │  │    :3202     │                     │    :3200     │
└──────────────┘  └──────────────┘                     └──────────────┘
  vérifie le rôle admin
```

| Service  | Port | Dossier      | Données                         | Appelle            |
|----------|------|--------------|---------------------------------|--------------------|
| Movie    | 3200 | `movie/`     | `databases/movies.json`         | –                  |
| Booking  | 3201 | `booking/`   | `databases/bookings.json`       | Schedule           |
| Schedule | 3202 | `schedule/`  | `databases/times.json`          | Movie, User        |
| User     | 3203 | `user/`      | `databases/users.json`          | –                  |

Chaque service :

- est une application Flask indépendante (`<service>/<service>.py`) ;
- stocke ses données dans un fichier JSON chargé au démarrage et réécrit à chaque modification ;
- décrit son API dans `<service>/openapi.yaml` (OpenAPI), lisible avec [Swagger Editor](https://editor.swagger.io/) par exemple ;
- possède un `Dockerfile` (encore à compléter).

### Interactions entre services

- `POST /bookings/create-booking/<userid>` sur **Booking** appelle `GET /schedule/<date>` sur **Schedule** pour vérifier que chaque film demandé est programmé ce jour-là.
- `POST` et `DELETE /schedule/<date>/<user_id>` sur **Schedule** appellent `GET /users/is-admin/<user_id>` sur **User** pour vérifier les droits.
- À l'ajout de films dans le planning, **Schedule** appelle `GET /movies/<id>` sur **Movie** et ignore les identifiants inconnus.

Les services s'appellent sur `127.0.0.1`, ils doivent donc tourner sur la même machine.

## Principaux endpoints

### Movie (`:3200`)

| Méthode | Route                       | Description                         |
|---------|-----------------------------|-------------------------------------|
| GET     | `/movies/list/all`          | Liste tous les films                |
| GET     | `/movies/<movieid>`         | Détail d'un film                    |
| GET     | `/movies/info?title=...`    | Recherche par titre                 |
| POST    | `/movies/<movieid>`         | Ajoute un film                      |
| PUT     | `/movies/rating/<movieid>`  | Met à jour la note (`{"rating": x}`) |
| DELETE  | `/movies/<movieid>`         | Supprime un film                    |

### Schedule (`:3202`)

| Méthode | Route                        | Description                                        |
|---------|------------------------------|----------------------------------------------------|
| GET     | `/schedule/list/all`         | Planning complet                                   |
| GET     | `/schedule/<date>`           | Films programmés à une date (`AAAAMMJJ`)           |
| POST    | `/schedule/<date>/<user_id>` | Ajoute des films à une date (admin uniquement)     |
| DELETE  | `/schedule/<date>/<user_id>` | Retire des films d'une date (admin uniquement)     |

Corps attendu pour POST/DELETE : `{"date": "20151201", "movies": ["<movie_id>", ...]}`.

### Booking (`:3201`)

| Méthode | Route                                       | Description                  |
|---------|---------------------------------------------|------------------------------|
| GET     | `/bookings/read-all-bookings`               | Liste toutes les réservations |
| POST    | `/bookings/create-booking/<userid>`         | Crée une réservation          |
| GET     | `/bookings/get-detailed-booking/<id>`       | Détail d'une réservation      |
| DELETE  | `/bookings/delete-booking/<id>`             | Supprime une réservation      |

Corps attendu pour la création : `{"date": "20151201", "movies": ["<movie_id>", ...]}`.

### User (`:3203`)

| Méthode | Route                          | Description                          |
|---------|--------------------------------|--------------------------------------|
| GET     | `/users/read-all-users`        | Liste les utilisateurs               |
| GET     | `/users/verify-user/<user_id>` | Détail d'un utilisateur              |
| GET     | `/users/is-admin/<user_id>`    | 200 si l'utilisateur est admin       |
| POST    | `/users/create-user/<user_id>` | Crée un utilisateur                  |
| PUT     | `/users/update-user/<user_id>` | Modifie un utilisateur               |
| DELETE  | `/users/delete-user/<user_id>` | Supprime un utilisateur (rôle `user`) |

Le détail complet (schémas, codes de retour) se trouve dans les fichiers `openapi.yaml`.

## Lancer le projet

### Prérequis

- Python 3.10 ou plus récent

### Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
pip install requests             # utilisé pour les appels entre services
```

### Démarrage

Chaque service lit son fichier JSON avec un chemin relatif (`./databases/...`) : il faut le lancer **depuis son propre dossier**. Ouvrez un terminal par service :

```bash
cd movie    && python movie.py       # http://127.0.0.1:3200
cd schedule && python schedule.py    # http://127.0.0.1:3202
cd booking  && python booking.py     # http://127.0.0.1:3201
cd user     && python user.py        # http://127.0.0.1:3203
```

`py-mon` est installé avec les dépendances et permet de relancer un service automatiquement à chaque modification : `cd movie && pymon movie.py`.

### Exemples de requêtes

```bash
# Lister les films
curl http://127.0.0.1:3200/movies/list/all

# Programmer un film le 1er décembre 2015 (chris_rivers est admin)
curl -X POST http://127.0.0.1:3202/schedule/20151201/chris_rivers \
  -H "Content-Type: application/json" \
  -d '{"date": "20151201", "movies": ["720d006c-3a57-4b6a-b18f-9b713b073f3c"]}'

# Réserver ce film pour garret_heaton
curl -X POST http://127.0.0.1:3201/bookings/create-booking/garret_heaton \
  -H "Content-Type: application/json" \
  -d '{"date": "20151201", "movies": ["720d006c-3a57-4b6a-b18f-9b713b073f3c"]}'
```

### Docker

La conteneurisation est prévue pour une séance ultérieure : les `Dockerfile` et le `docker-compose.yml` (qui ne déclare pour l'instant que le service Movie) sont incomplets. Une fois terminés, le lancement se fera avec :

```bash
docker compose up --build
```

## Structure du dépôt

```
.
├── booking/
│   ├── booking.py
│   ├── openapi.yaml
│   ├── Dockerfile
│   └── databases/bookings.json
├── movie/
│   ├── movie.py
│   ├── openapi.yaml
│   ├── Dockerfile
│   ├── templates/index.html
│   └── databases/movies.json
├── schedule/
│   ├── schedule.py
│   ├── openapi.yaml
│   ├── Dockerfile
│   └── databases/times.json
├── user/
│   ├── user.py
│   ├── openapi.yaml
│   ├── Dockerfile
│   └── databases/users.json
├── docker-compose.yml
├── requirements.txt
└── LICENSE
```

## Licence

Voir le fichier [LICENSE](LICENSE).
