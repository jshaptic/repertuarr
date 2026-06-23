#!/usr/bin/env python3
"""Verify the recommendation prompt includes user context"""
import chevron
import os

# Simulate loading prompt
def load_prompt(name, **kwargs):
    current_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(current_dir, 'bots', 'media_bot', 'prompts', f'{name}.mustache')
    with open(prompt_path, 'r') as f:
        return chevron.render(f, kwargs)

print("=== Testing Recommendation Prompt with User Context ===\n")

# Test 1: With full user context
print("Test 1: With user name and description")
print("-" * 60)
prompt1 = load_prompt("recommendation", 
                     query="sci-fi movies", 
                     user_name="Eugene",
                     user_description="Enjoys sci-fi movies, psychological thrillers, and indie films. Prefers thought-provoking content over action blockbusters.")
print(prompt1)
print("\n")

# Test 2: Without user context (anonymous/new user)
print("Test 2: Without user context")
print("-" * 60)
prompt2 = load_prompt("recommendation", 
                     query="sci-fi movies",
                     user_name="",
                     user_description="")
print(prompt2)
print("\n")

# Test 3: With name but no description
print("Test 3: With name but no description")
print("-" * 60)
prompt3 = load_prompt("recommendation", 
                     query="horror movies",
                     user_name="Eugene",
                     user_description="")
print(prompt3)

print("\n\n✅ Prompt template verification complete!")
