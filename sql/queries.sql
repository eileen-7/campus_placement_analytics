-- SQL Queries for Campus Placement Analytics
-- These queries analyze student placement rates, average packages, top hiring companies, and gaps.

-- 1. PLACEMENT RATE BY DEPARTMENT
-- This query calculates the percentage of students in each department who got and accepted an offer.
SELECT 
    s.department,
    COUNT(DISTINCT s.student_id) AS total_students,
    COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN s.student_id END) AS placed_students,
    ROUND(
        (COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN s.student_id END)::NUMERIC / COUNT(DISTINCT s.student_id) * 100), 
        2
    ) AS placement_rate_percent
FROM students s
LEFT JOIN offers o ON s.student_id = o.student_id
GROUP BY s.department
ORDER BY placement_rate_percent DESC;


-- 2. AVERAGE PACKAGE (SALARY) TRENDS BY DEPARTMENT
-- This query finds the average, maximum, and minimum package (in LPA) accepted by students in each department.
SELECT 
    s.department,
    ROUND(AVG(o.package_lpa), 2) AS avg_package_lpa,
    MAX(o.package_lpa) AS max_package_lpa,
    MIN(o.package_lpa) AS min_package_lpa
FROM students s
JOIN offers o ON s.student_id = o.student_id
WHERE o.accepted = TRUE
GROUP BY s.department
ORDER BY avg_package_lpa DESC;


-- 3. TOP HIRING COMPANIES
-- This query finds the companies that made the most accepted job offers.
SELECT 
    c.name AS company_name,
    c.industry,
    COUNT(o.offer_id) AS total_offers_made,
    COUNT(CASE WHEN o.accepted = TRUE THEN 1 END) AS offers_accepted
FROM companies c
JOIN offers o ON c.company_id = o.company_id
GROUP BY c.company_id, c.name, c.industry
ORDER BY offers_accepted DESC, total_offers_made DESC
LIMIT 5;


-- 4. APPLIED VS PLACED GAP (STUDENT PLACEMENT FUNNEL)
-- This query shows the gap between the total students, those who actively applied, and those who got placed in each department.
SELECT 
    s.department,
    COUNT(DISTINCT s.student_id) AS total_students,
    COUNT(DISTINCT a.student_id) AS students_who_applied,
    COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN o.student_id END) AS students_placed,
    COUNT(DISTINCT s.student_id) - COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN o.student_id END) AS gap_unplaced
FROM students s
LEFT JOIN applications a ON s.student_id = a.student_id
LEFT JOIN offers o ON s.student_id = o.student_id AND o.accepted = TRUE
GROUP BY s.department
ORDER BY total_students DESC;
