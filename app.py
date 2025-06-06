import streamlit as st
import json
from docx_parser import extract_articles_from_docx
from regex_utils import to_split_regex
from collections import defaultdict

MODES = ["Fewshot examples", "Fewshots rejected", "Transitions only", "Transitions only rejected", "Fewshot examples (JSONL)", "Fewshots finetuning rejected"]

st.title("📄 Structured Transition Triplets Extractor Prototype by Ayman")

uploaded_file = st.file_uploader("Upload a Word (.docx) file", type=["docx"])

if uploaded_file:
    try:
        raw_articles = extract_articles_from_docx(uploaded_file.read())

        st.success(f"Found {len(raw_articles)} article(s)")

        # for i, article in enumerate(raw_articles, 1):
        #     st.markdown(f"### ✏️ Article {i}")
        #     st.text_area(label="", value=article, height=200)

        fewshot_examples = []
        used_transitions = defaultdict(int)
        transitions_rejected = []
        transitions_only = []
        transitions_used_more_than_once = []
        total_transitions_count = 0
        for article in raw_articles:
            lines = article.splitlines()
            try:
                transitions_index = (
                    lines.index("Transitions :") if "Transitions :" in lines
                    else lines.index("Transitions") if "Transitions" in lines
                    else -1
                )
            except ValueError:
                transitions_index = -1

            transitions = lines[transitions_index + 1:] if transitions_index != -1 else []
            large_para = lines[transitions_index - 1] if transitions_index > 0 else None

            if not large_para:
                raise ValueError("Large paragraph not found")

            for transition in transitions:
                total_transitions_count += 1
                if transition not in transitions_only:
                    transitions_only.append(transition)

                pattern = to_split_regex(transition)

                if not pattern.search(large_para):
                    print(lines[0])
                    print("⚠️ No match for transition:", transition)
                    print("Large paragraph:", large_para)
                    print("Regex:", pattern)
                    continue

                used_transitions[transition] += 1
                if used_transitions[transition] > 1:
                    if transition not in transitions_used_more_than_once:
                        transitions_used_more_than_once.append(transition)
                if used_transitions[transition] > 3:
                    if transition not in transitions_rejected:
                        transitions_rejected.append(transition)
                    continue

                split_result = pattern.split(large_para, maxsplit=1)
                if len(split_result) != 2:
                    print(f"⚠️ Could not split on: {transition}")
                    continue

                paragraph_a, paragraph_b = split_result
                fewshot_examples.append({
                    "paragraph_a": paragraph_a.strip(),
                    "transition": transition,
                    "paragraph_b": paragraph_b.strip(),
                })

        st.success(f"Found {total_transitions_count} transition(s)")
        selected_mode = st.selectbox("Select processing mode", list(MODES))

        if selected_mode == "Fewshot examples":
            st.caption("Extracted triplets with paragraph_a, transition, and paragraph_b (cap each transition at 3 uses)")
            st.success(f"Found {len(fewshot_examples)} fewshot examples")
            json_data = json.dumps(fewshot_examples, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_data,
                file_name="fewshot_examples.json",
                mime="application/json"
            )
        elif selected_mode == "Fewshots rejected":
            st.caption("List of transitions used more than 3 times with actual count")
            st.success(f"Found {len(transitions_rejected)} fewshots rejected")
            st.download_button(
                label="📥 Download as text",
                data="\n".join([f"{transition} - {used_transitions[transition]}" for transition in transitions_rejected]),
                file_name="fewshots_rejected.txt",
                mime="text/plain"
            )
        elif selected_mode == "Transitions only":
            st.caption("Unique transitions, one per line, taken from the listed transitions under each article")
            st.success(f"Found {len(transitions_only)} unique transitions")
            st.download_button(
                label="📥 Download as text",
                data="\n".join(transitions_only),
                file_name="transitions_only.txt",
                mime="text/plain"
            )
        elif selected_mode == "Transitions only rejected":
            st.caption("Transitions used more than once, with actual count")
            st.success(f"Found {len(transitions_used_more_than_once)} transitions used more than once")
            st.download_button(
                label="📥 Download as text",
                data="\n".join([f"{transition} - {used_transitions[transition]}" for transition in transitions_used_more_than_once]),
                file_name="transitions_only_rejected.txt",
                mime="text/plain"
            )
        elif selected_mode == "Fewshot examples (JSONL)":
            st.caption("JSONL format for fine-tuning, using structured messages with role:system, role:user, and role:assistant")
            st.success(f"Found {len(fewshot_examples)} fewshot examples")
            st.text("Download is not yet implemented")
        elif selected_mode == "Fewshots finetuning rejected":
            st.caption("List of transitions used more than 3 times in the fine-tuning format")
            st.success(f"Found {len(transitions_rejected)} fewshots finetuning rejected")
            st.download_button(
                label="📥 Download as text",
                data="\n".join([f"{transition} - {used_transitions[transition]}" for transition in transitions_rejected]),
                file_name="fewshots-fineTuning_rejected.txt",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"Error: {e}")
