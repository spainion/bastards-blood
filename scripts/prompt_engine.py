#!/usr/bin/env python3
"""Prompt engineering engine for complex LLM interactions."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional


def ensure_prompt_dirs():
    """Ensure prompt directories exist."""
    dirs = [
        "data/prompts",
        "data/prompts/templates",
        "data/prompts/chains"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


# Built-in prompt templates
BUILTIN_TEMPLATES = {
    "narration": {
        "id": "narration",
        "name": "Narrative Description",
        "description": "Generate narrative descriptions for scenes and events",
        "system_prompt": """You are a skilled narrator for a tabletop RPG campaign called "Bastards Blood". 
Your role is to create vivid, immersive descriptions that engage players and bring the world to life.

Guidelines:
- Use sensory details (sights, sounds, smells, textures)
- Maintain consistent tone with the campaign's dark fantasy setting
- Be concise but evocative
- Leave room for player agency and choices
- Reference established lore and characters when relevant""",
        "user_template": """Describe the following scene or event:

{{scene_description}}

Characters present: {{characters}}
Location: {{location}}
Mood: {{mood}}

Provide a narrative description that:
1. Sets the atmosphere
2. Highlights important details
3. Engages the senses
4. Suggests possible actions or interactions""",
        "variables": ["scene_description", "characters", "location", "mood"]
    },
    
    "dialogue": {
        "id": "dialogue",
        "name": "NPC Dialogue",
        "description": "Generate in-character dialogue for NPCs",
        "system_prompt": """You are a dialogue writer for a tabletop RPG. You create authentic, 
character-appropriate dialogue for NPCs based on their personality, background, and current situation.

Guidelines:
- Stay in character at all times
- Use appropriate speech patterns and vocabulary
- Reflect the NPC's emotions and motivations
- Provide useful information or hooks when appropriate
- Keep responses concise and actionable""",
        "user_template": """Generate dialogue for the following NPC:

NPC Name: {{npc_name}}
Role: {{npc_role}}
Personality: {{personality}}
Current Mood: {{mood}}
Speaking to: {{speaking_to}}
Context: {{context}}

The NPC should respond to: {{player_action}}

Provide 2-3 dialogue options ranging from helpful to neutral to potentially hostile.""",
        "variables": ["npc_name", "npc_role", "personality", "mood", "speaking_to", "context", "player_action"]
    },
    
    "combat_description": {
        "id": "combat_description",
        "name": "Combat Narration",
        "description": "Generate exciting combat descriptions",
        "system_prompt": """You are a combat narrator for a tabletop RPG. You create dynamic, 
exciting descriptions of combat actions that make battles feel cinematic and impactful.

Guidelines:
- Make attacks feel impactful and visceral
- Vary descriptions to avoid repetition
- Reflect character fighting styles
- Include environmental interactions when possible
- Keep the pace fast and exciting""",
        "user_template": """Describe this combat action:

Attacker: {{attacker}} ({{attacker_class}})
Target: {{target}}
Action: {{action_type}}
Weapon/Ability: {{weapon}}
Result: {{result}} ({{damage}} damage)
Critical: {{is_critical}}

Environment: {{environment}}

Provide a vivid 2-3 sentence description of this action.""",
        "variables": ["attacker", "attacker_class", "target", "action_type", "weapon", "result", "damage", "is_critical", "environment"]
    },
    
    "world_building": {
        "id": "world_building",
        "name": "World Building",
        "description": "Generate world lore and location details",
        "system_prompt": """You are a world builder for the "Bastards Blood" campaign. You create 
rich, detailed lore that fits the established setting while adding depth and mystery.

Guidelines:
- Maintain consistency with existing lore
- Add hooks for potential adventures
- Include historical and cultural details
- Create memorable names and descriptions
- Leave some elements mysterious""",
        "user_template": """Create content for the following:

Type: {{content_type}}
Name: {{name}}
Region: {{region}}
Related to: {{related_elements}}
Tone: {{tone}}
Special requirements: {{requirements}}

Provide:
1. A brief overview (2-3 sentences)
2. Key details and features
3. Potential plot hooks or secrets
4. Connections to existing elements""",
        "variables": ["content_type", "name", "region", "related_elements", "tone", "requirements"]
    },
    
    "character_voice": {
        "id": "character_voice",
        "name": "Character Voice",
        "description": "Generate character-specific responses and actions",
        "system_prompt": """You are embodying a specific character in a tabletop RPG. 
Stay true to their personality, background, and motivations in all responses.

Guidelines:
- Use the character's speech patterns consistently
- React based on their personality traits
- Reference their backstory when relevant
- Show their growth and development
- Balance character flaws with strengths""",
        "user_template": """As {{character_name}}, respond to this situation:

