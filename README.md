# fintech-local-ai-rag-auditor 🤖🔒

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Showcase-purple?style=for-the-badge&logo=github)](https://alejano.github.io/fintech-local-ai-rag-auditor/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-teal?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)](https://python.org)

**Autor:** Alejandro Barragán Jasso  
**Enfoque:** Tech Lead / Mobile & Embedded Payment Systems Engineer

> 🌐 **Página Web Interactiva:** Visita las diapositivas interactivas y prueba el auditor de tramas TLV en [alejano.github.io/fintech-local-ai-rag-auditor](https://alejano.github.io/fintech-local-ai-rag-auditor/).

---

## 🎯 Objetivo de la Publicación

Uso de IA Local (LLaMA 3 + LangChain) y FastAPI para auditar mensajes y tramas financieras sin enviar ningún dato confidencial a la nube, garantizando cumplimiento normativo estricto (*Air-Gapped*).

Capacidades del auditor:
1. **Decodificación BER-TLV:** Parseo de tramas binarias y tags de 1 y 2 bytes.
2. **Validación de Especificaciones:** Verificación de longitud exacta de criptogramas (`9F26` = 8 bytes), presencia obligatoria de CID (`9F27`), AIP (`82`) y montos (`9F02`).
3. **Proxy Interceptor FastAPI:** Endpoint `/api/v1/audit/emv` para inspección en tiempo real durante desarrollo con hardware físico.

---

## 🚀 Cómo Probar el Código

### Modo Consola:
```bash
python local_audit_service.py
```

### Modo Servidor API:
```bash
uvicorn local_audit_service:app --reload --port 8000
```
Swagger UI disponible en: `http://localhost:8000/docs`

---

## 📱 Publicación en LinkedIn
El texto para LinkedIn y el guión del carrusel están en [POST_LINKEDIN.md](POST_LINKEDIN.md).
