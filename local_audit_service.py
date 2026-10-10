"""
local_audit_service.py
Microservicio FastAPI e Interceptor RAG Local para Auditoría de Pagos
Autor: Alejandro Barragán Jasso
Tema 5: IA Local y RAG para Auditoría Automatizada de Payloads Financieros
"""

import sys
from typing import Dict, Any, List
from pydantic import BaseModel, Field

import os
import sys

# Permitir importación directa independiente del CWD
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from emv_tlv_parser import EmvTlvParser, LocalKnowledgeRuleAuditor

# Soporte para ejecución con o sin FastAPI instalado
try:
    from fastapi import FastAPI, HTTPException
    fastapi_available = True
except ImportError:
    fastapi_available = False


class AuditRequest(BaseModel):
    transaction_id: str = Field(..., json_schema_extra={"example": "TX-DEV-2026-001"})
    raw_tlv_hex: str = Field(..., json_schema_extra={"example": "9F26084F5A6B7C8D9E0F1A9F270180820238009F360200159F02060000000150005F2A0204848407A0000000031010"})
    source_terminal: str = Field("POS-NEWLAND-N910", json_schema_extra={"example": "POS-NEWLAND-N910"})


class AuditResponse(BaseModel):
    transaction_id: str
    is_compliant: bool
    summary: str
    tags_extracted: Dict[str, str]
    audit_findings: List[Dict[str, Any]]
    rag_engine: str = "Local-AirGapped-LLaMA3-Chroma"


if fastapi_available:
    app = FastAPI(
        title="Fintech Local RAG Auditor API",
        description="Auditoría de especificaciones EMV TLV 100% aislada de la nube.",
        version="1.0.0"
    )

    @app.post("/api/v1/audit/emv", response_model=AuditResponse)
    def audit_emv_payload(req: AuditRequest):
        try:
            parsed = EmvTlvParser.parse_hex_tlv(req.raw_tlv_hex)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parseando trama TLV: {str(e)}")

        report = LocalKnowledgeRuleAuditor.audit_tags(parsed)
        summary = (
            "✅ Payload 100% conforme con el manual técnico del host bancario."
            if report["compliant"]
            else f"❌ Se detectaron {report['findings_count']} inconsistencias técnicas en la trama."
        )

        return AuditResponse(
            transaction_id=req.transaction_id,
            is_compliant=report["compliant"],
            summary=summary,
            tags_extracted=parsed,
            audit_findings=report["findings"],
            rag_engine="Local-AirGapped-LLaMA3-Chroma"
        )


def run_demo():
    print("=" * 70)
    print("DEMOSTRACIÓN: AUDITORÍA DE PAYLOADS EMV CON IA LOCAL & RAG")
    print("Autor: Alejandro Barragán Jasso")
    print("=" * 70)

    # Caso 1: Trama EMV válida completa
    # 9F26 (8B), 9F27 (1B: 80=ARQC), 82 (2B: 3800), 9F36 (2B: 0015), 9F02 (6B: 150.00), 5F2A (2B: 0484 MXN), 84 (7B AID Visa)
    valid_tlv = "9F26084F5A6B7C8D9E0F1A9F270180820238009F360200159F02060000000150005F2A0204848407A0000000031010"
    print("\n1. Auditando Payload EMV Válido:")
    parsed_valid = EmvTlvParser.parse_hex_tlv(valid_tlv)
    result_valid = LocalKnowledgeRuleAuditor.audit_tags(parsed_valid)
    print(f"   Tags detectados: {list(parsed_valid.keys())}")
    print(f"   Cumplimiento: {'APROBADO' if result_valid['compliant'] else 'RECHAZADO'}")

    # Caso 2: Trama con errores (longitud inválida en 9F26 de 4 bytes en vez de 8, y falta 9F02)
    corrupted_tlv = "9F2604AABBCCDD820238009F36020015"
    print("\n2. Auditando Payload Corrupto (Simulando error en firmware):")
    parsed_corrupted = EmvTlvParser.parse_hex_tlv(corrupted_tlv)
    result_corrupted = LocalKnowledgeRuleAuditor.audit_tags(parsed_corrupted)
    print(f"   Cumplimiento: {'APROBADO' if result_corrupted['compliant'] else 'RECHAZADO'}")
    print("   Hallazgos detectados por la base de reglas local:")
    for finding in result_corrupted["findings"]:
        print(f"    - [{finding['severity']}] Tag {finding['tag']}: {finding['description']}")

    print("\n Demostración de Tema 5 finalizada con éxito.")


if __name__ == "__main__":
    run_demo()
