# Seshat AI – OULAD Dataset README / Data Dictionary

## Dataset Used

**Open University Learning Analytics Dataset (OULAD)**
This dataset contains anonymized student interaction, assessment, demographic, and learning behavior data collected from online learning environments.

The dataset is used for:

* Student performance prediction
* Dropout risk analysis
* Learning behavior analysis
* Tutorial recommendation systems
* Educational analytics dashboards


# Dataset Overview

The dataset consists of the following CSV files:

| File Name               | Description                                           |
| ----------------------- | ----------------------------------------------------- |
| assessments.csv         | Information about assessments/exams                   |
| studentAssessment.csv   | Student assessment scores                             |
| courses.csv             | Course/module information                             |
| studentInfo.csv         | Student demographic and academic details              |
| studentRegistration.csv | Student registration and withdrawal information       |
| studentVle.csv          | Student interaction with virtual learning environment |
| vle.csv                 | Learning material/activity metadata                   |

---

# 1. assessments.csv

## Purpose

Contains information about assessments conducted for each course module.



## Columns Description

| Column Name       | Description                              |
| ----------------- | ---------------------------------------- |
| code_module       | Unique course/module identifier          |
| code_presentation | Semester/presentation identifier         |
| id_assessment     | Unique assessment ID                     |
| assessment_type   | Type of assessment (TMA, CMA, Exam)      |
| date              | Assessment submission deadline (in days) |
| weight            | Weightage of assessment in final score   |

## Assessment Types

| Type | Meaning                    |
| ---- | -------------------------- |
| TMA  | Tutor Marked Assignment    |
| CMA  | Computer Marked Assessment |
| Exam | Final Examination          |

## Possible Use Cases

* Assessment analytics
* Score prediction
* Student performance evaluation

---

# 2. studentAssessment.csv

## Purpose

Contains student scores obtained in assessments.


## Columns Description

| Column Name    | Description                       |
| -------------- | --------------------------------- |
| id_assessment  | Assessment ID                     |
| id_student     | Unique student ID                 |
| date_submitted | Submission date                   |
| is_banked      | Indicates reused assessment score |
| score          | Student assessment score          |

## Possible Use Cases

* Performance prediction
* Score analysis
* Weak student identification

---

# 3. courses.csv

## Purpose

Contains course/module details.


## Columns Description

| Column Name                | Description                |
| -------------------------- | -------------------------- |
| code_module                | Unique module/course ID    |
| code_presentation          | Course presentation period |
| module_presentation_length | Course duration in days    |

## Possible Use Cases

* Course analytics
* Learning duration analysis

---

# 4. studentInfo.csv

## Purpose

Contains demographic and academic information of students.


## Columns Description

| Column Name          | Description                       |
| -------------------- | --------------------------------- |
| code_module          | Module/course ID                  |
| code_presentation    | Presentation period               |
| id_student           | Unique student ID                 |
| gender               | Student gender                    |
| region               | Geographic region                 |
| highest_education    | Highest educational qualification |
| imd_band             | Socioeconomic deprivation band    |
| age_band             | Student age category              |
| num_of_prev_attempts | Number of previous attempts       |
| studied_credits      | Total credits studied             |
| disability           | Disability status                 |
| final_result         | Final course outcome              |

## Final Result Categories

| Result      | Meaning                |
| ----------- | ---------------------- |
| Pass        | Successfully completed |
| Fail        | Failed course          |
| Distinction | High performance       |
| Withdrawn   | Student dropped out    |

## Possible Use Cases

* Student profiling
* Dropout prediction
* Performance prediction
* Educational analytics

---

# 5. studentRegistration.csv

## Purpose

Contains student registration and withdrawal information.


## Columns Description

| Column Name         | Description         |
| ------------------- | ------------------- |
| code_module         | Module ID           |
| code_presentation   | Presentation period |
| id_student          | Student ID          |
| date_registration   | Registration date   |
| date_unregistration | Withdrawal date     |

## Notes

* Empty `date_unregistration` indicates active/completed students.
* Non-empty value indicates student withdrawal/dropout.

## Possible Use Cases

* Dropout analysis
* Student retention analysis

---

# 6. studentVle.csv

## Purpose

Contains student interaction logs with learning resources in the Virtual Learning Environment (VLE).


## Columns Description

| Column Name       | Description                   |
| ----------------- | ----------------------------- |
| code_module       | Module ID                     |
| code_presentation | Presentation period           |
| id_student        | Student ID                    |
| id_site           | Learning resource/site ID     |
| date              | Interaction date              |
| sum_click         | Number of clicks/interactions |

## Important Feature

### sum_click

Represents student engagement/activity level.

Higher clicks generally indicate:

* Better engagement
* Active participation
* Higher learning interaction

## Possible Use Cases

* Engagement analysis
* Recommendation systems
* Learning behavior analysis
* Dropout prediction

---

# 7. vle.csv

## Purpose

Contains metadata about learning materials/resources.

## Columns Description

| Column Name       | Description                 |
| ----------------- | --------------------------- |
| id_site           | Unique learning resource ID |
| code_module       | Module ID                   |
| code_presentation | Presentation period         |
| activity_type     | Type of learning activity   |
| week_from         | Starting week availability  |
| week_to           | Ending week availability    |

## Activity Types

| Activity Type | Meaning                    |
| ------------- | -------------------------- |
| resource      | Learning resource/document |
| oucontent     | Open University content    |
| homepage      | Homepage interaction       |
| url           | External link/resource     |

## Possible Use Cases

* Tutorial recommendation
* Resource analytics
* Content popularity analysis