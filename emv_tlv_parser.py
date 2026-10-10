"""
emv_tlv_parser.py
Parser y Validador de Estructuras EMV TLV (Tag-Length-Value)
Autor: Alejandro Barragán Jasso
Tema 5: Auditoría de Payloads Financieros con IA Local y RAG
"""

from typing import Dict, Any, List, Tuple

class EmvTlvParser:
    """Decodifica tramas EMV BER-TLV en diccionarios estructurados."""

    @staticmethod
    def parse_hex_tlv(hex_string: str) -> Dict[str, str]:
        """
        Parsea un string hexadecimal continuo en un diccionario {TAG: VALUE_HEX}.
        Maneja tags de 1 y 2 bytes según la especificación EMV Book 3.
        """
        clean_hex = hex_string.strip().replace(" ", "").upper()
        idx = 0
        length = len(clean_hex)
        tags_dict = {}

        while idx < length:
            # 1. Leer Tag (1 o 2 bytes)
            first_byte_str = clean_hex[idx:idx+2]
            idx += 2
            first_byte = int(first_byte_str, 16)

            # Si los 5 bits menos significativos son '11111' (0x1F), el tag tiene 2 bytes
            if (first_byte & 0x1F) == 0x1F:
                second_byte_str = clean_hex[idx:idx+2]
                idx += 2
                tag = (first_byte_str + second_byte_str).upper()
            else:
                tag = first_byte_str.upper()

            if idx >= length:
                break

            # 2. Leer Longitud (Length)
            len_byte_str = clean_hex[idx:idx+2]
            idx += 2
            len_byte = int(len_byte_str, 16)

            # Si bit 8 está activo, longitud multiocteto
            if (len_byte & 0x80) == 0x80:
                num_length_bytes = len_byte & 0x7F
                raw_len_str = clean_hex[idx:idx + (num_length_bytes * 2)]
                idx += num_length_bytes * 2
                val_len_bytes = int(raw_len_str, 16) if raw_len_str else 0
            else:
                val_len_bytes = len_byte

            # 3. Extraer Valor (Value)
            val_chars = val_len_bytes * 2
            val_hex = clean_hex[idx:idx + val_chars]
            idx += val_chars

            tags_dict[tag] = val_hex

        return tags_dict


class LocalKnowledgeRuleAuditor:
    """Base de conocimiento local con especificaciones EMV oficiales (emula Vector DB / RAG)."""

    EMV_SPEC_CATALOG = {
        "9F26": {
            "name": "Application Cryptogram (ARQC/TC/AAC)",
            "expected_len_bytes": 8,
            "format": "Binary / Hex (16 chars)",
            "mandatory": True
        },
        "9F27": {
            "name": "Cryptogram Information Data (CID)",
            "expected_len_bytes": 1,
            "format": "Binary / Hex (2 chars)",
            "mandatory": True
        },
        "82": {
            "name": "Application Interchange Profile (AIP)",
            "expected_len_bytes": 2,
            "format": "Binary / Hex (4 chars)",
            "mandatory": True
        },
        "9F36": {
            "name": "Application Transaction Counter (ATC)",
            "expected_len_bytes": 2,
            "format": "Binary / Hex (4 chars)",
            "mandatory": True
        },
        "9F02": {
            "name": "Amount, Authorised (Numeric)",
            "expected_len_bytes": 6,
            "format": "Numeric (12 digits)",
            "mandatory": True
        },
        "5F2A": {
            "name": "Transaction Currency Code",
            "expected_len_bytes": 2,
            "format": "Numeric (4 chars)",
            "mandatory": True
        },
        "84": {
            "name": "Dedicated File (DF) Name / AID",
            "min_len_bytes": 5,
            "max_len_bytes": 16,
            "format": "Binary / Hex",
            "mandatory": True
        }
    }

    @classmethod
    def audit_tags(cls, parsed_tags: Dict[str, str]) -> Dict[str, Any]:
        """Evalúa el payload contra las reglas del manual técnico de pagos."""
        findings: List[Dict[str, Any]] = []
        is_compliant = True

        # Validar campos obligatorios
        for tag, spec in cls.EMV_SPEC_CATALOG.items():
            if spec.get("mandatory") and tag not in parsed_tags:
                findings.append({
                    "severity": "CRITICAL",
                    "tag": tag,
                    "description": f"Tag obligatorio faltante: '{spec['name']}'"
                })
                is_compliant = False

        # Validar consistencia y longitud de tags presentes
        for tag, val in parsed_tags.items():
            if tag in cls.EMV_SPEC_CATALOG:
                spec = cls.EMV_SPEC_CATALOG[tag]
                val_len_bytes = len(val) // 2
                
                if "expected_len_bytes" in spec and val_len_bytes != spec["expected_len_bytes"]:
                    findings.append({
                        "severity": "ERROR",
                        "tag": tag,
                        "description": f"Longitud inválida para {spec['name']}: se esperaban {spec['expected_len_bytes']} bytes, se recibieron {val_len_bytes} bytes."
                    })
                    is_compliant = False

        # Validación cruzada criptográfica: Si hay 9F26 (Criptograma), debe haber 9F27 (CID)
        if "9F26" in parsed_tags and "9F27" not in parsed_tags:
            findings.append({
                "severity": "CRITICAL",
                "tag": "9F27",
                "description": "El payload incluye Criptograma (9F26) pero carece de CID (9F27)."
            })
            is_compliant = False

        return {
            "compliant": is_compliant,
            "total_tags_analyzed": len(parsed_tags),
            "findings_count": len(findings),
            "findings": findings
        }
