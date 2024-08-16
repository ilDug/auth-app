from fastapi import Header, HTTPException, Cookie

from .. import Auth


# async def remote_authentication(authorization: str = Header(...)):
#     bearer_token = authorization

#     try:
#         response = requests.get(
#             AUTHENTICATION_BASE_URL,
#             headers={"Authorization": bearer_token}
#         )

#         if not response.status_code:
#             raise HTTPException(
#                 401, "Unauthorized - DAG Auth Server No Response")

#         print(response.headers)
#         print(response.text)
#         print(response.status_code)
#         print(response.ok)
#         print(response.raise_for_status())

#     except ConnectionError as e:
#         print("Errore di connessione al server di authenticazione")
#         raise HTTPException(
#             401, "Unauthorized - Errore di connessione al server di authenticazione")

#     except Exception as e:
#         print("Errore AUTH MIDDLEWARE JWT: " + str(e.args))
#         err_details = response.headers['x-error'] if "x-error" in response.headers else str(
#             e.args)

#         raise HTTPException(401, err_details)
