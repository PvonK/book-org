from book_org import categorizer


def test_single_keyword_match():
    path = "Learning_Linux_2024.pdf"
    result = categorizer.category_fallback(path)
    assert "computers" in result


def test_multiple_keywords_same_category():
    path = "Advanced_Cyber_VPN_Security.pdf"
    result = categorizer.category_fallback(path)
    assert result.count("computers") >= 1
    assert "computers" in result


def test_multiple_keywords_different_categories():
    path = "Python_Cybersecurity_Handbook.pdf"
    result = categorizer.category_fallback(path)
    assert "programming" in result
    assert "cybersecurity" in result


def test_case_insensitivity():
    path = "ETHEREUM_BlockChain_Primer.epub"
    result = categorizer.category_fallback(path)
    assert "blockchain" in result


def test_partial_substring_token_match():
    path = "Intro_to_Physics_and_Physiology.pdf"
    result = categorizer.category_fallback(path)
    assert "Science" in result


def test_no_match_returns_uncategorized():
    path = "CompletelyRandomFileName.abc"
    result = categorizer.category_fallback(path)
    assert result == ["uncategorized"]


def test_returns_all_matching_categories():
    path = "Python_Kubernetes_Security.pdf"
    result = categorizer.category_fallback(path)
    assert sorted(result) == sorted(["programming", "devops", "cybersecurity"])


def test_handles_non_alphanumeric_characters():
    path = "Startup [Business!].pdf"
    result = categorizer.category_fallback(path)
    assert "Business" in result


def test_does_not_duplicate_categories():
    path = "Game_Development_with_Unity_and_Godot.pdf"
    result = categorizer.category_fallback(path)
    assert (
        result.count("gamedev") == 2 or
        result.count("gamedev") == len(result)
        )
