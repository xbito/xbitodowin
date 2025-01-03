import random

motivational_phrases = [
    "Believe in yourself, anything is possible.",
    "Don't watch the clock; do what it does - keep going.",
    "Success is not final, failure is not fatal: it's the courage to continue that counts.",
    "You are stronger than you think, braver than you feel, and smarter than you know.",
    "Every step forward is a step closer to your dream.",
    "Don't give up - you never know what tomorrow will bring.",
    "The only way to do great work is to love what you do.",
    "You are capable of amazing things, just trust yourself.",
    "Push through the hard times; they're preparing you for better days.",
    "Every accomplishment starts with a single step.",
    "You are one decision away from a totally different life.",
    "Don't be afraid to take risks - that's where the magic happens.",
    "The biggest risk is not taking any risk at all.",
    "Your only limit is your own mind.",
    "Keep going, even when you don't feel like it.",
    "You are stronger than your excuses.",
    "Believe in yourself and you'll be unstoppable.",
    "Don't compare yourself to others; compare yourself to who you were yesterday.",
    "The best way to get started is to quit talking and begin doing.",
    "Success is a journey, not a destination.",
    "You are capable of achieving anything you set your mind to.",
    "Keep pushing forward, even when it feels like nothing is happening.",
    "Your thoughts have the power to shape your reality.",
    "You are one step away from changing everything.",
    "The biggest mistake is giving up on your dreams.",
    "Take control of your life and make today count.",
    "Don't let fear hold you back - face it head-on.",
    "Success is not about being perfect; it's about being persistent.",
    "You are capable of amazing things, just trust yourself.",
    "Keep going, even when it feels like giving up is the easy way out.",
    "Your mindset determines your outcome.",
    "Don't be afraid to ask for help - that's what friends are for.",
    "Believe in yourself and you'll be unstoppable.",
    "The only thing holding you back is your own self-doubt.",
    "Take action today; don't put it off until tomorrow.",
    "You are stronger than you think, braver than you feel, and smarter than you know.",
    "Keep pushing forward, even when the road gets rough.",
    "Believe in yourself and your abilities.",
    "Take control of your life and make today count.",
    "The biggest mistake is giving up on your dreams.",
    "Success is not about being perfect; it's about being persistent.",
    "Your thoughts have the power to shape your reality.",
    "You are capable of achieving anything you set your mind to.",
    "Keep going, even when it feels like nothing is happening.",
    "The biggest risk is not taking any risk at all.",
    "Don't compare yourself to others; compare yourself to who you were yesterday.",
    "Success is a journey, not a destination.",
    "You are one step away from changing everything.",
    "Believe in yourself and your abilities.",
    "Take control of your life and make today count.",
    "The biggest mistake is giving up on your dreams.",
    "Keep pushing forward, even when the road gets rough.",
    "Your mindset determines your outcome.",
    "Don't be afraid to take risks - that's where the magic happens.",
    "You are capable of amazing things, just trust yourself.",
    "Keep going, even when it feels like giving up is the easy way out.",
    "The only thing holding you back is your own self-doubt.",
    "Take action today; don't put it off until tomorrow.",
    "Don't let fear hold you back - face it head-on.",
    "You are stronger than you think, braver than you feel, and smarter than you know.",
    "Keep pushing forward, even when the road gets rough.",
    "Believe in yourself and your abilities.",
    "Take control of your life and make today count.",
    "The biggest mistake is giving up on your dreams.",
    "Success is not about being perfect; it's about being persistent.",
    "Your thoughts have the power to shape your reality.",
    "You are capable of achieving anything you set your mind to.",
    "Keep going, even when it feels like nothing is happening.",
    "The biggest risk is not taking any risk at all.",
    "Don't compare yourself to others; compare yourself to who you were yesterday.",
    "Success is a journey, not a destination.",
    "You are one step away from changing everything.",
    "Believe in yourself and your abilities.",
    "Take control of your life and make today count.",
    "The biggest mistake is giving up on your dreams.",
    "Keep pushing forward, even when the road gets rough.",
    "Your mindset determines your outcome.",
    "Don't be afraid to ask for help - that's what friends are for.",
    "You are stronger than you think, braver than you feel, and smarter than you know.",
    "Keep going, even when it feels like giving up is the easy way out.",
    "The only thing holding you back is your own self-doubt.",
    "Take action today; don't put it off until tomorrow.",
    "You got this!",
]


def get_motivational_phrase():
    return random.choice(motivational_phrases)
