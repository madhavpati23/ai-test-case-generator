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


def test_weak_prompt_gets_a_concrete_rewrite():
    s = assess("summarize this document")
    assert s.example                                  # a rewrite is offered
    assert "<" not in s.example                        # concrete, no <slot> placeholders
    assert "summarize this document" in s.example.lower()   # keeps the user's task
    assert "You are" in s.example                      # adds a sensible role


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


def test_mid_prompt_has_capped_suggestions_and_a_rewrite():
    s = assess("You are a tutor. Explain how recursion works to a beginner.")
    assert s.score < 85
    assert 1 <= len(s.suggestions) <= 3        # gives pointers, never naggy
    assert s.example                            # offers a concrete rewrite


def test_audience_and_purpose_is_scored():
    # a prompt naming audience + purpose should get credit for that dimension
    s = assess("Write a status update for my manager so that they understand the delay.")
    assert "audience & purpose" in s.present and s.present["audience & purpose"]
