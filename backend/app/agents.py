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
    
    async def generate_text(self, prompt: str) -> str:
        """
        Generate text using Gemini AI.
        
        Args:
            prompt: The input prompt for text generation
            
        Returns:
            Generated text response
        """
        try:
            response = await self.model.generate_content_async(prompt)
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
        
        # Generate Mermaid diagrams for each blueprint
        logger.info("Generating Mermaid diagrams for blueprints...")
        diagram_tasks = [generate_mermaid_diagram(bp) for bp in blueprints]
        diagrams = await asyncio.gather(*diagram_tasks)
        
        # Add diagrams to blueprints
        for blueprint, diagram in zip(blueprints, diagrams):
            blueprint["mermaid_diagram"] = diagram
        
        logger.info(f"Successfully generated microservices architectural blueprint with diagram")
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


async def generate_mermaid_diagram(blueprint: Dict[str, Any]) -> str:
    """
    Generate a Mermaid diagram for the architecture blueprint using Gemini AI.
    
    Args:
        blueprint: The architecture blueprint dictionary containing name, description, pros, and cons
        
    Returns:
        A string containing valid Mermaid.js diagram syntax
    """
    agent = GeminiAgent()
    
    prompt = f"""You are an expert software architect and diagram designer. Generate a comprehensive, beautiful Mermaid.js flowchart diagram for the following architecture blueprint.

ARCHITECTURE BLUEPRINT:
Name: {blueprint['name']}
Description: {blueprint['description']}

REQUIREMENTS:
1. Use "graph TB" (top-to-bottom) layout
2. Include ALL services, databases, message queues, caches, and infrastructure components mentioned in the description
3. Show relationships between components with proper arrows (solid for direct calls, dashed for events/async)
4. Use these style classes:
   - clientClass: for client/browser (pink #ec4899)
   - gatewayClass: for API gateways (orange #f59e0b)
   - serviceClass: for microservices (blue #3b82f6)
   - dbClass: for databases (green #10b981)
   - queueClass: for message queues, cache, Redis (purple #8b5cf6)
5. Add appropriate emojis to components (e.g., 👤 for client, 🌐 for gateway, 🔐 for auth, 🗄️ for database, 📨 for message broker)
6. Create a clear, well-organized diagram that shows the complete system architecture
7. Label arrows with meaningful text (e.g., "REST", "WebSocket", "events", "queries")
8. If service mesh is mentioned, use a subgraph
9. Make it visually appealing and easy to understand

OUTPUT FORMAT:
Return ONLY the raw Mermaid diagram syntax. Do NOT include markdown code fences, explanations, or any other text.
Start directly with "graph TB" and include all class definitions.

EXAMPLE STRUCTURE:
graph TB
    classDef serviceClass fill:#3b82f6,stroke:#1e40af,stroke-width:2px,color:#fff
    classDef dbClass fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    classDef queueClass fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff
    classDef gatewayClass fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    classDef clientClass fill:#ec4899,stroke:#db2777,stroke-width:2px,color:#fff

    Client[👤 Client/Browser]:::clientClass
    Gateway[🌐 API Gateway]:::gatewayClass
    ...
    
Generate a detailed, production-quality Mermaid diagram now:"""

    try:
        logger.info(f"Generating Mermaid diagram for blueprint: {blueprint['name']}")
        mermaid_syntax = await agent.generate_text(prompt)
        
        # Clean up the response - remove markdown code fences if present
        mermaid_syntax = mermaid_syntax.strip()
        if mermaid_syntax.startswith("```mermaid"):
            mermaid_syntax = mermaid_syntax[10:]
        if mermaid_syntax.startswith("```"):
            mermaid_syntax = mermaid_syntax[3:]
        if mermaid_syntax.endswith("```"):
            mermaid_syntax = mermaid_syntax[:-3]
        mermaid_syntax = mermaid_syntax.strip()
        
        # Validate it starts with graph TB
        if not mermaid_syntax.startswith("graph TB") and not mermaid_syntax.startswith("graph TD"):
            logger.warning("Generated diagram doesn't start with 'graph TB', adding it...")
            mermaid_syntax = "graph TB\n" + mermaid_syntax
        
        logger.info(f"Successfully generated Mermaid diagram ({len(mermaid_syntax)} characters)")
        return mermaid_syntax
        
    except Exception as e:
        logger.error(f"Mermaid diagram generation failed: {str(e)}")
        # Return a fallback simple diagram
        return f"""graph TB
    classDef serviceClass fill:#3b82f6,stroke:#1e40af,stroke-width:2px,color:#fff
    classDef clientClass fill:#ec4899,stroke:#db2777,stroke-width:2px,color:#fff
    
    Client[👤 Client/Browser]:::clientClass
    System[⚙️ {blueprint['name']}]:::serviceClass
    Client --> System
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
