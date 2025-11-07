"""
AI Agents for The Genesis Engine

This module contains AI agent implementations using Google's Gemini API
and other AI services for intelligent automation and responses.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional

import google.generativeai as genai
from .config import Settings

# Initialize settings
settings = Settings()

# Configure Gemini AI
genai.configure(api_key=settings.gemini_api_key)

EMBEDDING_MODEL_NAME = settings.gemini_embedding_model
EMBEDDING_DIMENSION = settings.gemini_embedding_dimension

class GeminiAgent:
    """AI Agent using Google's Gemini model for text generation and analysis."""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model = genai.GenerativeModel(model_name or settings.gemini_model_name)
    
    async def generate_text(self, prompt: str, temperature: float = 1.0, max_output_tokens: int = 8192) -> str:
        """
        Generate text using Gemini AI.
        
        Args:
            prompt: The input prompt for text generation
            temperature: Sampling temperature (0.0-2.0). Higher = more creative
            max_output_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini AI generation failed: {str(e)}")
    
    async def analyze_content(self, content: str, analysis_type: str = "general") -> str:
        """
        Analyze content using Gemini AI.
        
        Args:
            content: The content to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        prompt = f"Analyze the following content for {analysis_type} insights:\n\n{content}"
        return await self.generate_text(prompt)

# Global agent instance
gemini_agent = GeminiAgent()

# Setup logging
logger = logging.getLogger(__name__)


async def generate_embedding(text_to_embed: str) -> List[float]:
    """Generate an embedding vector for the provided text using Gemini."""
    if not text_to_embed:
        return []

    def _embed_sync() -> List[float]:
        response = genai.embed_content(
            model=EMBEDDING_MODEL_NAME,
            content=text_to_embed
        )
        embedding = response.get("embedding")
        if embedding is None:
            raise ValueError("Embedding response did not contain an embedding vector")
        embedding_list = list(embedding)
        if EMBEDDING_DIMENSION and len(embedding_list) != EMBEDDING_DIMENSION:
            logger.warning(
                "Received embedding dimension %s, expected %s",
                len(embedding_list),
                EMBEDDING_DIMENSION
            )
        return embedding_list

    try:
        return await asyncio.to_thread(_embed_sync)
    except Exception as exc:
        logger.error("Failed to generate embedding: %s", exc)
        raise Exception(f"Embedding generation failed: {exc}") from exc


