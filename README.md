# Brandeis Transportation Coordinator Dashboard

## 📖 Overview
This project provides a **Python Dash** dashboard designed to help the Brandeis Transportation office analyze ridership trends across their campus shuttle routes. By visualizing historical and real-time ridership data, this tool supports data-driven decisions such as:
- Adjusting vehicle capacity
- Modifying service hours
- Identifying under- or over-utilized stops

Additionally, the project required (but not included here) scripts for **data cleaning** and reformatting, tailored to the vendor's data inconsistencies, ensuring that the dashboard receives well-structured, accurate inputs.

---

## Getting Started

### Prerequisites
Before using this dashboard, ensure you have the following installed:
- **Python** (v3.10+ recommended)

---

## Directory Structure
```
Transportation-Coordinator-Dashboard/
│-- data/ # Raw and processed datasets
│-- docs/ # Documentation and assets for the README
│-- pages/ # Application pages (Dash)
│-- static/ # Static assets (CSS, JS, images)
│-- utils/ # Utility scripts for data cleaning and processing
│-- run.py # Entry point to launch the dashboard
│-- README.md # Project documentation
```
---

## Dashboard Features

### Time-Based Ridership Analysis
The **Time** page allows you to explore ridership across multiple granularities. Available visualizations include:
- Ridership by **semester** and **year**
- Ridership by **month**, **week**, and **date**
- Ridership in **30-min intervals**
- Ridership by **scheduled time** at any selected stop

![Ridership by Time](assets/RidershipSummaryWaltham.gif)

By default, the dashboard displays ridership trends for the entire date range defined by the filters at the top of the page.

### Stop Utilization
The **Stop Utilization** page highlights which stops are most and least frequented. It includes:
- Top and bottom **10 stops** by ridership (adjustable in code)
- Daily ridership breakdowns for each day of the week across these top and bottom stops

![Ridership by Stop](assets/RidershipByStop.gif)

---

## Future Improvements
This project is under active development. Upcoming enhancements include:
- Redesigned and more visually appealing **home page**
- Enhanced **Ridership Summary** page with at-a-glance overview
- **Drag-and-drop data ingestion** with automated preprocessing tailored to the company’s specific data format

---

## Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/alexstvn/Transportation-Coordinator-Dashboard.git
   cd Transportation-Coordinator-Dashboard
   ```
2. Install dependencies
    ```
    pip install -r requirements.txt
    ```
3. Run the application.
    ```
    python run.py
    ```
---

## Contact
For questions or feedback, please feel free to reach out to [me](https://github.com/alexstvn)!
