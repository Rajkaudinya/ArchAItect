with open(r'c:\ArchAItect\backend\app\services\analyzer_v2.py', encoding='utf-8') as f:
    content = f.read()

head_marker = '<<<<<<< HEAD\n        print(f"[ANALYSIS] Analyzing requirements document: {filename}")'
end_marker = '>>>>>>> 1542567 (flowchart , fr-ids , questions)\n        result = AnalysisResult'

idx = content.find(head_marker)
end_idx = content.find(end_marker)
end_pos = end_idx + len('>>>>>>> 1542567 (flowchart , fr-ids , questions)\n')

# Replacement: new branch body with step 7 using _calculate_metrics_with_breakdown
replacement = '''        print(f"[ANALYSIS] Analyzing requirements document: {filename}")

        # Append clarification answers as extra context so LLM sees them
        enriched_text = text
        if clarification_answers:
            notes = "\\n\\n=== CLARIFICATION ANSWERS ===\\n"
            for qa in clarification_answers:
                q = qa.get("question", "")
                a = qa.get("answer", "").strip()
                if a:
                    notes += f"Q: {q}\\nA: {a}\\n\\n"
            enriched_text = text + notes
            print(f"   Appended {len(clarification_answers)} clarification answers to context")

        # Step 1: NLP extraction — actors, capabilities, entities, FR-IDs
        print("[Step 1] NLP extraction...")
        extraction = self.nlp_engine.extract_entities_and_actions(enriched_text)
        entities   = extraction.get("entities", [])
        actions    = extraction.get("actions", [])
        fr_ids     = self.nlp_engine.extract_fr_ids(enriched_text)
        actors     = self.nlp_engine.extract_actors(enriched_text)
        capabilities = self.nlp_engine.extract_capabilities(enriched_text)
        print(f"   {len(actors)} actors, {len(capabilities)} capabilities, {len(fr_ids)} FR-IDs")

        # Step 2: Build exactly 6 canonical services (LLM-enriched)
        print("[Step 2] Building 6 canonical microservices via LLM...")
        services = self._build_six_canonical_services(enriched_text, actors, capabilities, entities)
        print(f"   {len(services)} services built")

        # Step 3: Clarification questions (surface ambiguities for the user)
        print("[Step 3] Detecting clarification questions...")
        domain_tuples = [(t["domain"], 80.0, t["keywords"], "") for t in CANONICAL_SERVICES]
        clarifications = ClarificationEngine().detect_ambiguities(
            enriched_text, entities, actors, capabilities, fr_ids, domain_tuples
        )
        print(f"   {len(clarifications)} clarifications")

        # Step 4: Flow diagram
        print("[Step 4] Generating user-journey flow diagram...")
        flow_diagram = self._generate_llm_flow_diagram(actors, capabilities, entities, domain_tuples, enriched_text)

        # Step 5: Canonical dependencies (filtered by document presence)
        print("[Step 5] Building canonical service dependencies...")
        dependencies = self._build_canonical_dependencies(enriched_text)
        print(f"   {len(dependencies)} dependencies")

        # Step 6: FR-ID assignment and impact map
        svc_fr_ids = self._assign_fr_ids_to_canonical(services, fr_ids, enriched_text)
        impact_map = self._compute_impact_map(svc_fr_ids)

        # Step 7: Metrics with statistical breakdown
        print("[Step 7] Computing architecture quality metrics with statistical analysis...")
        metrics, metrics_breakdown = self._calculate_metrics_with_breakdown(services, dependencies, enriched_text)

        # Step 8: Traceability matrix
        print("[Step 8] Building requirements traceability matrix...")
        traceability = self._build_traceability_canonical(enriched_text, services, fr_ids)

        preview = enriched_text[:500] + "..." if len(enriched_text) > 500 else enriched_text

        '''

new_content = content[:idx] + replacement + content[end_pos:]

with open(r'c:\ArchAItect\backend\app\services\analyzer_v2.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done. Conflict block replaced.")

# Verify no conflict markers remain
remaining = new_content.count('<<<<<<<')
print(f"Remaining conflict markers: {remaining}")