async def run_architect_agent(user_prompt: str) -> List[Dict[str, Any]]:
    """
    Generate a microservices architectural blueprint using Gemini AI.
    
    Args:
        user_prompt: User's project description/requirements
        
    Returns:
        List containing one microservices blueprint dictionary with keys: name, description, pros, cons
    """
    system_prompt = """You are a Senior Software Architect with expertise in designing scalable, cloud-native microservices systems.

Your task is to analyze the user's project requirements and design a MICROSERVICES ARCHITECTURE.

CRITICAL INSTRUCTIONS:
1. Return ONLY a valid JSON array containing exactly 1 object
2. The object must have these keys: "name", "description", "pros", "cons"
3. "name": String (max 255 chars) - Should include "Microservices" in the name
4. "description": String - Detailed technical description of the microservices architecture including:
   - Core microservices and their responsibilities
   - Communication patterns (REST APIs, message queues, event-driven)
   - Data management strategy (database per service, shared databases, etc.)
   - Infrastructure considerations (containers, orchestration, service mesh)
5. "pros": Array of objects with "point" and "description" keys - advantages (4-6 items)
6. "cons": Array of objects with "point" and "description" keys - disadvantages/challenges (4-6 items)
7. NO extra text, explanations, or markdown - ONLY the JSON array

Example format:
[
  {
    "name": "Cloud-Native Microservices Architecture",
    "description": "Distributed system with independent services deployed in containers, communicating via REST APIs and event streaming. Each service owns its data and can be developed, deployed, and scaled independently.",
    "pros": [
      {"point": "Independent Scalability", "description": "Each microservice can scale horizontally based on its specific load patterns"},
      {"point": "Technology Flexibility", "description": "Teams can choose optimal tech stacks per service"},
      {"point": "Fault Isolation", "description": "Failures in one service don't cascade to others"},
      {"point": "Faster Development", "description": "Teams work independently with smaller, focused codebases"}
    ],
    "cons": [
      {"point": "Operational Complexity", "description": "Requires robust DevOps practices and infrastructure automation"},
      {"point": "Distributed System Challenges", "description": "Network latency, service discovery, and inter-service communication overhead"},
      {"point": "Data Consistency", "description": "Managing transactions across services requires eventual consistency patterns"},
      {"point": "Testing Complexity", "description": "Integration and end-to-end testing becomes more complex"}
    ]
  }
]

Design a comprehensive microservices architecture for this project:"""

    try:
        full_prompt = f"{system_prompt}\n\nProject Requirements:\n{user_prompt}"
        
        response = await gemini_agent.generate_text(full_prompt)
        
        # Clean up response (remove markdown code blocks if present)
        cleaned_response = response.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        # Parse JSON response
        blueprints = json.loads(cleaned_response)
        
        # Validate response structure
        if not isinstance(blueprints, list) or len(blueprints) != 1:
            raise ValueError(f"Expected exactly 1 blueprint, got {len(blueprints) if isinstance(blueprints, list) else 'non-list'}")
        
        for i, blueprint in enumerate(blueprints):
            required_keys = ["name", "description", "pros", "cons"]
            if not all(key in blueprint for key in required_keys):
                missing_keys = [key for key in required_keys if key not in blueprint]
                raise ValueError(f"Blueprint {i+1} missing required keys: {missing_keys}")
        
        logger.info(f"Successfully generated microservices architectural blueprint (diagram will be generated after analyses)")
        return blueprints
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response from architect agent: {str(e)}")
        logger.error(f"Raw response: {response}")
        raise Exception(f"Invalid JSON response from architect agent: {str(e)}")
    except Exception as e:
        logger.error(f"Architect agent failed: {str(e)}")
        raise Exception(f"Failed to generate architectural blueprints: {str(e)}")


