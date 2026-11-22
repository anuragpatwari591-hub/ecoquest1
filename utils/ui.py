"""Small UI helper: turn the result of record_activity() into flash messages (XP, level up, badges)."""
from flask import flash


def flash_rewards(result, headline):
    """Show XP, bonuses, level-up and badge notifications after an activity."""
    flash(f"{headline} +{result['xp']} XP", "success")
    if result.get("bonus"):
        flash(f"🔥 Streak bonus! +{result['bonus']} XP included", "success")
    if result.get("quest_bonus"):
        flash(f"🎯 All daily quests complete! +{result['quest_bonus']} XP bonus included", "success")
    if result.get("level_up"):
        flash(f"🎉 LEVEL UP! You reached Level {result['level_up']} — your Eco City is getting cleaner!", "levelup")
    for badge in result["badges"]:
        flash(f"Badge unlocked: {badge['icon']} {badge['name']}", "badge")
