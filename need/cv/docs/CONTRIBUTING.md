# Contribution Rules (v2)

## 1. Repository Rule
DrishtiSetu is ONE integrated project. Do not create separate repositories for individual modules.

## 2. Branches
```text
main
feature/risk-engine
feature/computer-vision
feature/gis-data
feature/rag-nlp
feature/agentic-ai
feature/platform-integration
```
`main` must remain runnable at all times.

## 3. Module Ownership
| Member | Module |
|---|---|
| 1 | ML + Risk |
| 2 | Computer Vision |
| 3 | GIS + Data |
| 4 | RAG + NLP |
| 5 | Agentic AI + Relocation |
| 6 | Frontend + Backend + Integration |

## 4. Contract Test Requirement
Every module must pass unit and contract test suites against `API_CONTRACT.md` before merging.
