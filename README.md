# ShelfSense-Agent 

**Team:** Team 2  
**Team members:** Sofia Aristizabal, Miguel Fonseca, Juan Felipe Gómez, Valentina Román  
**Use case:** Inventory Counting and Traceability System Using Computer Vision

## 1. Problem / User Need
Warehouse workers often count items manually, a time-consuming process that can introduce errors. Supervisors may also lack timely, centralized information about stock levels, item movements, and stockouts. They need a faster, more reliable way to know what inventory is available and understand how it changes over time without recording every movement manually.

## 2. Product Purpose and Goal
**Purpose:** Reduce manual counting effort and inventory errors while improving visibility and traceability of warehouse items.

**Product goal:** Develop a computer-vision-assisted inventory system that identifies and counts items from visual inputs, presents results for human verification, and progressively supports inventory updates, movement history, relevant alerts, and dashboard-based supervision.

## 3. Sprint Goals
| Sprint | Goal |
|---|---|
| 1 | Refine the product backlog: split user stories into smaller stories, revise the product goal, and translate it into English. |
| 2 | Prepare training data by collecting more than 600 images of target inventory items. |
| 3 | Label and augment the collected images, train the item detection model, and test its performance. |
| 4 | Identify and count inventory items and detect faces in live video by integrating facial detection, the trained model, and a camera feed. |
| 5 | Integrate a functional API that retrieves information from the database and connects it to the dashboard. |
| 6 | Integrate the image detection model, API, backend, frontend, and login into a unified ecosystem. |
| 7 | Implement the agent and integrate its visual interface into the frontend, while updating the camera implementation to support real-time image detection. |