Character Details:
- Class: {{character_class}}
- Background: {{background}}
- Personality: {{personality}}
- Current state: {{current_state}}

Situation: {{situation}}

Provide:
1. Internal thoughts (1-2 sentences)
2. Verbal response
3. Physical action or body language""",
        "variables": ["character_name", "character_class", "background", "personality", "current_state", "situation"]
    },
    
    "dm_assistant": {
        "id": "dm_assistant",
        "name": "DM Assistant",
        "description": "Provide DM guidance and suggestions",
        "system_prompt": """You are an experienced Dungeon Master assistant. You help DMs run 
engaging sessions by providing tactical advice, story suggestions, and game management tips.

Guidelines:
- Offer multiple options when possible
- Consider player enjoyment and agency
- Suggest ways to handle unexpected situations
- Provide rule clarifications when needed
- Help maintain narrative consistency""",
        "user_template": """Help with the following DM challenge:

Current situation: {{situation}}
Players involved: {{players}}
Session goal: {{goal}}
Difficulty level: {{difficulty}}
Specific question: {{question}}

Provide:
1. Direct answer to the question
2. Alternative approaches
3. Things to consider
4. Potential consequences""",
        "variables": ["situation", "players", "goal", "difficulty", "question"]
    },
    
    "rules_query": {
        "id": "rules_query",
        "name": "Rules Query",
        "description": "Answer rules questions and provide clarifications",
        "system_prompt": """You are a rules expert for tabletop RPGs. You provide clear, 
accurate rules interpretations while maintaining fun and fairness.

Guidelines:
- Cite specific rules when possible
- Explain the reasoning behind rules
- Offer RAW (Rules As Written) and RAI (Rules As Intended) interpretations
- Suggest house rule alternatives when appropriate
- Prioritize fun over strict adherence""",
        "user_template": """Answer this rules question:

Question: {{question}}
Context: {{context}}
System: {{game_system}}
Relevant characters/abilities: {{relevant_elements}}

Provide:
1. Direct answer
2. Rule citation or reference
3. Common edge cases
4. Optional house rule suggestion""",
        "variables": ["question", "context", "game_system", "relevant_elements"]
    },
    
    "story_generation": {
        "id": "story_generation",
        "name": "Story Generation",
        "description": "Generate story elements and plot developments",
        "system_prompt": """You are a story generator for tabletop RPGs. You create compelling 
narrative elements that drive the story forward while respecting player agency.

Guidelines:
- Create meaningful choices and consequences
- Include personal stakes for characters
- Balance mystery with clarity
- Layer plots at different scales
- Include foreshadowing and callbacks""",
        "user_template": """Generate story content:

Type: {{story_type}}
Tone: {{tone}}
Characters involved: {{characters}}
Current plot threads: {{plot_threads}}
Desired outcome: {{desired_outcome}}
Constraints: {{constraints}}

Create:
1. Setup/hook
2. Key developments
3. Potential complications
4. Possible resolutions
5. Future implications""",
        "variables": ["story_type", "tone", "characters", "plot_threads", "desired_outcome", "constraints"]
    },
    
    "encounter_design": {
        "id": "encounter_design",
        "name": "Encounter Design",
        "description": "Design combat and non-combat encounters",
        "system_prompt": """You are an encounter designer for tabletop RPGs. You create 
balanced, engaging encounters that challenge players while remaining fair.

Guidelines:
- Match difficulty to party capabilities
- Include environmental elements
- Provide multiple solutions
- Consider pacing and resource drain
- Include non-combat options when possible""",
        "user_template": """Design an encounter:

Type: {{encounter_type}}
Party composition: {{party}}
Difficulty: {{difficulty}}
Environment: {{environment}}
Story purpose: {{purpose}}
Special requirements: {{requirements}}

