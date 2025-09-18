# FST Development Journey: From Rule-Based to Finite State Transducers

## Overview

This document describes the development of a Finite State Transducer (FST) based Hebrew phonemizer, the agent's journey in creating it, and provides a comprehensive tutorial for replicating this development process with local open-source models.

## Table of Contents

1. [How FSTs Work in Phonemization](#how-fsts-work-in-phonemization)
2. [Current Implementation Architecture](#current-implementation-architecture)
3. [Agent Development Journey](#agent-development-journey)
4. [Tutorial: Creating a Local Agent](#tutorial-creating-a-local-agent)
5. [Iterative Development Process](#iterative-development-process)
6. [Key Learnings and Best Practices](#key-learnings-and-best-practices)

## How FSTs Work in Phonemization

### What is a Finite State Transducer?

A Finite State Transducer (FST) is a computational model that maps input sequences to output sequences through a series of states and transitions. In phonemization, FSTs excel because they can:

- **Handle sequential transformations**: Convert character sequences to phoneme sequences
- **Manage context-dependent rules**: Different outputs based on surrounding characters
- **Compose multiple rule layers**: Combine consonant, vowel, and stress rules
- **Optimize performance**: Pre-compiled rules for fast execution

### FST vs Rule-Based Approaches

```
Traditional Rule-Based:
Hebrew Text → Python Rules → IPA Phonemes
     ↓           ↓              ↓
   שָׁלוֹם    → if/else logic → ʃalˈom

FST Approach:
Hebrew Text → Compiled FST → IPA Phonemes
     ↓            ↓            ↓
   שָׁלוֹם    → State Machine → ʃalˈom
```

### Benefits of FST for Hebrew

1. **Complex morphology**: Hebrew's rich morphological system benefits from FST's ability to handle multiple simultaneous transformations
2. **Context sensitivity**: Vowel and consonant pronunciation depends heavily on context
3. **Composability**: Different linguistic rules can be composed as separate FSTs
4. **Performance**: Pre-compiled transducers are faster than runtime rule evaluation

## Current Implementation Architecture

### Hybrid FST-Rule System

Our implementation uses a **hybrid approach** that bridges traditional rule-based logic with FST foundations:

```python
class PhonemizerFST:
    def __init__(self):
        self.consonant_fst = self._build_consonant_fst()    # Hebrew → IPA consonants
        self.vowel_fst = self._build_vowel_fst()           # Nikud → IPA vowels
        self.special_rules_fst = self._build_special_rules_fst()  # Shva, Dagesh
        self.stress_fst = self._build_stress_fst()         # Hatama → Stress
        self.fst = self._compose_fsts()                    # Combined FST
```

### Key Components

#### 1. **Consonant FST**

Maps Hebrew letters to IPA consonants:

- Basic mappings: `א → ʔ`, `ב → v`, `ש → ʃ`
- Geresh handling: `ג׳ → dʒ`, `ז׳ → ʒ`
- Dagesh rules: `בּ → b`, `כּ → k`

#### 2. **Vowel FST**

Handles nikud (Hebrew vowel points):

- `ִ → i` (Hirik)
- `ֶ → e` (Segol)
- `ָ → a` (Qamats)
- `ֹ → o` (Holam)
- `ֻ → u` (Qubuts)

#### 3. **Special Rules FST**

Context-dependent transformations:

- Silent shva: `ְ → ∅`
- Vocal shva: `ְֽ → e`
- Vav patterns: `וֹ → o`, `וּ → u`, `ווֹ → vo`

#### 4. **Stress FST**

Stress marker placement:

- `֫ → ˈ` (Hatama to IPA primary stress)
- Position-aware placement before vowels

### Processing Pipeline

```
Input: שָׁלוֹם
  ↓
1. Normalize Unicode: שָׁלוֹם
  ↓
2. Mark Vocal Shva: שָׁלוֹם (no change)
  ↓
3. Add Stress: שָׁל֫וֹם (milra stress on final syllable)
  ↓
4. Parse Letters: [ש+ָׁ, ל+֫, ו+ֹ, ם]
  ↓
5. Hybrid Phonemization:
   - ש+ָׁ → ['ʃ', 'a']
   - ל+֫ → ['l', 'ˈ'] (stress marker)
   - ו+ֹ → ['o'] (vav-holam = vowel only)
   - ם → ['m']
  ↓
6. Stress Placement: ['ʃ', 'a', 'l', 'ˈ', 'o', 'm'] → ['ʃ', 'a', 'l', 'ˈo', 'm']
  ↓
7. Join & Clean: ʃalˈom
```

## Agent Development Journey

### Phase 1: Analysis & Understanding (Completed)

**Goal**: Understand the existing rule-based system and FST requirements

**Actions Taken**:

- Analyzed `hebrew.py` to understand phonemization logic
- Studied the lexicon mappings and special cases
- Examined test cases to understand expected behavior
- Researched FST theory and pynini library

**Key Insights**:

- Hebrew phonemization has complex context-dependent rules
- Vav (ו) handling is particularly intricate
- Stress placement requires careful vowel detection
- The existing system handles many edge cases

### Phase 2: FST Foundation (Completed)

**Goal**: Build basic FST structures for character mappings

**Actions Taken**:

- Created separate FSTs for consonants, vowels, special rules, and stress
- Implemented basic character-to-phoneme mappings using `pynini.cross()`
- Built FST composition logic to combine multiple transducers

**Challenges**:

- Learning pynini syntax and FST composition
- Understanding how to represent Hebrew Unicode properly
- Balancing FST purity vs practical implementation needs

### Phase 3: Rule Implementation (Completed)

**Goal**: Implement Hebrew-specific phonological rules

**Actions Taken**:

- Translated complex rules from `hebrew.py` to FST-compatible logic
- Implemented vav handling for vowel/consonant determination
- Added geresh and dagesh support
- Created context-sensitive transformations

**Key Decisions**:

- Used hybrid approach: FST for mappings, rules for complex context
- Maintained compatibility with existing preprocessing pipeline
- Preserved all special case handling from original implementation

### Phase 4: Stress Handling (Completed)

**Goal**: Implement proper Hebrew stress placement

**Actions Taken**:

- Analyzed Hebrew stress patterns (milra/milel)
- Implemented position-aware stress placement
- Fixed stress duplication issues
- Ensured IPA-compliant stress marker positioning

**Technical Challenges**:

- Hebrew stress appears on consonants but should precede vowels in IPA
- Multiple stress markers from preprocessing needed deduplication
- Different stress patterns required flexible placement logic

### Phase 5: Testing & Debugging (Completed)

**Goal**: Achieve 100% test pass rate

**Actions Taken**:

- Created debug scripts to trace phonemization process
- Fixed vocal shva conflicts with other vowels
- Resolved vav double-vowel issues
- Optimized stress placement algorithm

**Debugging Process**:

1. **Test Failure**: `שָׁלוֹם` → `ʃalˈoom` (extra 'o')

   - **Root Cause**: Vav producing both consonant and vowel
   - **Fix**: Skip diacritics when vav produces vowel

2. **Test Failure**: `עֶ֫רֶב` → `ʔeˈreˈv` (multiple stress)

   - **Root Cause**: Stress applied per letter + word level
   - **Fix**: Single stress placement with position tracking

3. **Test Failure**: `יָאִיר` → `jaeʔˈir` (extra 'e')
   - **Root Cause**: Vocal shva (meteg) producing vowel alongside qamats
   - **Fix**: Skip vocal shva when other vowels present

## Tutorial: Creating a Local Agent

This section provides a comprehensive guide to creating a local AI agent that can replicate the FST development process using open-source models.

### Prerequisites

```bash
# Required tools
pip install transformers torch accelerate bitsandbytes
pip install guidance langchain
pip install pytest black isort

# Optional: GPU acceleration
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Model Selection

For code generation and iterative development, recommend these open-source models:

1. **Code Llama 34B** (Recommended for best results)
2. **DeepSeek Coder 33B** (Good balance of performance/resources)
3. **WizardCoder 15B** (Lighter option)
4. **Phind CodeLlama 34B** (Specialized for coding tasks)

### Agent Architecture

```python
# agent_framework.py
import subprocess
import json
from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class LocalCodeAgent:
    def __init__(self, model_name: str = "codellama/CodeLlama-34b-Instruct-hf"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            load_in_4bit=True  # Memory optimization
        )
        self.conversation_history = []
        self.iteration_count = 0

    def generate_response(self, prompt: str, max_length: int = 2048) -> str:
        """Generate code/response using the local model"""
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response[len(prompt):].strip()

    def run_command(self, command: str) -> Dict[str, Any]:
        """Execute shell command and return result"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": -1
            }

    def analyze_test_failure(self, test_output: str) -> Dict[str, str]:
        """Parse test failure output to extract key information"""
        lines = test_output.split('\n')
        failure_info = {
            "test_name": "",
            "expected": "",
            "actual": "",
            "error_message": ""
        }

        for i, line in enumerate(lines):
            if "FAILED" in line:
                failure_info["test_name"] = line.split("::")[-1].split()[0]
            elif "assert" in line and "==" in line:
                # Extract expected vs actual from assertion
                parts = line.split("==")
                if len(parts) == 2:
                    failure_info["expected"] = parts[1].strip()
                    failure_info["actual"] = parts[0].split("assert")[-1].strip()
            elif "AssertionError:" in line:
                failure_info["error_message"] = line.split("AssertionError:")[-1].strip()

        return failure_info
```

### Comprehensive Agent Prompt

```python
AGENT_SYSTEM_PROMPT = """
You are an expert software engineer specializing in computational linguistics and finite state transducers.
Your task is to develop a Hebrew phonemizer using FSTs (Finite State Transducers) with the pynini library.

CONTEXT:
- You're working on a Hebrew text-to-phoneme conversion system
- The existing system uses rule-based logic in hebrew.py
- You need to create an FST-based implementation inspired by the existing logic
- The target is to pass all tests in test_phonemize_fst.py

CAPABILITIES YOU HAVE:
1. Read and analyze existing code files
2. Write and modify Python code
3. Run tests and debug failures
4. Execute shell commands with uv
5. Create documentation and debug scripts

DEVELOPMENT METHODOLOGY:
1. **Analyze First**: Always understand the existing system before coding
2. **Incremental Development**: Build and test small pieces
3. **Debug Systematically**: Use debug scripts to trace issues
4. **Test-Driven**: Let test failures guide your development
5. **Document Decisions**: Explain your reasoning for complex choices

HEBREW PHONEMIZATION RULES TO CONSIDER:
- Consonant mappings (א→ʔ, ב→v, etc.)
- Nikud (vowel points) handling (ִ→i, ֶ→e, etc.)
- Special cases: Vav patterns, Geresh, Dagesh
- Stress placement (Hatama ֫ → ˈ before vowels)
- Context-dependent transformations

FST PRINCIPLES:
- Use pynini.cross(input, output) for basic mappings
- Compose FSTs with pynini.union() and pynini.compose()
- Handle context with conditional logic when FST becomes complex
- Balance FST purity with practical implementation needs

CURRENT TASK: {current_task}

ITERATION: {iteration}

PREVIOUS RESULTS: {previous_results}

NEXT STEPS:
{next_steps}
"""

def create_iteration_prompt(agent: LocalCodeAgent, task: str, test_results: Dict) -> str:
    """Create a comprehensive prompt for the current iteration"""

    previous_results = ""
    if agent.conversation_history:
        previous_results = f"""
Previous Iteration Results:
- Actions taken: {agent.conversation_history[-1].get('actions', 'None')}
- Test results: {agent.conversation_history[-1].get('test_results', 'None')}
- Issues found: {agent.conversation_history[-1].get('issues', 'None')}
"""

    next_steps = ""
    if test_results.get("failures"):
        failure_info = agent.analyze_test_failure(test_results["output"])
        next_steps = f"""
IMMEDIATE ISSUE TO FIX:
- Test: {failure_info['test_name']}
- Expected: {failure_info['expected']}
- Actual: {failure_info['actual']}
- Error: {failure_info['error_message']}

Focus on understanding why this specific test is failing and implement a targeted fix.
"""
    else:
        next_steps = "Continue with the next development phase or optimize existing implementation."

    return AGENT_SYSTEM_PROMPT.format(
        current_task=task,
        iteration=agent.iteration_count,
        previous_results=previous_results,
        next_steps=next_steps
    )
```

### Iterative Development Loop

````python
# main_agent_loop.py
def run_development_cycle():
    """Main development loop that mimics the agent's journey"""

    agent = LocalCodeAgent()

    # Development phases
    phases = [
        {
            "name": "Analysis & Understanding",
            "goal": "Understand existing hebrew.py and test requirements",
            "tasks": [
                "Read and analyze phonikud/hebrew.py",
                "Examine test cases in tests/test_phonemize_fst.py",
                "Study lexicon mappings",
                "Research FST theory and pynini usage"
            ]
        },
        {
            "name": "FST Foundation",
            "goal": "Create basic FST structure",
            "tasks": [
                "Implement PhonemizerFST class skeleton",
                "Create consonant FST mappings",
                "Build vowel FST rules",
                "Add special rules FST",
                "Implement FST composition logic"
            ]
        },
        {
            "name": "Rule Implementation",
            "goal": "Add Hebrew-specific phonological rules",
            "tasks": [
                "Implement vav handling logic",
                "Add geresh and dagesh support",
                "Handle context-sensitive transformations",
                "Create hybrid rule-FST approach"
            ]
        },
        {
            "name": "Stress Handling",
            "goal": "Implement proper Hebrew stress placement",
            "tasks": [
                "Analyze Hebrew stress patterns",
                "Implement position-aware stress placement",
                "Fix stress duplication issues",
                "Ensure IPA-compliant output"
            ]
        },
        {
            "name": "Testing & Debugging",
            "goal": "Achieve 100% test pass rate",
            "tasks": [
                "Create debug scripts",
                "Fix test failures systematically",
                "Optimize performance",
                "Clean up code and documentation"
            ]
        }
    ]

    for phase in phases:
        print(f"\n{'='*60}")
        print(f"PHASE: {phase['name']}")
        print(f"GOAL: {phase['goal']}")
        print(f"{'='*60}")

        for task in phase['tasks']:
            success = run_task_iteration(agent, task, phase['name'])
            if not success:
                print(f"Failed on task: {task}")
                break

        # Run tests after each phase
        test_results = agent.run_command("uv run pytest tests/test_phonemize_fst.py -v")

        if test_results["success"]:
            print(f"✅ Phase '{phase['name']}' completed successfully!")
        else:
            print(f"❌ Phase '{phase['name']}' needs more work")
            print("Test output:", test_results["stdout"][-500:])  # Last 500 chars

def run_task_iteration(agent: LocalCodeAgent, task: str, phase: str) -> bool:
    """Run a single task iteration with the agent"""

    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        agent.iteration_count += 1
        attempt += 1

        print(f"\n--- Iteration {agent.iteration_count} ---")
        print(f"Task: {task}")
        print(f"Attempt: {attempt}/{max_attempts}")

        # Run initial test to get current state
        test_results = agent.run_command("uv run pytest tests/test_phonemize_fst.py -v")

        # Create prompt for this iteration
        prompt = create_iteration_prompt(agent, task, {
            "success": test_results["success"],
            "output": test_results["stdout"] + test_results["stderr"],
            "failures": not test_results["success"]
        })

        # Get agent response
        print("🤖 Agent thinking...")
        response = agent.generate_response(prompt)

        # Parse and execute agent's actions
        actions = parse_agent_actions(response)
        results = execute_actions(agent, actions)

        # Store conversation history
        agent.conversation_history.append({
            "iteration": agent.iteration_count,
            "task": task,
            "phase": phase,
            "prompt": prompt[:200] + "...",  # Truncated
            "response": response[:500] + "...",  # Truncated
            "actions": actions,
            "results": results,
            "test_results": test_results
        })

        # Check if task is complete
        final_test = agent.run_command("uv run pytest tests/test_phonemize_fst.py -v")

        if final_test["success"]:
            print("✅ Task completed successfully!")
            return True
        elif attempt == max_attempts:
            print("❌ Max attempts reached, moving to next task")
            return False
        else:
            print(f"🔄 Test still failing, trying again (attempt {attempt+1})")

    return False

def parse_agent_actions(response: str) -> List[Dict[str, str]]:
    """Parse agent response to extract actionable steps"""
    actions = []

    # Look for code blocks
    import re
    code_blocks = re.findall(r'```python\n(.*?)\n```', response, re.DOTALL)
    for code in code_blocks:
        actions.append({
            "type": "write_code",
            "content": code
        })

    # Look for shell commands
    shell_commands = re.findall(r'```bash\n(.*?)\n```', response, re.DOTALL)
    for cmd in shell_commands:
        actions.append({
            "type": "shell_command",
            "content": cmd
        })

    # Look for file operations
    file_ops = re.findall(r'(READ|WRITE|EDIT) FILE: (.*)', response)
    for op, filepath in file_ops:
        actions.append({
            "type": "file_operation",
            "operation": op.lower(),
            "filepath": filepath
        })

    return actions

def execute_actions(agent: LocalCodeAgent, actions: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Execute the parsed actions"""
    results = []

    for action in actions:
        if action["type"] == "shell_command":
            result = agent.run_command(action["content"])
            results.append({
                "action": action,
                "result": result
            })
        elif action["type"] == "write_code":
            # This would need more sophisticated parsing to determine
            # which file to write to and how to structure the code
            print(f"Code to implement:\n{action['content'][:200]}...")
            results.append({
                "action": action,
                "result": {"note": "Code implementation needed"}
            })
        # Add more action types as needed

    return results

if __name__ == "__main__":
    run_development_cycle()
````

### Key Iteration Examples

#### Iteration 1: Initial FST Structure

**Agent Input**:

```
Task: Create basic FST structure
Current State: Empty phonemize_fst.py file
Test Result: ImportError - PhonemizerFST not defined
```

**Agent Response**:

```python
# I need to create the basic FST class structure with pynini
class PhonemizerFST:
    def __init__(self):
        self.consonant_fst = self._build_consonant_fst()
        # ... other FSTs

    def _build_consonant_fst(self):
        rules = []
        for hebrew_char, ipa_phone in lexicon.LETTERS_PHONEMES.items():
            if ipa_phone:
                rules.append(pynini.cross(hebrew_char, ipa_phone))
        return pynini.union(*rules) if rules else pynini.Fst()
```

**Agent Actions**:

1. Write code to phonemize_fst.py
2. Run test: `uv run pytest tests/test_phonemize_fst.py -v`
3. Analyze results

#### Iteration 15: Fixing Vav Double Vowel Issue

**Agent Input**:

```
Task: Fix test failure
Expected: ʃalˈom
Actual: ʃalˈoom
Issue: Vav producing both consonant and vowel sounds
```

**Agent Response**:

```python
# The issue is that vav with holam should only produce vowel 'o', not 'v' + 'o'
# I need to skip diacritics when vav produces a vowel sound

elif cur.char == "ו":
    vav_phonemes, vav_skip_offset = self._handle_vav_simple(cur, prev, next_letter)
    if vav_phonemes:
        cur_phonemes.extend(vav_phonemes)
        skip_consonants = True
        skip_diacritics = True  # <- This is the key fix
        skip_offset = vav_skip_offset
```

**Agent Actions**:

1. Modify vav handling logic
2. Run test to verify fix
3. Debug remaining issues

### Performance Optimization

For better performance with local models:

````python
# Optimize model loading
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# Use guidance for structured generation
from guidance import models, gen, select

guidance_model = models.Transformers(model, tokenizer=tokenizer)

# Structured code generation
with guidance_model.chat():
    guidance_model += "You are a Python expert. Generate code to fix this test failure:"
    guidance_model += f"Error: {error_message}"
    guidance_model += "```python\n"
    guidance_model += gen("code", max_tokens=500, stop="```")
    guidance_model += "\n```"
````

## Iterative Development Process

### The Complete Development Cycle

Each iteration follows this pattern:

1. **Analyze Current State**

   - Run tests to see current failures
   - Examine error messages and stack traces
   - Understand what needs to be implemented/fixed

2. **Plan Solution**

   - Break down the problem into smaller pieces
   - Consider multiple approaches
   - Choose the most appropriate solution

3. **Implement Changes**

   - Write code incrementally
   - Follow established patterns
   - Maintain code quality

4. **Test & Debug**

   - Run tests immediately after changes
   - Create debug scripts when needed
   - Trace through the execution path

5. **Iterate**
   - If tests pass, move to next task
   - If tests fail, analyze and fix
   - Learn from each failure

### Example Iteration Breakdown

**Iteration 1-5**: Basic Structure

- Created FST class skeleton
- Added basic imports and dependencies
- Implemented simple consonant mappings
- Result: Basic structure in place, but no phonemization yet

**Iteration 6-10**: Vowel Handling

- Added nikud (vowel point) mappings
- Implemented vowel FST construction
- Added basic vowel processing
- Result: Simple vowels working, but missing complex rules

**Iteration 11-15**: Complex Rules

- Implemented vav handling for vowel/consonant determination
- Added geresh and dagesh support
- Fixed context-sensitive transformations
- Result: Most phonemization working, stress issues remain

**Iteration 16-20**: Stress Placement

- Analyzed Hebrew stress patterns
- Implemented stress tracking and placement
- Fixed multiple stress marker issues
- Result: Correct stress placement achieved

**Iteration 21-25**: Final Debugging

- Fixed vocal shva conflicts
- Resolved edge cases
- Optimized performance
- Result: All tests passing

## Key Learnings and Best Practices

### Technical Insights

1. **Hybrid Approach Works Best**

   - Pure FST implementation can be overly complex for Hebrew
   - Combining FST foundations with rule-based logic provides flexibility
   - Gradual migration path from rules to FST

2. **Context is Critical**

   - Hebrew phonemization heavily depends on context
   - Position-aware processing is essential
   - Lookahead and lookbehind are frequently needed

3. **Unicode Normalization Matters**

   - Hebrew text can have multiple Unicode representations
   - Consistent normalization prevents subtle bugs
   - Diacritic ordering affects processing

4. **Test-Driven Development Essential**
   - Tests provide immediate feedback on changes
   - Edge cases are revealed through systematic testing
   - Regression prevention is crucial

### Agent Development Insights

1. **Incremental Progress**

   - Small, testable changes are more effective than large rewrites
   - Each iteration should have a clear, measurable goal
   - Build confidence through early wins

2. **Debug Scripts Are Invaluable**

   - Visibility into the processing pipeline prevents guesswork
   - Character-by-character analysis reveals issues quickly
   - Unicode inspection tools are essential for Hebrew text

3. **Pattern Recognition**

   - Similar issues appear across different test cases
   - Generic solutions are often better than specific fixes
   - Code patterns can be reused across similar problems

4. **Documentation During Development**
   - Recording decisions and reasoning helps with later debugging
   - Understanding the "why" is as important as the "what"
   - Future maintainers (including yourself) will appreciate context

### Recommendations for Local Agent Development

1. **Start Simple**

   - Begin with basic functionality
   - Add complexity incrementally
   - Validate each step before proceeding

2. **Invest in Tooling**

   - Good debugging tools pay for themselves quickly
   - Automated testing catches regressions early
   - Code formatting and linting maintain quality

3. **Learn from Failures**

   - Each failed test teaches something valuable
   - Systematic debugging develops better intuition
   - Failed approaches often inform successful ones

4. **Balance Automation and Human Insight**
   - Agents excel at systematic, repetitive tasks
   - Human insight is valuable for architectural decisions
   - Hybrid human-agent development is often most effective

## Conclusion

The development of the Hebrew FST phonemizer demonstrates how systematic, iterative development can tackle complex linguistic programming challenges. The hybrid FST-rule approach provides a practical solution that balances theoretical FST principles with real-world implementation constraints.

For developers looking to create similar systems:

1. **Understand the domain deeply** before starting implementation
2. **Use tests as your guide** for development direction
3. **Build incrementally** with frequent validation
4. **Debug systematically** with good tooling
5. **Document your journey** for future reference

The local agent approach shown here can be adapted for many other complex development tasks, providing a framework for systematic problem-solving with AI assistance.

---

_This documentation was created as part of the FST development process and serves as both a technical reference and a tutorial for replicating the development methodology._
