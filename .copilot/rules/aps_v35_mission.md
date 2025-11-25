# 🧠 ADA-AI / SWARM J2C – Metodología APS v3.5  
**Agent Prompt Specification Framework**

---

## 🎯 Propósito general

Este repositorio implementa la metodología **APS v3.5**, cuyo objetivo es **estructurar, validar y versionar los prompts de los agentes del swarm J2C**.  
El propósito de Copilot es **entender el contexto funcional del swarm**, y actuar dentro de un entorno gobernado por reglas y estados formales (`STATE_JSON`, `ada.status`, `covered.*`, etc.).

---

## 🧩 Fundamentos técnicos

- Cada agente del swarm tiene su **prompt formalizado** en un archivo YAML dentro de `/swarm/aps/<agent>/agent.aps.yaml`.  
- Estos YAMLs sustituyen a los antiguos `.md` como **fuente de verdad** y están diseñados para ser interpretados por el **orquestador ADA-AI**.  
- La estructura de cada YAML incluye:
  - `sections.role` → Rol y contexto del agente.  
  - `sections.goals` → Objetivos funcionales.  
  - `sections.constraints` → Reglas y contratos (con `sid` estables).  
  - `policies.output` → Formato de salida y control de handoff.  
  - `metadata.prompt_checksum` → Hash de integridad del prompt original.  

---

## ⚙️ Responsabilidad de Copilot

1. **No sugerir cambios directos** sobre los `.md` históricos (solo YAML).  
2. **Respetar la semántica funcional**: nunca alterar `sid`, `phase` ni `handoff`.  
3. **Mantener coherencia estructural** entre YAMLs de los agentes.  
4. **Ayudar a validar** cambios mediante los scripts del directorio `/scripts/`.  
5. **Priorizar legibilidad, consistencia y compatibilidad con orquestador.**

---

## 🧭 Contexto metodológico

- La metodología APS v3.5 forma parte del framework **ADA-AI (Agent-Driven Architecture)**.  
- Sigue el patrón **ADA Swarm** → Motivaciones → Stakeholders → ASIS → Riesgos → GAP → Requisitos → Informe.  
- Cada agente implementa una fase del flujo; la coordinación está a cargo del **Orchestrator**.  

---

## 🛡️ Principio rector

> “Los prompts ya no son texto: son **componentes arquitectónicos versionables**.”

---

## 🧠 Recordatorio persistente

Al abrir este repositorio, Copilot debe **asumir este contexto** y aplicar las reglas APS v3.5 en todas las sugerencias.  
El objetivo no es solo generar código, sino **garantizar integridad semántica entre los agentes**.

---
© ADA-AI · SWARM J2C · APS v3.5