The sprint goals are documented in the [Sprint Goals wiki page](https://github.com/sofiaaristizabal/ShelfSense-Agent/wiki/Sprint-Goals); the Sprint 7 objective is based on the team-provided description.

## 4. User Stories Addressed in the Last Sprint

| GitHub issue | User story | Status / evidence |
|---|---|---|
| [#51](https://github.com/sofiaaristizabal/ShelfSense-Agent/issues/51) | Review Low-Confidence Results | Sprint 7 screenshot; completion/evidence to verify |
| [#52](https://github.com/sofiaaristizabal/ShelfSense-Agent/issues/52) | Mark a Detection as Incorrect | Sprint 7 screenshot; completion/evidence to verify |
| [#70](https://github.com/sofiaaristizabal/ShelfSense-Agent/issues/70) | Handle an Unrecognized Person | Sprint 7 screenshot; completion/evidence to verify |
| [#67](https://github.com/sofiaaristizabal/ShelfSense-Agent/issues/67) | Associate a Movement with a Warehouse Zone | Sprint 7 screenshot; completion/evidence to verify |
| [#66](https://github.com/sofiaaristizabal/ShelfSense-Agent/issues/66) | Record the Time of a Movement | Sprint 7 screenshot; completion/evidence to verify |
| [#63](https://github.com/sofiaaristizabal/ShelfSense-Agent/issues/63) | Detect an Item Movement | Sprint 7 screenshot; completion/evidence to verify |
| [#65](https://github.com/sofiaaristizabal/ShelfSense-Agent/issues/65) | Associate a Movement with an Inventory Item | Sprint 7 screenshot; completion/evidence to verify |
| [#64](https://github.com/sofiaaristizabal/ShelfSense-Agent/issues/64) | Determine Whether an Item Was Taken or Returned | Sprint 7 screenshot; completion/evidence to verify |
| [#54](https://github.com/sofiaaristizabal/ShelfSense-Agent/issues/54) | Correct the Detected Item Type | Sprint 7 screenshot; completion/evidence to verify |
| [#55](https://github.com/sofiaaristizabal/ShelfSense-Agent/issues/55) | Review the Final Inventory Result | Sprint 7 screenshot; completion/evidence to verify |

[Product backlog](https://github.com/users/sofiaaristizabal/projects/1) · [Repository issues](https://github.com/sofiaaristizabal/ShelfSense-Agent/issues)

## 5. Proposed Solution Architecture

The architecture diagram shows the user-facing React application, static assets and snapshots in Amazon S3, a live camera application in the warehouse, and the ShelfAgent API (FastAPI in Docker) hosted on Linode. The API uses computer vision and face-analysis libraries, communicates with OpenAI API, and reads and writes information in a Supabase PostgreSQL database. The diagram also includes the service's disk volume where the API gets the employees images for face detection and the weights for the YOLO model.

![image alt](https://github.com/sofiaaristizabal/ShelfSense-Agent/blob/ac635eb842280885ed1d2d6e17722c38a03c3166/shelfagent_with_arrow.png)

## 6. How the Agent Works

The agent receives a user request and uses an OpenAI language model to decide whether to answer directly or invoke a tool. Tool results return to the agent, which may repeat the tool-use cycle for up to five rounds as shown in the diagram. The agent interacts with the OpenAI API and a PostgreSQL database when needed and ultimately returns an answer to the user.

![image alt](https://github.com/sofiaaristizabal/ShelfSense-Agent/blob/ac635eb842280885ed1d2d6e17722c38a03c3166/agentt.png)

## 7. Progress and Scope
The project's documented sprint goals describe work on the detection model, live-camera analysis, database/API integration, dashboard, and login. Sprint 7 focuses on integrating the agent with a frontend visual interface and updating the camera implementation for real-time image detection. The implementation status and demonstration evidence should be confirmed separately from these stated goals.

The product requirements distinguish planned capabilities (such as movement tracking, employee identification, history, alerts, and support for additional visual inputs) from features that have already been demonstrated. See the [Product Requirements Document](https://github.com/sofiaaristizabal/ShelfSense-Agent/wiki/Product-Requirements-Document).

## 8. Future Work

- Validate item counting accuracy and robustness under varying lighting, camera angles, and occlusion.
- Strengthen result review and correction, and verify that inventory state remains consistent.
- Have the live camera model working on an actual security camera than can be on 24/7 and can be pointed at specific warehouse points.
- Extend and validate movement traceability, history, and stockout alerts.
- Improve end-to-end tests, operational documentation, and deployment reliability.
- Address employee consent, access controls, and privacy requirements before any facial recognition involving identifiable employees.
- Be able to use other visual sources. Have users upload inventory videos, analize smart galsses footage, amongs others. 
- Add security to the API.
- Have the warehouse administrator be able to register items trough camera registration.
- Have the warehouse administrator be able to register employees trough camera registration (like when a face is registered for the iphone face ID). 

## 9. Documentation and Supporting Materials
- [Project wiki / documentation](https://github.com/sofiaaristizabal/ShelfSense-Agent/wiki)
- [Product Requirements Document](https://github.com/sofiaaristizabal/ShelfSense-Agent/wiki/Product-Requirements-Document)
- [Sprint Goals](https://github.com/sofiaaristizabal/ShelfSense-Agent/wiki/Sprint-Goals)
- [Definition of Done](https://github.com/sofiaaristizabal/ShelfSense-Agent/wiki/Definition-of-Done-%28DoD%29)
- [Product backlog](https://github.com/users/sofiaaristizabal/projects/1)
- [Source code repository](https://github.com/sofiaaristizabal/ShelfSense-Agent)
- [GitHub issues / user stories](https://github.com/sofiaaristizabal/ShelfSense-Agent/issues)
- [Live camera code](https://github.com/sofiaaristizabal/ShelfAgent-live-camera.git)
- You can also pull the API image from docker hub here: **docker pull sofiaaristizabal/shelfagent-api-rag-api:latest**
- **Additional evidence:** Demo, test results, deployment notes, and screenshots/videos are accessible through the repository or should be linked here if separately required by the instructor.


