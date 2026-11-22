# Project Proposal and Feasibility Study

## Project Proposal
**Title:** EcoQuest — Gamified Environmental Education Platform for Schools and Colleges
**Tagline:** Learn. Play. Act. Make an Impact.

**Problem.** Environmental education is often delivered in a traditional, theoretical way that does not engage students,
so awareness of sustainability and eco-friendly practices remains limited.

**Proposed solution.** A web platform where students learn environmental topics through short lessons, practise with
quizzes, complete real-life eco challenges, and earn XP, levels, badges and streaks. Teachers use it as a classroom-support
tool; administrators manage users and content.

**Objectives**
1. Make environmental learning interactive and engaging through gamification.
2. Provide structured content across six environmental topics.
3. Give students measurable progress information.
4. Give teachers tools to create quizzes/challenges and view class participation.
5. Build the system with simple, well-understood technologies suited to a B.Tech project.

**Expected impact (stated academically).** The platform is designed to improve engagement, awareness and participation in
environmental education. Its effectiveness has **not been evaluated with real users**; any such evaluation is future work.

**Methodology.** Agile incremental development in seven increments:
1. Requirements and architecture · 2. Database and authentication · 3. Student learning · 4. Quiz and gamification ·
5. Challenges · 6. Teacher and admin modules · 7. Testing and deployment preparation.

## Existing systems
Typical alternatives are static websites/textbooks and general quiz or e-learning platforms. They are usually not
focused on environmental topics, do not combine lessons, quizzes and real-world habit challenges, and offer teachers little
class-level visibility. (This is a general characterisation, not a survey of specific products; no market study was performed.)

## Feasibility Study
| Aspect | Assessment |
|---|---|
| **Technical** | Feasible: Flask, MySQL, HTML/CSS/JS are mature, well documented and part of the student's prior learning. The whole system was built and run on a single laptop. |
| **Economic** | Feasible: all software used is free/open source (Python, Flask, MySQL Community, Chart.js, VS Code, Git). Cloud hosting for a demo can use a free or low-cost tier (subject to the provider's current plans — not verified). |
| **Operational** | Feasible: the interface is simple; a short user manual is provided; roles map to real classroom roles. |
| **Schedule** | Feasible within a semester using seven short increments. |
| **Legal/ethical** | Only minimal personal data (name, email, optional class) is stored; passwords are hashed. A real deployment with minors would need a privacy policy and parental-consent process (out of scope). |
| **Risks** | Limited content volume (mitigated by admin content tools); no email verification/password reset; dependence on CDN for charts. |

## Risk management summary
| Risk | Mitigation |
|---|---|
| Scope creep | Fixed core feature list; optional features only after core completion |
| Data loss | Foreign keys + transactions; seed script can rebuild demo data |
| Security mistakes | Parameterised SQL, hashing, CSRF tokens, role checks, tests |
| Over-complex technology | Restricted to curriculum technologies |
