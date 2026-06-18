from test_case_generator.prompt_quality import assess, assess_instructions


def test_instructions_weak_lists_missing_dimensions():
    s = assess_instructions("Help the user.")
    assert s.score < 65
    assert s.example                                  # offers an instructions template
    assert any("permission" in x.lower() or "tool" in x.lower() or "refuse" in x.lower()
               for x in s.suggestions)


def test_instructions_strong_scores_high():
    instr = (
        "You are a Jira support agent whose goal is to help triage tickets. "
        "Tools you may use: search_issues, get_issue, update_issue; use update_issue only after confirming. "
        "You must not delete issues or act outside the user's project; only authorized actions are allowed. "
        "Refuse unauthorized or out-of-scope requests. Use the Jira API as the source of truth and cite issue keys. "
        "Respond in concise bullet points. If information is missing, ask rather than guess."
    )
    s = assess_instructions(instr)
    assert s.score >= 85 and s.suggestions == []


def test_empty_prompt_scores_zero():
    s = assess("   ")
    assert s.score == 0 and s.suggestions


def test_weak_prompt_gets_low_score_and_capped_suggestions():
    s = assess("do it")
    assert s.score < 45
    assert len(s.suggestions) <= 3            # never naggy


def test_weak_prompt_gets_example_shape_with_the_task():
    s = assess("summarize this document")
    assert s.example                                  # an example shape is offered
    assert "Task: summarize this document" in s.example
    assert "Output:" in s.example                     # fills a missing dimension


def test_strong_prompt_scores_high_and_no_suggestions():
    prompt = (
        "You are a senior copy editor. Rewrite the paragraph below to be concise "
        "and formal, in at most 3 sentences. Return the result as JSON with a "
        "'text' field. For example: {\"text\": \"...\"}. Paragraph: ..."
    )
    s = assess(prompt)
    assert s.score >= 85
    assert s.suggestions == []                # already strong -> stop, don't lecture
    assert s.example == ""                    # no example needed
    assert s.level == "Strong"


def test_suggestions_target_missing_dimensions():
    # has a clear task + context, but no output format / constraints / example
    s = assess("You are a tutor. Explain how recursion works to a beginner.")
    assert 45 <= s.score < 85
    assert any("output" in x.lower() or "constraint" in x.lower() or "example" in x.lower()
               for x in s.suggestions)
