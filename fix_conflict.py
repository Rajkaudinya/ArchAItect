import re

with open(r'c:\ArchAItect\backend\app\services\analyzer_v2.py', encoding='utf-8') as f:
    content = f.read()

# Locate remaining conflict block (lines 188-318)
head_marker = '<<<<<<< HEAD\n        print(f"[ANALYSIS] Analyzing requirements document: {filename}")'
idx = content.find(head_marker)
print('HEAD marker at char:', idx)

end_marker = '>>>>>>> 1542567 (flowchart , fr-ids , questions)\n        result = AnalysisResult'
end_idx = content.find(end_marker)
print('END marker at char:', end_idx)

if idx >= 0 and end_idx >= 0:
    old_block = content[idx:end_idx + len('>>>>>>> 1542567 (flowchart , fr-ids , questions)\n')]
    print('Block length:', len(old_block))
    print('First 100 chars:', repr(old_block[:100]))
    print('Last 100 chars:', repr(old_block[-100:]))
