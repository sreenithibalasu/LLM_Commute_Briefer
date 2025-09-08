# v1.1: LLM Powered Commute Briefer

## Project Purpose
This project automates the creation of a personalized daily briefing that includes:
- Tesla vehicle data via Tesla's Fleet API
- Weather updates via a OpenWeatherMap API
- Route planning and traffic info via Google Maps API
- Generating a natural language summary using Anthropic Claude (LLM)
- Sending the briefing as an email to the user

The goal is to streamline daily commute preparation by aggregating and summarizing relevant data into a single email.

## Current Status - Updated Sept 7, 2025
- Successfully implemented API calls for Tesla, Weather, and Google Maps data
- Route information includes freeways to take and distance per route. LLM presented with options for different departure times and route options
- Integrated Anthropic Claude to generate the LLM-based response
- Automated sending of the generated briefing email
- Upcoming: Integrate Google Calendar functionality to personalize the briefing further based on the user's schedule

## Automation - Updated Sept 7, 2025
The entire workflow is automated locally using **cron jobs**, allowing the briefing to be generated and emailed at scheduled times daily without manual intervention.

## Sample Output
```
Good morning! ☀️ Here's your daily commute briefing:

**Weather & What to Wear:**
Tomorrow's looking lovely with temps reaching the low 80s! Perfect for early September. 
I'd suggest pairing a breezy short-sleeve button-up or a lightweight cotton tee with 
comfortable chinos or your favorite jeans. Since mornings will be in the low 60s,
 grab a light cardigan or denim jacket for the drive - you can leave it in the car once you arrive. 
 Slip on some breathable sneakers or loafers, and don't forget your sunglasses for that California sunshine!

**Commute Recommendation:**
I recommend leaving at 9:30 AM for the smoothest ride! You'll cruise up US-101 in just 34 minutes, 
arriving by 10:04 AM with time to spare. Traffic looks pretty manageable tomorrow - the earlier slots 
have slightly longer commute times, so sleeping in a bit actually works in your favor!

**Battery Status:**
Your Tesla has 34% charge (97 miles range) - plenty for your 27-mile commute! You'll use about 14% battery 
for the round trip, leaving you with roughly 20% by evening. I'd suggest plugging in tonight to start
tomorrow with more cushion, especially if you have any errands planned after work.
```
---

## Coming Soon
- API and set up instructions

*This file will be updated regularly as the project progresses.*

