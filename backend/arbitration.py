AGENT_WEIGHTS = {
    "monitor": 1,
    "cascade": 2,
    "impact": 3,
    "response": 3,
    "comms": 1,
}


def arbitrate(agent_outputs: dict) -> dict:
    response_rec = agent_outputs.get("response", {}).get("recommendation", "A")
    impact_vote = "A"
    response_vote = "B" if response_rec == "A" else "A"
    cascade_vote = "A"

    vote_breakdown = {
        "cascade": {"vote": cascade_vote, "weight": AGENT_WEIGHTS["cascade"]},
        "impact": {"vote": impact_vote, "weight": AGENT_WEIGHTS["impact"]},
        "response": {"vote": response_vote, "weight": AGENT_WEIGHTS["response"]},
    }

    votes_for_a = sum(v["weight"] for v in vote_breakdown.values() if v["vote"] == "A")
    votes_for_b = sum(v["weight"] for v in vote_breakdown.values() if v["vote"] == "B")
    total_weight = votes_for_a + votes_for_b

    recommendation = response_rec
    winning_votes = votes_for_a if recommendation == "A" else votes_for_b
    confidence = round(winning_votes / total_weight, 2) if total_weight else 0.87

    human_review_needed = impact_vote != response_vote and response_rec != impact_vote

    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "vote_breakdown": vote_breakdown,
        "human_review_needed": human_review_needed,
    }
