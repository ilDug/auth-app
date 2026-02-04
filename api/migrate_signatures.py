"""
Script di migrazione da sistema firma v1 a v2

Questo script aiuta a migrare documenti firmati con v1 al nuovo formato v2.
ATTENZIONE: La migrazione richiede ri-firma dei documenti.
"""

from typing import Any
from datetime import datetime, timezone
from models import DataWithSignature, SignModel
from models.sign import SignedDocument
from controllers.account import Account
from controllers.sign.sign import sign_content


async def convert_v1_signature_to_v2(
    v1_document: DataWithSignature,
    re_sign: bool = True
) -> SignedDocument | dict:
    """
    Converte un documento firmato con v1 al formato v2.

    IMPORTANTE: Non è possibile convertire direttamente una firma v1 in v2
    perché usano algoritmi e strutture diverse. Questa funzione ha due modalità:

    1. re_sign=True (default, raccomandato):
       - Estrae i dati originali
       - Recupera l'utente originale
       - Ri-firma i dati con v2
       - Mantiene l'utente originale
       - ⚠️ Il timestamp sarà nuovo

    2. re_sign=False (solo per riferimento):
       - Converte la struttura senza ri-firmare
       - ⚠️ La firma non sarà valida in v2
       - Utile solo per visualizzazione/confronto

    Args:
        v1_document: Documento firmato con sistema v1
        re_sign: Se True, ri-firma il documento con v2. Se False, converte solo la struttura.

    Returns:
        SignedDocument: Documento nel formato v2

    Raises:
        HTTPException: Se l'utente non esiste o la conversione fallisce
    """
    # Estrai i dati originali (rimuovi la firma)
    original_data = v1_document.model_dump(exclude={"signature"})
    v1_signature: SignModel = v1_document.signature

    if re_sign:
        # MODALITÀ 1: Ri-firma con v2 (raccomandato)
        print(f"♻️  Ri-firma documento per utente {v1_signature.uid}")

        # Recupera l'utente originale
        user = await Account.get_user(uid=v1_signature.uid)

        # Ri-firma con v2
        v2_document = sign_content(content=original_data, user=user)

        print(f"✅ Documento ri-firmato con v2")
        print(f"   - Utente: {user.email}")
        print(f"   - Firma originale v1: {v1_signature.date}")
        print(f"   - Nuova firma v2: {v2_document.signature.metadata.timestamp}")

        return v2_document

    else:
        # MODALITÀ 2: Solo conversione struttura (non valido)
        print("⚠️  Conversione solo struttura - firma NON valida")

        # Converte la struttura mantenendo le informazioni originali
        from models.sign import SignatureMetadata, DigitalSignature

        # Crea metadata v2 dai dati v1
        metadata = SignatureMetadata(
            version="2.0",
            algorithm="RSA-PSS-SHA256",
            uid=v1_signature.uid,
            # Converti data in timestamp (assumendo mezzanotte UTC)
            timestamp=f"{v1_signature.date}T00:00:00Z",
            content_hash=v1_signature.fingerprint,
            content_type="json" if isinstance(original_data, dict) else "text",
        )

        # Nota: La firma v1 in hex non è compatibile con v2 in base64
        # Convertiamo comunque per mantenere riferimento
        import base64
        try:
            signature_bytes = bytes.fromhex(v1_signature.signature)
            signature_b64 = base64.b64encode(signature_bytes).decode("ascii")
        except ValueError:
            # Se la conversione fallisce, usa un placeholder
            signature_b64 = "INVALID_V1_SIGNATURE_NOT_CONVERTED"

        v2_signature = DigitalSignature(
            metadata=metadata,
            signature=signature_b64
        )

        return {
            "content": original_data,
            "signature": v2_signature.model_dump(),
            "_migration_note": "This document was converted from v1 structure but signature is NOT valid. Please re-sign."
        }


async def migrate_documents_batch(
    v1_documents: list[DataWithSignature],
    progress_callback=None
) -> dict[str, Any]:
    """
    Migra un batch di documenti da v1 a v2.

    Args:
        v1_documents: Lista di documenti firmati con v1
        progress_callback: Funzione opzionale chiamata per ogni documento (index, total, status)

    Returns:
        dict: Statistiche della migrazione
    """
    results = {
        "total": len(v1_documents),
        "successful": 0,
        "failed": 0,
        "errors": [],
        "migrated_documents": []
    }

    for i, v1_doc in enumerate(v1_documents):
        try:
            # Converti e ri-firma
            v2_doc = await convert_v1_signature_to_v2(v1_doc, re_sign=True)
            results["migrated_documents"].append(v2_doc)
            results["successful"] += 1

            if progress_callback:
                progress_callback(i + 1, results["total"], "success")

        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "document_index": i,
                "uid": v1_doc.signature.uid if hasattr(v1_doc, 'signature') else None,
                "error": str(e)
            })

            if progress_callback:
                progress_callback(i + 1, results["total"], f"error: {e}")

    return results


