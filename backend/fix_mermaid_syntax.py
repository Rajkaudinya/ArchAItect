"""
Fix invalid Mermaid syntax in existing analysis files
"""
import json
import re
from pathlib import Path

def fix_mermaid_syntax(mermaid_code: str) -> str:
    """Fix common invalid Mermaid arrow syntax"""
    if not mermaid_code:
        return mermaid_code
    
    # Fix invalid solid arrow syntax: -->|label|> → -->|label|
    fixed = re.sub(r"-->\|([^|]+)\|>", r"-->|\1|", mermaid_code)
    # Fix invalid dashed arrow syntax: -.->|label|> → -.->|label|
    fixed = re.sub(r"-\.\->\|([^|]+)\|>", r"-.->|\1|", fixed)
    # Fix invalid dashed arrow syntax (old): --|label|> → -.->|label|
    fixed = re.sub(r"--\|([^|]+)\|>", r"-.->|\1|", fixed)
    # Fix invalid dashed arrow without label: --|> → -.->
    fixed = re.sub(r"--\|>", r"-.->", fixed)
    
    return fixed

def main():
    data_dir = Path(__file__).parent / "data"
    fixed_count = 0
    
    # Process all analysis files
    for json_file in data_dir.glob("analysis_*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if there's a flow_diagram to fix
            if "analysis_metadata" in data and "flow_diagram" in data["analysis_metadata"]:
                original = data["analysis_metadata"]["flow_diagram"]
                fixed = fix_mermaid_syntax(original)
                
                if original != fixed:
                    data["analysis_metadata"]["flow_diagram"] = fixed
                    
                    # Write back to file
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    fixed_count += 1
                    print(f"✅ Fixed: {json_file.name}")
        
        except Exception as e:
            print(f"❌ Error processing {json_file.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Fixed {fixed_count} analysis file(s) with invalid Mermaid syntax")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
