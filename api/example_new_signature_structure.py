"""
Esempio pratico del nuovo sistema di firma v2

Dimostra come la firma viene aggiunta direttamente all'oggetto originale
"""

# Esempio 1: Firma di una fattura
print("=" * 60)
print("ESEMPIO 1: Firma di una fattura")
print("=" * 60)

# Documento originale (PRIMA della firma)
invoice_before = {
    "invoice_id": "INV-2026-001",
    "amount": 1500.00,
    "currency": "EUR",
    "client": "Acme Corp",
}

print("\n📄 Documento PRIMA della firma:")
import json

print(json.dumps(invoice_before, indent=2))

# Dopo la firma (viene aggiunta solo la proprietà 'signature')
invoice_after = {
    "invoice_id": "INV-2026-001",
    "amount": 1500.00,
    "currency": "EUR",
    "client": "Acme Corp",
    "signature": {  # ⬅️ Aggiunta come proprietà
        "metadata": {
            "version": "2.0",
            "algorithm": "RSA-PSS-SHA256",
            "uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
            "date": "2026-02-04",
            "content_hash": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
            "content_type": "json",
        },
        "signature": "MEUCIQDxG8vqz2dVBXm...",
    },
}

print("\n✅ Documento DOPO la firma:")
print(json.dumps(invoice_after, indent=2))

print("\n💡 Nota: La firma è stata aggiunta come proprietà dell'oggetto originale!")


# Esempio 2: Documento con 'signature' esistente
print("\n\n" + "=" * 60)
print("ESEMPIO 2: Documento con firma pre-esistente")
print("=" * 60)

# Se l'oggetto ha già una proprietà 'signature', viene rimossa prima di firmare
document_with_old_signature = {
    "invoice_id": "INV-2026-002",
    "amount": 2000.00,
    "signature": {  # ⬅️ Firma vecchia (sarà rimossa)
        "metadata": {"date": "2025-01-01"},
        "signature": "old_signature",
    },
}

print("\n⚠️  Documento CON firma vecchia:")
print(json.dumps(document_with_old_signature, indent=2))

# Dopo ri-firma (la vecchia signature viene sostituita)
document_resigned = {
    "invoice_id": "INV-2026-002",
    "amount": 2000.00,
    "signature": {  # ⬅️ Nuova firma (sostituisce la vecchia)
        "metadata": {
            "version": "2.0",
            "algorithm": "RSA-PSS-SHA256",
            "uid": "f47ac10b-58cc-5372-a567-0e02b2c3d479",
            "date": "2026-02-04",
            "content_hash": "new_hash",
            "content_type": "json",
        },
        "signature": "NEW_SIGNATURE",
    },
}

print("\n✅ Documento RI-FIRMATO (vecchia firma rimossa):")
print(json.dumps(document_resigned, indent=2))

print("\n💡 Nota: La vecchia firma è stata automaticamente rimossa prima di firmare!")


# Esempio 3: Verifica
print("\n\n" + "=" * 60)
print("ESEMPIO 3: Processo di verifica")
print("=" * 60)

signed_doc = {
    "invoice_id": "INV-2026-001",
    "amount": 1500.00,
    "currency": "EUR",
    "signature": {"metadata": "...", "signature": "..."},
}

print("\n1️⃣  Sistema riceve documento firmato:")
print(json.dumps(signed_doc, indent=2))

print("\n2️⃣  Estrae la firma:")
signature = signed_doc["signature"]
print(f"   signature = {signature}")

print("\n3️⃣  Estrae il contenuto originale (tutto tranne 'signature'):")
original_content = {k: v for k, v in signed_doc.items() if k != "signature"}
print(f"   original_content = {json.dumps(original_content, indent=2)}")

print("\n4️⃣  Calcola hash del contenuto originale")
print("   calculated_hash = sha256(original_content)")

print("\n5️⃣  Confronta con hash nella firma")
print("   if calculated_hash == signature['metadata']['content_hash']:")
print("       ✅ Contenuto non modificato!")

print("\n6️⃣  Verifica firma digitale con chiave pubblica")
print("   public_key.verify(signature_bytes, metadata_bytes)")
print("       ✅ Firma autentica!")


# Esempio 4: Confronto con sistema precedente
print("\n\n" + "=" * 60)
print("CONFRONTO: Sistema PRECEDENTE vs NUOVO")
print("=" * 60)

print("\n❌ Sistema PRECEDENTE (v1):")
print("""
{
  "content": {
    "invoice_id": "INV-2026-001",
    "amount": 1500.00
  },
  "signature": {...}
}

⚠️  Struttura separata: content e signature sono divisi
⚠️  Meno intuitivo: devi accedere a doc.content.invoice_id
""")

print("\n✅ Sistema NUOVO (v2):")
print("""
{
  "invoice_id": "INV-2026-001",
  "amount": 1500.00,
  "signature": {...}
}

✅ Struttura piatta: signature è una proprietà come le altre
✅ Più intuitivo: accedi a doc.invoice_id direttamente
✅ Più naturale: come aggiungere metadati a un oggetto
""")


# Esempio 5: API Request/Response
print("\n\n" + "=" * 60)
print("ESEMPIO API: Request e Response")
print("=" * 60)

print("\n📤 REQUEST (firma documento):")
print("""
POST /api/v2/sign/?on=2026-02-04
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": {
    "invoice_id": "INV-2026-001",
    "amount": 1500.00,
    "currency": "EUR"
  }
}
""")

print("\n📥 RESPONSE (documento firmato):")
print("""
{
  "invoice_id": "INV-2026-001",
  "amount": 1500.00,
  "currency": "EUR",
  "signature": {
    "metadata": {
      "version": "2.0",
      "algorithm": "RSA-PSS-SHA256",
      "uid": "user-uuid",
      "date": "2026-02-04",
      "content_hash": "abc123...",
      "content_type": "json"
    },
    "signature": "MEUCIQDxG..."
  }
}

💡 La signature è stata aggiunta direttamente all'oggetto!
""")

print("\n✅ Vantaggi di questo approccio:")
print("   1. Più naturale e intuitivo")
print("   2. Facile serializzare/deserializzare")
print("   3. Compatibile con sistemi esistenti")
print("   4. Riduce nesting inutile")
print("   5. Signature può essere facilmente rimossa se necessario")

print("\n" + "=" * 60)