async def migrate_mongodb_collection(
    collection_name: str = "signed_documents",
    batch_size: int = 100,
    dry_run: bool = True
):
    """
    Migra una collezione MongoDB da v1 a v2.

    Args:
        collection_name: Nome della collezione da migrare
        batch_size: Numero di documenti per batch
        dry_run: Se True, simula la migrazione senza salvare

    Returns:
        dict: Statistiche della migrazione
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    from core.config import MONGO_CS, DB

    print(f"\n{'='*60}")
    print(f"MIGRAZIONE COLLEZIONE: {collection_name}")
    print(f"Modalità: {'DRY RUN (simulazione)' if dry_run else 'PRODUZIONE'}")
    print(f"{'='*60}\n")

    async with AsyncIOMotorClient(MONGO_CS) as client:
        db = client[DB]
        collection = db[collection_name]

        # Conta documenti totali
        total_docs = await collection.count_documents({})
        print(f"📊 Documenti totali: {total_docs}")

        if total_docs == 0:
            print("✅ Nessun documento da migrare")
            return {"total": 0, "successful": 0, "failed": 0}

        migrated = 0
        failed = 0
        errors = []

        # Processa in batch
        cursor = collection.find({}).batch_size(batch_size)

        async for doc in cursor:
            try:
                # Converti documento MongoDB in DataWithSignature
                v1_doc = DataWithSignature(**doc)

                # Migra a v2
                v2_doc = await convert_v1_signature_to_v2(v1_doc, re_sign=True)

                if not dry_run:
                    # Salva il documento migrato
                    # Opzione 1: Sostituisci documento esistente
                    await collection.replace_one(
                        {"_id": doc["_id"]},
                        v2_doc.model_dump()
                    )
                    # Opzione 2: Crea nuova collezione v2
                    # await db[f"{collection_name}_v2"].insert_one(v2_doc.model_dump())

                migrated += 1
                print(f"✅ Migrato {migrated}/{total_docs}", end="\r")

            except Exception as e:
                failed += 1
                errors.append({
                    "doc_id": str(doc.get("_id")),
                    "error": str(e)
                })
                print(f"❌ Errore documento {doc.get('_id')}: {e}")

        print(f"\n\n{'='*60}")
        print(f"MIGRAZIONE COMPLETATA")
        print(f"{'='*60}")
        print(f"✅ Migrati: {migrated}")
        print(f"❌ Falliti: {failed}")

        if errors:
            print(f"\n⚠️  Errori:")
            for error in errors[:10]:  # Mostra primi 10
                print(f"   - {error['doc_id']}: {error['error']}")

        return {
            "total": total_docs,
            "successful": migrated,
            "failed": failed,
            "errors": errors
        }


def generate_migration_report(stats: dict[str, Any]) -> str:
    """
    Genera un report testuale della migrazione.

    Args:
        stats: Statistiche della migrazione

    Returns:
        str: Report formattato
    """
    success_rate = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0

    report = f"""
╔{'='*58}╗
║{' '*18}MIGRATION REPORT{' '*22}║
╚{'='*58}╝

📊 Statistiche:
   - Documenti totali:     {stats['total']}
   - Migrati con successo: {stats['successful']}
   - Falliti:              {stats['failed']}
   - Tasso di successo:    {success_rate:.1f}%

"""

    if stats["errors"]:
        report += "⚠️  Errori:\n"
        for error in stats["errors"][:5]:
            report += f"   - Doc #{error.get('document_index', '?')}: {error['error']}\n"

        if len(stats["errors"]) > 5:
            report += f"   ... e altri {len(stats['errors']) - 5} errori\n"

    report += f"\n{'='*60}\n"

    return report


# Script eseguibile
if __name__ == "__main__":
    import asyncio

    async def main():
        print("\n" + "="*60)
        print("SCRIPT DI MIGRAZIONE v1 → v2")
        print("="*60)
        print("\n⚠️  IMPORTANTE:")
        print("   - La migrazione richiede ri-firma dei documenti")
        print("   - I timestamp saranno aggiornati")
        print("   - Backup consigliato prima della migrazione")
        print("\nOpzioni:")
        print("   1. Migrazione collezione MongoDB (DRY RUN)")
        print("   2. Migrazione collezione MongoDB (PRODUZIONE)")
        print("   3. Test singolo documento")
        print("   0. Esci")

        choice = input("\nScelta: ")

        if choice == "1":
            await migrate_mongodb_collection(dry_run=True)
        elif choice == "2":
            confirm = input("\n⚠️  Confermi migrazione PRODUZIONE? (yes/no): ")
            if confirm.lower() == "yes":
                await migrate_mongodb_collection(dry_run=False)
            else:
                print("❌ Migrazione annullata")
        elif choice == "3":
            print("\n🧪 Test singolo documento...")
            # Qui puoi testare con un documento di esempio
            print("✅ Implementa un test con un documento di esempio")
        else:
            print("👋 Uscita")

    asyncio.run(main())
