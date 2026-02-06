# auth-app

[![Lint Python](https://github.com/ilDug/auth-app/actions/workflows/check-python.yaml/badge.svg)](https://github.com/ilDug/auth-app/actions/workflows/check-python.yaml)

**Backend Service** running on Docker Container, for managing users, accesses, accounts, permissions, privileges.

## Prerequisites

This backend service works as an API throught HTTP protocol.

It needs:

-   a certificate/key pair (RSA) to sign the JWT token
-   a mongodb database to store users and permissions
-   a proxy to expose the service to the network (like [traefik](https://traefik.io))

In the [lib](./lib/scripts) folder there are some scripts to help to create the inital configuration in order to pass them to `docker-compose.yaml`file. All configuration files are saved automatically to `lib/secrets/` folder. Feel fre to use another more secure system to pass secrets files to the container.

1. `lib/scripts/0.generate-credentials.zsh` creates credentials for MONGODB and stores it to `lib/secrets/` folder.

2. `lib/scripts/1.create-certificates.zsh` creates a cert/key pair and saves it in `lib/secrets/` folder.

3. `lib/scripts/2.create-email-config.zsh`creates an empty configuration that must be filled with a valid email account.

## Docker Container

To pull and run the Docker container, you can use the following commands:

```bash
docker pull ghcr.io/ildug/auth-app:latest
```

Make sure you have Docker installed and running on your machine before executing these commands.

It needs also a **mongodb** database where to store the data of users, account, permission and logins.

Make sure to set SECRETS and ENVIROMENTAL VARIABLES for the container in the [`docker-compose.yaml`](./docker-compose.prod.yaml):

## API ENDPOINTS

Base path: `/api/auth/v2`

### Account

| METHOD | ENDPOINT                           | PAYLOAD             |
| ------ | ---------------------------------- | ------------------- |
| POST   | `/account/login`                   | `{email, password}` |
| POST   | `/account/register?notify=true`    | `{email, password}` |
| GET    | `/account/exists/{email_md5_hash}` |                     |

### Digtal signature

| METHOD | ENDPOINT               | PAYLOAD                |
| ------ | ---------------------- | ---------------------- |
| POST   | `/sign/?on=2024-10-31` | `{...data}`            |
| POST   | `/sign/verify`         | `{...data, signature}` |

### Remote authentication/authorization

| METHOD | ENDPOINT                             | PAYLOAD                                                                                                 |
| ------ | ------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| GET    | `/auth/authenticate?claims=true`     | <small>Uses the JWT in header. If claims are true returns the jwt payload, else return boolean.</small> |
| GET    | `/auth/authorize?permission=<admin>` | <small>Set the permission or role you want to authorize.</small>                                        |

| METHOD | ENDPOINT           | PAYLOAD               |
| ------ | ------------------ | --------------------- |
| GET    | `/users/`          |                       |
| PUT    | `/users/`          | _user object as json_ |
| GET    | `/users/{user_id}` |                       |
| DELETE | `/users/{user_id}` |                       |

### Health

| METHOD | ENDPOINT  | PAYLOAD |
| ------ | --------- | ------- |
| GET    | `/health` |         |

## REGISTRATION BEHAVIOUR

Select the behaviour of registration setting the environmental variable `REGISTRATION_BEHAVIOUR`

- `ALLOW_ANYBODY`
- `ONLY_ADMIN`
