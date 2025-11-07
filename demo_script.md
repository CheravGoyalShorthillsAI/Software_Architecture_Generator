# Demo Video Script (≈5 minutes)

**0:00 – 0:30 | Hello and problem**
- “Hi everyone, I’m Amrit. Thanks for joining. Today I’ll walk through *The Genesis Engine*. It’s a helper that turns a single idea into a full software architecture in minutes. No long meetings, no guess work.”

**0:30 – 1:00 | What happens behind the scenes**
- “I give the app a short prompt. In the background three AI agents wake up: an architect that designs the system, a systems analyst that checks the tech risks, and a biz-ops analyst that looks at cost and operations. All their notes go into Tiger Postgres so we can search them later.”

**1:00 – 2:30 | Create a project and show the result**
- “Let me show you. I’ll paste a prompt, hit *Generate*. The app shows the project as ‘processing’ while the agents work.”
- “If I open the History page you can see older runs. I’ll click one that finished.”
- “Here’s the blueprint: name, overview, pros and cons. Scroll down and you get a Mermaid diagram.”
- “Further down are the two analysis sections. The systems agent warns about technical issues, the biz-ops agent talks about cost, team, and compliance. It’s like having a panel of experts in seconds.”

**2:30 – 3:30 | Hybrid search**
- “Everything is searchable. I can type something like ‘Kafka cost’ or ‘GDPR risk’. Because we store both text and vector embeddings in Postgres, the search understands keywords and meaning. I get the exact findings, ready to read or copy into a doc.”

**3:30 – 4:00 | Diagram**
- “Back at the top, the Mermaid diagram gives a quick visual. It shows the services, data stores, event bus – perfect for architecture reviews.”

**4:00 – 4:30 | Why Postgres matters here**
- “This runs on Agentic Postgres. We use Tiger CLI to create database forks for the agents, pg_text plus pgvector for hybrid search, and we store every result in one place. It’s fast to run, easy to query, and everything stays versioned.”

**4:30 – 5:00 | Wrap-up**
- “So that’s The Genesis Engine. You give it an idea, it gives back a complete plan, all the analysis, and a searchable history. It saves teams from building the wrong thing and gives everyone a shared source of truth. Thanks for watching!”


