"""
Clarification Engine — detects requirement ambiguities before boundary detection.

Applies three rule-based checks and returns up to 5 targeted questions for the
user. Each question includes the source line that triggered it and a description
of how the answer changes the generated architecture.
"""
import re
from typing import List, Dict, Any, Tuple


class ClarificationEngine:
    """
    Three ambiguity rules:

    1. entity_no_actor     – a noun is mentioned ≥3 times but never assigned
                             to an actor in a modal sentence ("X shall …").
    2. long_flow_no_boundary – >4 capabilities are chained in close document
                             proximity without any transaction-boundary term.
    3. capability_no_data  – a verb-object capability exists whose object noun
                             is not recognised as owned data in any domain.
    """

    def detect_ambiguities(
        self,
        text: str,
        entities: List[Dict],
        actors: List[Dict],
        capabilities: List[Dict],
        fr_ids: Dict[str, List[Dict]],
        domains: List[Tuple],
    ) -> List[Dict[str, Any]]:
        """
        Return ≤5 clarification questions, each a dict with:
          type      – rule class
          question  – the question to surface to the user
          line      – 1-indexed line in the document that triggered the question
          sentence  – the source sentence (truncated to 120 chars)
          impact    – what changes in the architecture depending on the answer
        """
        questions: List[Dict] = []
        questions.extend(self._rule_entity_no_actor(entities, actors, text))
        questions.extend(self._rule_long_flow_no_boundary(capabilities))
        questions.extend(self._rule_capability_no_data(capabilities, domains))

        seen: set = set()
        unique: List[Dict] = []
        for q in questions:
            if q["question"] not in seen:
                seen.add(q["question"])
                unique.append(q)
            if len(unique) >= 5:
                break
        return unique

    # ── Rule 1 ────────────────────────────────────────────────────────────────

    def _rule_entity_no_actor(
        self,
        entities: List[Dict],
        actors: List[Dict],
        text: str,
    ) -> List[Dict]:
        """
        Entities mentioned ≥3 times that never appear in a sentence where an
        actor is also the subject (modal clause).  No actor → no data owner →
        the boundary detector cannot tell which service should own this noun.
        """
        # Collect sentences that already contain an actor's modal action
        actor_sentences: set = set()
        for actor_info in actors:
            for sent_entry in actor_info.get("sentences", []):
                actor_sentences.add(sent_entry.get("sentence", "").lower())

        lines = text.split("\n")
        questions: List[Dict] = []

        for ent_info in entities[:30]:
            val = ent_info.get("value", "")
            if len(val) < 3:
                continue
            mention_count = text.lower().count(val)
            if mention_count < 3:
                continue
            if any(val in s for s in actor_sentences):
                continue  # already has an actor context

            line_num = ent_info.get("line", 1)
            sentence = lines[line_num - 1].strip() if line_num <= len(lines) else ""
            questions.append({
                "type": "entity_no_actor",
                "question": (
                    f"'{val}' is mentioned {mention_count}× but no actor is assigned "
                    f"to manage it. Who owns '{val}'?"
                ),
                "line": line_num,
                "sentence": sentence[:120],
                "impact": (
                    f"Determines which service owns '{val}' data. "
                    f"Without an owner, the boundary detector may split or absorb "
                    f"it incorrectly, producing a spurious service."
                ),
            })
            if len(questions) >= 2:
                break

        return questions

    # ── Rule 2 ────────────────────────────────────────────────────────────────

    def _rule_long_flow_no_boundary(
        self, capabilities: List[Dict]
    ) -> List[Dict]:
        """
        Detects windows of >4 capabilities clustered within 30 document lines
        without a transaction-boundary signal.  Long flows without boundaries
        often indicate a missing saga/coordinator service.
        """
        BOUNDARY_TERMS = {
            "payment", "auth", "transaction", "rollback", "compensat",
            "saga", "lock", "atomic", "commit", "idempotent",
        }

        if len(capabilities) <= 4:
            return []

        sorted_caps = sorted(
            [c for c in capabilities if c.get("sentences")],
            key=lambda c: c["sentences"][0].get("line", 9999),
        )

        for i in range(len(sorted_caps) - 4):
            window = sorted_caps[i : i + 5]
            first_line = window[0]["sentences"][0].get("line", 1)
            last_line = window[-1]["sentences"][0].get("line", 1)

            if last_line - first_line > 30:
                continue

            window_text = " ".join(c["capability"] for c in window).lower()
            if any(t in window_text for t in BOUNDARY_TERMS):
                continue

            names = ", ".join(c["capability"] for c in window[:4])
            return [{
                "type": "long_flow_no_boundary",
                "question": (
                    f"The flow '{names}…' chains 5+ steps with no transaction boundary. "
                    f"Does any step require atomic commit/rollback if a later step fails?"
                ),
                "line": first_line,
                "sentence": names[:120],
                "impact": (
                    "If yes, a Saga pattern or distributed transaction coordinator "
                    "is needed — adds a service and changes the dependency topology."
                ),
            }]

        return []

    # ── Rule 3 ────────────────────────────────────────────────────────────────

    def _rule_capability_no_data(
        self,
        capabilities: List[Dict],
        domains: List[Tuple],
    ) -> List[Dict]:
        """
        Capabilities whose object noun is not present in any domain's owned_data
        or matched keywords.  The object is an undefined data scope — a service
        built around it would be hallucinated.
        """
        all_owned: set = set()
        for domain_tuple in domains:
            if len(domain_tuple) >= 3:
                for kw in domain_tuple[2]:
                    all_owned.add(kw.lower())

        questions: List[Dict] = []
        for cap_info in capabilities[:25]:
            cap = cap_info["capability"]
            parts = cap.lower().split(None, 1)
            if len(parts) < 2:
                continue
            obj_noun = parts[1].strip()
            if len(obj_noun) < 3:
                continue
            in_owned = any(
                obj_noun in owned or owned in obj_noun for owned in all_owned
            )
            if not in_owned and cap_info.get("sentences"):
                line_num = cap_info["sentences"][0].get("line", 1)
                sentence = cap_info["sentences"][0].get("sentence", "")
                questions.append({
                    "type": "capability_no_data",
                    "question": (
                        f"'{cap}' references '{obj_noun}', which isn't mapped to any "
                        f"service's owned data. Which service should own '{obj_noun}'?"
                    ),
                    "line": line_num,
                    "sentence": sentence[:120],
                    "impact": (
                        f"Determines whether '{obj_noun}' extends an existing bounded "
                        f"context or requires a new service. Unanswered, it may inflate "
                        f"service count."
                    ),
                })
                if len(questions) >= 2:
                    break

        return questions
