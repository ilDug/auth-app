"""
Test di esempio per il sistema di firma digitale

Questo file mostra come utilizzare il sistema di firma in Python.
"""

import requests
import json

# Configurazione
BASE_URL = "http://localhost:8000"  # Modifica con il tuo URL
ACCESS_TOKEN = "your_access_token_here"  # Token di autenticazione


def sign_document(data: dict | str, date: str) -> dict:
    """
    Firma un documento o dati

    Args:
        data: I dati da firmare (dict o str)
        date: La data della firma (yyyy-mm-dd)

    Returns:
        dict: L'oggetto firmato contenente i dati e la firma
    """
    url = f"{BASE_URL}/api/v1/sign/object"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    params = {"on": date}

    response = requests.post(url, json={"data": data}, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Errore nella firma: {response.status_code} - {response.text}")


def verify_signature(signed_data: dict) -> dict:
    """
    Verifica un documento firmato

    Args:
        signed_data: L'oggetto contenente i dati e la firma

    Returns:
        dict: Il report di verifica
    """
    url = f"{BASE_URL}/api/v1/sign/verify_signature"

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=signed_data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Errore nella verifica: {response.status_code} - {response.text}"
        )


# Esempio 1: Firma di un documento dict
def example_sign_dict():
    print("\n=== Esempio 1: Firma di un documento dict ===\n")

    # Dati da firmare
    invoice = {
        "invoice_id": "INV-2026-001",
        "amount": 1500.00,
        "currency": "EUR",
        "client": "Acme Corp",
        "items": [
            {"description": "Consulenza IT", "quantity": 10, "price": 100.00},
            {"description": "Sviluppo Software", "quantity": 5, "price": 100.00},
        ],
    }

    # Firma il documento
    signed_invoice = sign_document(invoice, "2026-02-04")

    print("Documento firmato:")
    print(json.dumps(signed_invoice, indent=2))

    return signed_invoice


# Esempio 2: Firma di una stringa
def example_sign_string():
    print("\n=== Esempio 2: Firma di una stringa ===\n")

    # Messaggio da firmare
    message = "Approvo il progetto X con budget di 50.000 EUR"

    # Firma il messaggio
    signed_message = sign_document(message, "2026-02-04")

    print("Messaggio firmato:")
    print(json.dumps(signed_message, indent=2))

    return signed_message


# Esempio 3: Verifica di un documento firmato (autentico)
def example_verify_authentic(signed_data: dict):
    print("\n=== Esempio 3: Verifica documento autentico ===\n")

    # Verifica la firma
    verification_report = verify_signature(signed_data)

    print("Report di verifica:")
    print(json.dumps(verification_report, indent=2))

    if verification_report["verified"]:
        print(f"\n✓ Documento VALIDO")
        print(f"  Firmato da: {verification_report['user']}")
        print(f"  In data: {verification_report['date']}")
    else:
        print(f"\n✗ Documento NON VALIDO")
        print(f"  Errori: {', '.join(verification_report['errors'])}")


# Esempio 4: Verifica di un documento modificato (non autentico)
def example_verify_tampered(signed_data: dict):
    print("\n=== Esempio 4: Verifica documento modificato ===\n")

    # Modifica i dati (simula una manomissione)
    tampered_data = signed_data.copy()
    if "amount" in tampered_data:
        tampered_data["amount"] = 999999.99  # Modifica l'importo
        print("⚠ Documento manomesso: importo modificato da 1500.00 a 999999.99\n")

    # Verifica la firma
    verification_report = verify_signature(tampered_data)

    print("Report di verifica:")
    print(json.dumps(verification_report, indent=2))

    if verification_report["verified"]:
        print(f"\n✓ Documento VALIDO")
    else:
        print(f"\n✗ Documento NON VALIDO")
        print(f"  Errori rilevati:")
        for error in verification_report["errors"]:
            print(f"    - {error}")


# Esempio 5: Verifica di un documento con firma non autentica
def example_verify_fake_signature(signed_data: dict):
    print("\n=== Esempio 5: Verifica documento con firma falsificata ===\n")

    # Modifica la firma (simula una falsificazione)
    fake_data = signed_data.copy()
    fake_data["signature"]["signature"] = "0123456789abcdef" * 32  # Firma falsa
    print("⚠ Firma falsificata\n")

    # Verifica la firma
    verification_report = verify_signature(fake_data)

    print("Report di verifica:")
    print(json.dumps(verification_report, indent=2))

    if verification_report["verified"]:
        print(f"\n✓ Documento VALIDO")
    else:
        print(f"\n✗ Documento NON VALIDO")
        print(f"  Errori rilevati:")
        for error in verification_report["errors"]:
            print(f"    - {error}")


def main():
    """Esegue tutti gli esempi"""
    print("=" * 60)
    print("SISTEMA DI FIRMA DIGITALE - ESEMPI D'USO")
    print("=" * 60)

    try:
        # Esempio 1: Firma un documento
        signed_invoice = example_sign_dict()

        # Esempio 2: Firma una stringa
        signed_message = example_sign_string()

        # Esempio 3: Verifica documento autentico
        example_verify_authentic(signed_invoice)

        # Esempio 4: Verifica documento modificato
        example_verify_tampered(signed_invoice)

        # Esempio 5: Verifica firma falsificata
        example_verify_fake_signature(signed_invoice)

        print("\n" + "=" * 60)
        print("TEST COMPLETATI")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Errore durante l'esecuzione: {str(e)}")
        print("\nVerifica che:")
        print("1. Il server sia avviato")
        print("2. L'URL sia corretto")
        print("3. Il token di accesso sia valido")


if __name__ == "__main__":
    # Nota: Questo script richiede requests
    # Installalo con: pip install requests

    print("\n⚠ IMPORTANTE: Prima di eseguire questo script:")
    print("1. Avvia il server FastAPI")
    print("2. Ottieni un token di accesso valido")
    print("3. Aggiorna la variabile ACCESS_TOKEN in questo file")
    print("4. Verifica che l'URL BASE_URL sia corretto\n")

    input("Premi INVIO per continuare o CTRL+C per uscire...")

    main()