async def run_analyst_agents(
    blueprint: Dict[str, Any], 
    custom_systems_prompt: Optional[str] = None,
    custom_bizops_prompt: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Analyze a blueprint using two different analyst personas in parallel.
    
    Args:
        blueprint: Blueprint dictionary with name, description, pros, cons
        custom_systems_prompt: Optional custom prompt for systems analyst (overrides default)
        custom_bizops_prompt: Optional custom prompt for bizops analyst (overrides default)
        
    Returns:
        Combined list of analysis objects with keys: category, finding, severity
    """
    
    # Default prompts
    default_systems_prompt = """You are a Senior Systems Analyst with deep expertise in system architecture, performance, scalability, and technical risk assessment.

Your task is to analyze the provided architectural blueprint and identify potential issues, risks, and concerns from a SYSTEMS perspective.

CRITICAL INSTRUCTIONS:
1. Return ONLY a valid JSON array of analysis objects
2. Each object must have these keys: "category", "finding", "severity"
3. "category": String (max 100 chars) - Type of analysis (e.g., "Performance", "Security", "Scalability", "Reliability", "Maintainability")
4. "finding": String - Detailed technical finding or concern
5. "severity": Integer (1-10) - Risk level where 1=low, 10=critical
6. Focus on: Performance bottlenecks, scalability limits, security vulnerabilities, reliability issues, technical debt risks
7. Provide 2-4 analyses
8. NO extra text, explanations, or markdown - ONLY the JSON array

Example format:
[
  {
    "category": "Performance",
    "finding": "Database queries may become bottleneck under high load without proper indexing strategy",
    "severity": 7
  }
]

Analyze this architecture:"""

    default_bizops_prompt = """You are a Senior Business Operations (BizOps) Analyst with expertise in operational efficiency, cost analysis, team dynamics, and business risk assessment.

Your task is to analyze the provided architectural blueprint from a BUSINESS OPERATIONS perspective.

CRITICAL INSTRUCTIONS:
1. Return ONLY a valid JSON array of analysis objects
2. Each object must have these keys: "category", "finding", "severity"
3. "category": String (max 100 chars) - Type of analysis (e.g., "Cost", "Operations", "Team Structure", "Deployment", "Monitoring", "Compliance")
4. "finding": String - Detailed operational or business finding
5. "severity": Integer (1-10) - Business impact level where 1=low, 10=critical
6. Focus on: Operational complexity, cost implications, team skill requirements, deployment challenges, monitoring needs, compliance issues
7. Provide 2-4 analyses
8. NO extra text, explanations, or markdown - ONLY the JSON array

Example format:
[
  {
    "category": "Operations",
    "finding": "Requires specialized DevOps team with container orchestration expertise, increasing operational overhead",
    "severity": 6
  }
]

Analyze this architecture:"""

    # Use custom prompts if provided, otherwise use defaults
    systems_analyst_prompt = custom_systems_prompt if custom_systems_prompt else default_systems_prompt
    bizops_analyst_prompt = custom_bizops_prompt if custom_bizops_prompt else default_bizops_prompt

    # Prepare blueprint context for analysis
    blueprint_context = f"""
Architecture Name: {blueprint.get('name', 'Unknown')}
Description: {blueprint.get('description', 'No description provided')}

Pros: {json.dumps(blueprint.get('pros', []), indent=2)}
Cons: {json.dumps(blueprint.get('cons', []), indent=2)}
"""

    async def run_systems_analysis() -> List[Dict[str, Any]]:
        """Run systems analyst persona."""
        try:
            full_prompt = f"{systems_analyst_prompt}\n{blueprint_context}"
            response = await gemini_agent.generate_text(full_prompt)
            
            # Clean up response
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            analyses = json.loads(cleaned_response)
            
            # Validate structure
            if not isinstance(analyses, list):
                raise ValueError("Systems analyst response must be a JSON array")
            
            for analysis in analyses:
                required_keys = ["category", "finding", "severity"]
                if not all(key in analysis for key in required_keys):
                    missing_keys = [key for key in required_keys if key not in analysis]
                    raise ValueError(f"Systems analysis missing required keys: {missing_keys}")
                
                if not isinstance(analysis["severity"], int) or not (1 <= analysis["severity"] <= 10):
                    raise ValueError(f"Invalid severity value: {analysis['severity']} (must be 1-10)")
            
            # Add agent_type to track which agent generated this analysis
            for analysis in analyses:
                analysis['agent_type'] = 'systems'
            
            logger.info(f"Systems analyst generated {len(analyses)} analyses")
            return analyses
            
        except Exception as e:
            logger.error(f"Systems analyst failed: {str(e)}")
            raise Exception(f"Systems analysis failed: {str(e)}")

    async def run_bizops_analysis() -> List[Dict[str, Any]]:
        """Run BizOps analyst persona."""
        try:
            full_prompt = f"{bizops_analyst_prompt}\n{blueprint_context}"
            response = await gemini_agent.generate_text(full_prompt)
            
            # Clean up response
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            analyses = json.loads(cleaned_response)
            
            # Validate structure
            if not isinstance(analyses, list):
                raise ValueError("BizOps analyst response must be a JSON array")
            
            for analysis in analyses:
                required_keys = ["category", "finding", "severity"]
                if not all(key in analysis for key in required_keys):
                    missing_keys = [key for key in required_keys if key not in analysis]
                    raise ValueError(f"BizOps analysis missing required keys: {missing_keys}")
                
                if not isinstance(analysis["severity"], int) or not (1 <= analysis["severity"] <= 10):
                    raise ValueError(f"Invalid severity value: {analysis['severity']} (must be 1-10)")
            
            # Add agent_type to track which agent generated this analysis
            for analysis in analyses:
                analysis['agent_type'] = 'bizops'
            
            logger.info(f"BizOps analyst generated {len(analyses)} analyses")
            return analyses
            
        except Exception as e:
            logger.error(f"BizOps analyst failed: {str(e)}")
            raise Exception(f"BizOps analysis failed: {str(e)}")

    try:
        # Run both analyses in parallel
        systems_analyses, bizops_analyses = await asyncio.gather(
            run_systems_analysis(),
            run_bizops_analysis()
        )
        
        # Combine results
        all_analyses = systems_analyses + bizops_analyses
        
        logger.info(f"Successfully completed parallel analysis. Total analyses: {len(all_analyses)}")
        return all_analyses
        
    except Exception as e:
        logger.error(f"Parallel analyst agents failed: {str(e)}")
        raise Exception(f"Failed to analyze blueprint: {str(e)}")


def fix_mermaid_syntax(mermaid_code: str) -> str:
    """
    Fix common Mermaid syntax errors that LLMs generate.
    
    Removes:
    - Parentheses () in subgraph and node labels
    - Commas in labels (replace with 'and' or hyphens)
    - Other problematic characters
    
    Args:
        mermaid_code: Raw Mermaid diagram code
        
    Returns:
        Cleaned Mermaid code with valid syntax
    """
    import re
    
    logger.info("Cleaning up Mermaid syntax...")
    
    # Fix subgraph labels: subgraph ID[Label with (parentheses, commas)]
    # Pattern: subgraph SomeID[text with (parens) and, commas]
    def fix_subgraph_label(match):
        id_part = match.group(1)
        label = match.group(2)
        # Remove parentheses and their contents
        label = re.sub(r'\([^)]*\)', '', label)
        # Replace commas with 'and'
        label = label.replace(',', ' and')
        # Clean up extra spaces
        label = re.sub(r'\s+', ' ', label).strip()
        return f'subgraph {id_part}[{label}]'
    
    mermaid_code = re.sub(
        r'subgraph\s+(\w+)\[([^\]]+)\]',
        fix_subgraph_label,
        mermaid_code
    )
    
    # Fix node labels: NodeID["Label with (parentheses, commas)"]
    def fix_node_label(match):
        node_id = match.group(1)
        quote = match.group(2)  # " or '
        label = match.group(3)
        # Remove parentheses and their contents
        label = re.sub(r'\([^)]*\)', '', label)
        # Replace commas with 'and' or just remove
        label = label.replace(',', ' and')
        # Clean up extra spaces
        label = re.sub(r'\s+', ' ', label).strip()
        # Keep <br/> tags intact
        return f'{node_id}[{quote}{label}{quote}]'
    
    mermaid_code = re.sub(
        r'(\w+)\[([\"\'])([^\"\']+)\2\]',
        fix_node_label,
        mermaid_code
    )
    
    logger.info("✅ Mermaid syntax cleanup complete")
    return mermaid_code


async def generate_mermaid_diagram(
    blueprint_with_analyses: Dict[str, Any], 
    user_prompt: str = ""
) -> str:
    """
    Generate a comprehensive, production-grade Mermaid.js architecture diagram using Gemini AI.
    This is called AFTER all analyses are complete, so risk markers can be added based on findings.
    
    Args:
        blueprint_with_analyses: Complete blueprint with analyses array included
        user_prompt: The original user's project requirements for additional context
        
    Returns:
        A string containing valid Mermaid.js diagram syntax
    """
    agent = GeminiAgent()
    
    # Create full project context (complete API response structure with analyses)
    full_project_context = {
        "project": {
            "user_prompt": user_prompt,
            "status": "generating_diagram"
        },
        "blueprints": [blueprint_with_analyses]  # Include blueprint WITH analyses
    }
    
    # Convert to JSON string - ensure NO truncation
    project_json = json.dumps(full_project_context, indent=2, ensure_ascii=False)
    
    prompt = f"""🚨 CRITICAL SYSTEM INSTRUCTION - READ FIRST 🚨

YOU MUST CREATE A DETAILED ARCHITECTURE DIAGRAM WITH 20-30+ NODES.
THIS IS A MANDATORY REQUIREMENT. SMALL DIAGRAMS (< 15 nodes) ARE COMPLETELY UNACCEPTABLE AND WILL BE REJECTED.

Your output MUST include:
✓ 8-12 domain-specific microservices (NOT generic services)
✓ 8-12 separate databases (one per service)
✓ Infrastructure components (Gateway, Load Balancer, Message Broker, Cache, Kubernetes, Monitoring)
✓ ALL connections labeled with protocols

If your diagram has fewer than 20 nodes, IT IS WRONG. Start over and add more services and databases.

═══════════════════════════════════════════════════════════════════════════════

Now generate a **complete production-grade Mermaid.js architecture diagram** for the given project blueprint below.

SYSTEM INPUT (Full API Response - DO NOT TRUNCATE):
═══════════════════════════════
{project_json}
═══════════════════════════════

IMPORTANT: Use ALL information above. The description contains critical details about services, databases, and infrastructure components.

TASK:
You are a Senior Cloud Architect and Mermaid Diagram Expert.
Your job is to **analyze the SPECIFIC blueprint description** and create a **domain-specific, production-grade microservices architecture** tailored to THIS project.

⚠️ CRITICAL: DO NOT use generic templates. Every diagram must be unique based on the actual requirements.

────────────────────────────
📋 STEP 1: ANALYZE THE PROJECT
────────────────────────────

Before creating the diagram, answer these questions by reading the "user_prompt" and "description" fields:

1. What is the CORE BUSINESS DOMAIN? (e.g., cafe management, medical store, e-commerce, hospital, etc.)
2. What are the PRIMARY USER ACTIONS? (e.g., order food, manage prescriptions, book appointments)
3. What ENTITIES/RESOURCES exist? (e.g., menu items, medicines, patients, orders, inventory)
4. What WORKFLOWS are described? (e.g., order → kitchen → delivery, prescription upload → verification → dispensing)
5. What INTEGRATION POINTS are mentioned? (payment gateways, email, SMS, third-party APIs)

Use these answers to determine the SPECIFIC services needed for THIS domain.

────────────────────────────
🔍 STEP 2: ANALYZE RISK FINDINGS
────────────────────────────

The API response includes an "analyses" array with findings from Systems Analyst and BizOps Analyst.
Review these analyses to identify:
- High-risk services (severity 8-10) - mark with ⚠️ in the diagram
- Performance bottlenecks - mark with 🔥
- Security concerns - mark with 🔒
- Reliability issues - mark with ⚡

For example, if analyses mention "Auth Service has authorization risks" → label it as "🔐⚠️ Auth Service"

────────────────────────────
🎯 STEP 3: DIAGRAM REQUIREMENTS
────────────────────────────

1. **Domain-Specific Services (MANDATORY - 8-12 services minimum):**
   
   ⚠️ CRITICAL: You MUST create at least 8-12 domain-specific microservices. A small diagram is UNACCEPTABLE.
   
   **Example - Cafe Management System should have:**
   - 🔐 Auth Service (JWT/OAuth)
   - 👥 User Profile Service
   - ☕ Order Management Service (place orders, track status)
   - 📋 Menu Service (items, pricing, availability)
   - 🍳 Kitchen Management Service (order queue, preparation)
   - 💳 Payment Service (transactions, invoices)
   - 📦 Inventory Service (stock tracking)
   - 👨‍🍳 Staff Management Service (shifts, roles)
   - 📊 Analytics Service (sales reports, trends)
   - 📧 Notification Service (order updates, promotions)
   - 🚚 Delivery Service (if delivery is mentioned)
   - ⭐ Review/Rating Service (if feedback is mentioned)
   
   **Example - Medical Store should have:**
   - 🔐 Auth Service
   - 👥 User/Patient Service
   - 💊 Medicine Catalog Service (drug database)
   - 📝 Prescription Service (upload, verify, manage)
   - 🏥 Pharmacy Inventory Service (stock management)
   - 💳 Billing Service
   - 👨‍⚕️ Doctor Verification Service (if prescriptions need validation)
   - 📦 Order Fulfillment Service
   - 🚚 Delivery Service
   - 📧 Notification Service
   - 📊 Reporting Service (compliance, audits)
   - 🔍 Drug Interaction Check Service
   
   DO NOT create a tiny diagram with just "API Gateway → Service → Database". That is WRONG.

2. **Data & Communication Layers (SHOW EACH COMPONENT):**
   
   ⚠️ IMPORTANT: Show the DATABASE FOR EACH SERVICE separately!
   
   For a system with 10 services, you should show:
   - 10 separate database nodes (🗄️ Auth DB, 🗄️ Order DB, 🗄️ Menu DB, etc.)
   - 1 Message Broker (📨 Kafka/RabbitMQ) - for async events
   - 1 Redis Cache (⚡ Redis) - for performance
   - 1 API Gateway (🌐 API Gateway)
   - 1 Load Balancer
   
   This gives you 10 services + 10 databases + 4 infrastructure = **24 nodes minimum**

3. **Infrastructure & DevOps Components (context-appropriate):**
   - Kubernetes Cluster (☸️) - for production systems
   - Service Mesh (Istio) - if inter-service security/observability is critical
   - Monitoring (Prometheus + Grafana) - if mentioned or implied for production
   - Logging (ELK Stack) - if observability is emphasized
   - Cloud Provider layer (AWS/GCP/Azure) - if cloud-native is mentioned
   - CDN - ONLY if static content delivery or global distribution is needed

4. **Connections & Flows:**
   - REST/gRPC → solid lines (`-->`)
   - Async events → dashed lines (`-.->`)
   - Data flow/stream → thick arrows (`==>`)
   - Label every connection (`|REST|`, `|WebSocket|`, `|events|`, etc.)
   - Include both real-time and asynchronous paths.

5. **Layout & Style:**
   - Use `graph TB` layout (top-to-bottom)
   - Group components into subgraphs:
     - Client Layer
     - Gateway Layer
     - Service Layer
     - Data Layer
     - Infrastructure Layer
   - Keep clients at top, infra at bottom.
   - Minimum 15–20 nodes.

6. **Style Definitions (classDef):**
classDef clientClass fill:#ec4899,stroke:#db2777,stroke-width:3px,color:#fff
classDef gatewayClass fill:#f59e0b,stroke:#d97706,stroke-width:3px,color:#fff
classDef serviceClass fill:#3b82f6,stroke:#1e40af,stroke-width:2px,color:#fff
classDef dbClass fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
classDef queueClass fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff
classDef cacheClass fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
classDef infraClass fill:#84cc16,stroke:#65a30d,stroke-width:2px,color:#fff

⚠️ CRITICAL MERMAID.JS SYNTAX RULES - MUST FOLLOW:
1. Subgraph labels: NO parentheses () or commas , allowed
   - CORRECT: subgraph ServiceMesh[Service Mesh - Istio - mTLS]
   - WRONG: subgraph ServiceMesh[Service Mesh (Istio) - mTLS, Observability]
2. Node labels: NO parentheses () or commas , in square brackets
   - CORRECT: Gateway["API Gateway - JWT Validation and Routing"]
   - WRONG: Gateway["API Gateway (JWT Validation, Routing)"]
3. Use <br/> for line breaks in node labels, not commas
   - CORRECT: Node["Service A<br/>Feature 1 and Feature 2"]
   - WRONG: Node["Service A (Feature 1, Feature 2)"]
4. Use hyphens, "and", or <br/> instead of commas and parentheses

7. **Use Domain-Appropriate Emojis:**
Generic: 👤 Client | 🔐 Auth | 👥 User | 📨 Message Broker | ⚡ Cache | 🗄️ DB | ☸️ Kubernetes | 🕸️ Istio | 📊 Prometheus | 📈 Grafana | 🪵 ELK
Domain-Specific Examples:
- Cafe: ☕ Order Service | 📋 Menu Service | 🍳 Kitchen Service | 🚚 Delivery Service
- Medical: 💊 Medicine Service | 📝 Prescription Service | 🏥 Pharmacy Service | 📦 Inventory Service
- Hospital: 👨‍⚕️ Doctor Service | 🛏️ Appointment Service | 💬 Chat Service | 🚑 Emergency Service

8. **Output Requirements:**
- Return only Mermaid syntax
- No explanations or markdown fences
- Start directly with: `graph TB`
- **MINIMUM 20-30 NODES REQUIRED** (anything less is unacceptable)
- Must show: Client → Gateway → Multiple Services (8-12) → Multiple Databases (8-12) → Infrastructure
- EVERY PROJECT SHOULD PRODUCE A DIFFERENT DIAGRAM based on its unique domain requirements

⚠️ UNACCEPTABLE DIAGRAMS (DO NOT CREATE):
❌ Only 5-8 nodes total
❌ Single generic "Service" node instead of specific services
❌ Single "Database" instead of one per service
❌ Missing domain-specific services (Order Service, Menu Service, etc.)

✅ ACCEPTABLE DIAGRAMS:
✓ 20-30+ nodes total
✓ 8-12 named, domain-specific services
✓ Separate database for each service
✓ Clear infrastructure layer (Kubernetes, Monitoring, etc.)

────────────────────────────
📐 DIAGRAM STRUCTURE (follow this pattern):
────────────────────────────

graph TB
    %% Style Definitions
    classDef clientClass fill:#ec4899,stroke:#db2777,stroke-width:3px,color:#fff
    classDef gatewayClass fill:#f59e0b,stroke:#d97706,stroke-width:3px,color:#fff
    classDef serviceClass fill:#3b82f6,stroke:#1e40af,stroke-width:2px,color:#fff
    classDef dbClass fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    classDef queueClass fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff
    classDef cacheClass fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
    classDef infraClass fill:#84cc16,stroke:#65a30d,stroke-width:2px,color:#fff
    
    %% Client Layer
    Client[👤 Web/Mobile Client]:::clientClass
    
    %% Gateway Layer
    LB[🌐 Load Balancer]:::gatewayClass
    Gateway[🌐 API Gateway]:::gatewayClass
    
    %% Service Layer (8-12 domain-specific services)
    subgraph ServiceMesh[Service Mesh - Istio - mTLS and Observability]
        AuthService[🔐 Auth Service]:::serviceClass
        Service2[📋 Specific Service 2]:::serviceClass
        Service3[🔔 Specific Service 3]:::serviceClass
        %% ... continue for 8-12 total services based on domain
    end
    
    %% Data Layer (one DB per service)
    AuthDB[(🗄️ Auth DB<br/>PostgreSQL)]:::dbClass
    Service2DB[(🗄️ ... DB 2 ...)]:::dbClass
    %% ... continue for each service
    
    %% Infrastructure
    MsgBroker[📨 Message Broker<br/>Kafka]:::queueClass
    Cache[⚡ Redis Cache]:::cacheClass
    
    subgraph K8s[☸️ Kubernetes Cluster]
        Monitoring[📊 Prometheus]:::infraClass
        Grafana[📈 Grafana]:::infraClass
    end
    
    %% Connections
    Client --> LB
    LB --> Gateway
    Gateway --> AuthService
    Gateway --> Service2
    AuthService --> AuthDB
    AuthService -.->|events| MsgBroker
    %% ... continue connections

────────────────────────────
NOW GENERATE THE COMPLETE DIAGRAM:
────────────────────────────"""

    try:
        logger.info(f"Generating Mermaid diagram for blueprint: {blueprint_with_analyses['name']}")
        
        # DEBUG: Log the full prompt length and key details
        logger.info(f"DEBUG: Full prompt length: {len(prompt)} characters")
        logger.info(f"DEBUG: Blueprint has {len(blueprint_with_analyses.get('analyses', []))} analyses")
        logger.info(f"DEBUG: Sending request to Gemini AI with high token limit...")
        
        # Use higher temperature and max tokens for detailed diagrams
        mermaid_syntax = await agent.generate_text(
            prompt,
            temperature=1.2,  # Higher creativity for comprehensive diagrams
            max_output_tokens=8192  # Allow long, detailed diagrams
        )
        
        # DEBUG: Log the raw response details
        logger.info(f"DEBUG: Received diagram response length: {len(mermaid_syntax)} characters")
        logger.info(f"DEBUG: Counting nodes in response...")
        
        # Count approximate nodes (lines with [text])
        import re
        node_matches = re.findall(r'\[.*?\]', mermaid_syntax)
        logger.info(f"DEBUG: Approximate node count in response: {len(node_matches)}")
        
        if len(node_matches) < 15:
            logger.warning(f"⚠️ WARNING: Diagram has only {len(node_matches)} nodes - EXPECTED 20-30+!")
            logger.warning(f"⚠️ This suggests the LLM is not following the detailed instructions.")
            logger.info(f"DEBUG: First 500 chars of response: {mermaid_syntax[:500]}")
        else:
            logger.info(f"✅ Good: Diagram has {len(node_matches)} nodes")
        
        # Clean up the response - remove markdown code fences if present
        mermaid_syntax = mermaid_syntax.strip()
        if mermaid_syntax.startswith("```mermaid"):
            mermaid_syntax = mermaid_syntax[10:]
        if mermaid_syntax.startswith("```"):
            mermaid_syntax = mermaid_syntax[3:]
        if mermaid_syntax.endswith("```"):
            mermaid_syntax = mermaid_syntax[:-3]
        mermaid_syntax = mermaid_syntax.strip()
        
        # FIX COMMON SYNTAX ERRORS - Clean up problematic characters
        logger.info("Applying Mermaid syntax cleanup...")
        mermaid_syntax = fix_mermaid_syntax(mermaid_syntax)
        
        # Validate it starts with graph TB
        if not mermaid_syntax.startswith("graph TB") and not mermaid_syntax.startswith("graph TD"):
            logger.warning("Generated diagram doesn't start with 'graph TB', adding it...")
            mermaid_syntax = "graph TB\n" + mermaid_syntax
        
        logger.info(f"Successfully generated Mermaid diagram ({len(mermaid_syntax)} characters)")
        return mermaid_syntax
        
    except Exception as e:
        logger.error(f"Mermaid diagram generation failed: {str(e)}")
        # Return a fallback detailed diagram
        return f"""graph TB
    classDef clientClass fill:#ec4899,stroke:#db2777,stroke-width:3px,color:#fff
    classDef gatewayClass fill:#f59e0b,stroke:#d97706,stroke-width:3px,color:#fff
    classDef serviceClass fill:#3b82f6,stroke:#1e40af,stroke-width:2px,color:#fff
    classDef dbClass fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    classDef queueClass fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff
    classDef cacheClass fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
    
    Client[👤 Client/Browser]:::clientClass
    Gateway[🌐 API Gateway]:::gatewayClass
    Service[⚙️ Microservice]:::serviceClass
    DB[(🗄️ Database)]:::dbClass
    Cache[⚡ Cache]:::cacheClass
    Queue[📨 Message Queue]:::queueClass
    
    Client --> Gateway
    Gateway -->|REST| Service
    Service -->|queries| DB
    Service -->|cache| Cache
    Service -.->|events| Queue
"""


# Utility function to run full pipeline
async def generate_full_project_analysis(user_prompt: str) -> List[Dict[str, Any]]:
    """
    Run the complete analysis pipeline: generate blueprints and analyze each one.
    
    Args:
        user_prompt: User's project requirements
        
    Returns:
        List of blueprint dictionaries with embedded analyses
    """
    try:
        # Generate blueprints
        blueprints = await run_architect_agent(user_prompt)
        
        # Analyze each blueprint in parallel
        analysis_tasks = []
        for blueprint in blueprints:
            analysis_tasks.append(run_analyst_agents(blueprint))
        
        all_analyses = await asyncio.gather(*analysis_tasks)
        
        # Embed analyses into blueprints
        for i, blueprint in enumerate(blueprints):
            blueprint["analyses"] = all_analyses[i]
        
        logger.info(f"Completed full project analysis for {len(blueprints)} blueprints")
        return blueprints
        
    except Exception as e:
        logger.error(f"Full project analysis failed: {str(e)}")
        raise Exception(f"Failed to generate complete project analysis: {str(e)}")
