# Work In Progress: LLM Powered Commute Briefer

## Project Purpose
This project automates the creation of a personalized daily briefing that includes:
- Tesla vehicle data via Tesla's Fleet API
- Weather updates via a OpenWeatherMap API
- Route planning and traffic info via Google Maps API
- Generating a natural language summary using Anthropic Claude (LLM)
- Sending the briefing as an email to the user

The goal is to streamline daily commute preparation by aggregating and summarizing relevant data into a single email.

## Current Status
- Successfully implemented API calls for Tesla, Weather, and Google Maps data
- Integrated Anthropic Claude to generate the LLM-based response
- Automated sending of the generated briefing email
- Upcoming: Integrate Google Calendar functionality to personalize the briefing further based on the user's schedule

## Automation - WIP
The entire workflow will be automated using **cron jobs**, allowing the briefing to be generated and emailed at scheduled times daily without manual intervention.

## Sample Output
```
Good morning! ☀️ Here's your daily commute briefing:

**Weather & What to Wear:**
It's going to be a beautiful day! You'll enjoy clear skies in Menlo Park and just a few 
scattered clouds in South San Francisco. With temperatures ranging from the mid-50s to 
low-70s, I'd suggest layering - perhaps a light jacket or cardigan that you can easily 
remove as the day warms up. Perfect weather for your commute!

**Commute Recommendation:**
Great news - traffic looks light today! 🚗 Your 21.2-mile journey will take just 27-28 
minutes regardless of when you leave. Since there's no traffic difference, you can leave 
whenever suits your schedule best between 8:00 AM and 11:00 AM. The slightly shorter 
27-minute options start from 9:00 AM onwards if you prefer to avoid the earlier rush.

**Battery Status:**
Your Tesla is at 61% with an estimated range of 176 miles - more than enough for your 
round trip! Your commute will use about 11% of your battery (22% for the full round trip), 
leaving you with plenty of charge. No need to plug in before leaving, but you might want 
to charge tonight to start tomorrow with a fuller battery. 🔋
```
---

*This file will be updated regularly as the project progresses.*