Provide:
1. Encounter overview
2. Enemy/obstacle details
3. Tactical considerations
4. Possible outcomes
5. Rewards and consequences""",
        "variables": ["encounter_type", "party", "difficulty", "environment", "purpose", "requirements"]
    }
}


def load_template(template_id: str) -> Optional[dict]:
    """Load a prompt template by ID."""
    # Check built-in templates first
    if template_id in BUILTIN_TEMPLATES:
        return BUILTIN_TEMPLATES[template_id]
    
    # Check custom templates
    template_path = f"data/prompts/templates/{template_id}.json"
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            return json.load(f)
    
    return None


def save_template(template: dict) -> str:
    """Save a custom template."""
    ensure_prompt_dirs()
    template_id = template.get("id", f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    template["id"] = template_id
    template["created_at"] = datetime.now(timezone.utc).isoformat()
    
    template_path = f"data/prompts/templates/{template_id}.json"
    with open(template_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    return template_id


def list_templates() -> dict:
    """List all available templates."""
    templates = []
    
    # Built-in templates
    for tid, template in BUILTIN_TEMPLATES.items():
        templates.append({
            "id": tid,
            "name": template.get("name"),
            "description": template.get("description"),
            "builtin": True
        })
    
    # Custom templates
    templates_dir = "data/prompts/templates"
    if os.path.exists(templates_dir):
        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                with open(os.path.join(templates_dir, filename), 'r') as f:
                    template = json.load(f)
                    templates.append({
                        "id": template.get("id"),
                        "name": template.get("name"),
                        "description": template.get("description"),
                        "builtin": False
                    })
    
    return {"count": len(templates), "templates": templates}


def render_template(template: dict, variables: dict) -> dict:
    """Render a template with provided variables."""
    system_prompt = template.get("system_prompt", "")
    user_template = template.get("user_template", "")
    
    # Simple variable substitution
    rendered_user = user_template
    for var, value in variables.items():
        placeholder = "{{" + var + "}}"
        rendered_user = rendered_user.replace(placeholder, str(value) if value else "[not provided]")
    
    return {
        "system_prompt": system_prompt,
        "user_prompt": rendered_user,
        "template_id": template.get("id"),
        "variables_used": list(variables.keys())
    }


def generate_prompt(template_id: str, variables: dict, include_context: bool, model_hints: dict) -> dict:
    """Generate a complete prompt from template."""
    template = load_template(template_id)
    
    if not template:
        return {"error": f"Template not found: {template_id}"}
    
    rendered = render_template(template, variables)
    
    result = {
        "template_id": template_id,
        "template_name": template.get("name"),
        "system_prompt": rendered["system_prompt"],
        "user_prompt": rendered["user_prompt"],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Add model hints
    if model_hints:
        result["model_hints"] = model_hints
    
    # Add context if requested
    if include_context:
        # Import context engine functionality
        from context_engine import build_full_game_state
        context = build_full_game_state(2000, True, 10)
        result["context"] = context
    
    return result


def store_template(template_id: str, variables: dict, model_hints: dict) -> dict:
    """Store a new custom template."""
    template = {
        "id": template_id,
        "name": variables.get("name", template_id),
        "description": variables.get("description", "Custom template"),
        "system_prompt": variables.get("system_prompt", ""),
        "user_template": variables.get("user_template", ""),
        "variables": variables.get("variables", [])
    }
    
    saved_id = save_template(template)
    return {"stored": True, "template_id": saved_id}


def compose_chain(chain_id: str, templates: list, variables: dict) -> dict:
    """Compose a chain of prompts for multi-step generation."""
    ensure_prompt_dirs()
    
    chain = {
        "id": chain_id,
        "steps": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    for i, template_id in enumerate(templates):
        template = load_template(template_id)
        if template:
            chain["steps"].append({
                "step": i + 1,
                "template_id": template_id,
                "template_name": template.get("name"),
                "depends_on": i if i > 0 else None
            })
    
    # Save chain
    chain_path = f"data/prompts/chains/{chain_id}.json"
    with open(chain_path, 'w') as f:
        json.dump(chain, f, indent=2)
    
    return {"composed": True, "chain": chain}


def main():
    parser = argparse.ArgumentParser(description='Prompt engine')
    parser.add_argument('--action', required=True,
                       choices=['generate_prompt', 'store_template', 'get_template',
                               'list_templates', 'compose_chain', 'execute_chain'])
    parser.add_argument('--template-id', default='')
    parser.add_argument('--prompt-type', default='custom')
    parser.add_argument('--include-context', default='true')
    parser.add_argument('--variables-file', help='Path to variables JSON file')
    parser.add_argument('--model-hints-file', help='Path to model hints JSON file')
    
    args = parser.parse_args()
    
    include_context = args.include_context.lower() == 'true'
    
    variables = {}
    if args.variables_file and os.path.exists(args.variables_file):
        with open(args.variables_file, 'r') as f:
            try:
                variables = json.load(f)
            except json.JSONDecodeError:
                pass
    
    model_hints = {}
    if args.model_hints_file and os.path.exists(args.model_hints_file):
        with open(args.model_hints_file, 'r') as f:
            try:
                model_hints = json.load(f)
            except json.JSONDecodeError:
                pass
    
    template_id = args.template_id or args.prompt_type
    
    handlers = {
        'generate_prompt': lambda: generate_prompt(template_id, variables, include_context, model_hints),
        'store_template': lambda: store_template(template_id, variables, model_hints),
        'get_template': lambda: {"template": load_template(template_id)},
        'list_templates': list_templates,
        'compose_chain': lambda: compose_chain(template_id, variables.get("templates", []), variables),
        'execute_chain': lambda: {"action": "execute_chain", "message": "Chain execution not yet implemented"}
    }
    
    result = handlers[args.action]()
    
    with open('/tmp/prompt_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
