-- ============================================================
-- ai_alarm_mappings — Full Setup Script
-- Generated from: POWER_and_DOWN_normalized.txt
-- ============================================================

-- Step 1: Add technology column (run once)
ALTER TABLE ai_alarm_mappings
  ADD COLUMN IF NOT EXISTS technology VARCHAR(20) DEFAULT '';

-- Step 2: Clear existing data
TRUNCATE TABLE ai_alarm_mappings RESTART IDENTITY;

-- Step 3: Insert all alarm mappings
INSERT INTO ai_alarm_mappings (category, vendor, technology, alarm_name) VALUES

-- ============================================================
-- POWER alarms (technology = '' — not tech-specific)
-- ============================================================

-- POWER | Huawei
('POWER', 'Huawei', '', 'Hybrid DG Failure'),
('POWER', 'Huawei', '', 'AC Main Failure'),
('POWER', 'Huawei', '', 'AC mains failure'),
('POWER', 'Huawei', '', 'AC Power Failure'),
('POWER', 'Huawei', '', 'Eltek HC Rectifier AC POWER FAILURE'),
('POWER', 'Huawei', '', 'Emerson HC Rectifier Critical alarm (AC/DC)'),
('POWER', 'Huawei', '', 'Main Power Failure'),
('POWER', 'Huawei', '', 'main power failure of Rectifier'),
('POWER', 'Huawei', '', 'AC Panel Main Power'),
('POWER', 'Huawei', '', 'No AC Input Alarm'),
('POWER', 'Huawei', '', 'No DC Input Alarm'),
('POWER', 'Huawei', '', 'Power shelter Rectifier Ac main failure'),
('POWER', 'Huawei', '', 'Rectifier failure'),
('POWER', 'Huawei', '', 'Solar Major Batteries Level'),
('POWER', 'Huawei', '', 'Rectifier Failure of Second Rectifier'),
('POWER', 'Huawei', '', 'Main Power Failure of Second Rectifier'),
('POWER', 'Huawei', '', 'Hierarchical Power Supply Alarm'),
('POWER', 'Huawei', '', 'EMERSON AC POWER FAILURE'),
('POWER', 'Huawei', '', 'ALX0009  main power failure'),
('POWER', 'Huawei', '', 'PSU shutdown alarm'),
('POWER', 'Huawei', '', 'Mains Input Out of Range'),

-- POWER | Nokia
('POWER', 'Nokia', '', 'Huawei OD HC Rectifier AC Failure  alarm'),
('POWER', 'Nokia', '', 'Ericsson OD HC Rectifier  AC'),
('POWER', 'Nokia', '', 'Vertiv HC OD AC Rectifier Failure Alarm'),
('POWER', 'Nokia', '', 'Vertiv HC OD DC Rectifier Failure Alarm'),
('POWER', 'Nokia', '', 'Vertiv OD HC rectifier module failure'),
('POWER', 'Nokia', '', 'vertiv AC power rectefire alarm'),
('POWER', 'Nokia', '', 'vertiv DC rectefire alarm'),
('POWER', 'Nokia', '', 'Gen Running'),
('POWER', 'Nokia', '', 'Rectifier minor alarm'),
('POWER', 'Nokia', '', 'ELETIC rectfauirminor alarm'),
('POWER', 'Nokia', '', 'ELEtec OD HC Rectifier Module alarm'),
('POWER', 'Nokia', '', 'Vertiv OD HC Rectifier Main AC Failure'),
('POWER', 'Nokia', '', 'Ericsson OD HC Rectifier Major alarm'),
('POWER', 'Nokia', '', 'OD HC Rectefire AC alarm'),
('POWER', 'Nokia', '', 'Vertiv OD HC rectifier AC failure'),
('POWER', 'Nokia', '', 'ELTECK OD HC Rectifier Main AC Failure'),
('POWER', 'Nokia', '', 'rectifier AC failure'),
('POWER', 'Nokia', '', 'Emerson OD HC Rectifier Critical alarm'),
('POWER', 'Nokia', '', 'ZTE OD HC Rectifier AC Failure'),
('POWER', 'Nokia', '', 'Huawei OD HC Rectifier Failure alarm (one PSU Or More)'),
('POWER', 'Nokia', '', 'main power failure of Rectifier'),
('POWER', 'Nokia', '', 'Huawei OD HC Rectifier AC Failure'),
('POWER', 'Nokia', '', 'Ericsson OD HC Rectifier Minor alarm'),
('POWER', 'Nokia', '', 'Ericsson OD HC rectifier AC Failure'),
('POWER', 'Nokia', '', 'Rectifier failure'),

-- POWER | ZTE
('POWER', 'ZTE', '', 'AC power-cut alarm'),
('POWER', 'ZTE', '', 'Battery alarm'),
('POWER', 'ZTE', '', 'PSU alarm'),
('POWER', 'ZTE', '', 'Rectifier module alarm'),
('POWER', 'ZTE', '', 'The input voltage is abnormal'),
('POWER', 'ZTE', '', 'Generator running'),
('POWER', 'ZTE', '', 'Input power-off'),
('POWER', 'ZTE', '', 'AC power interruption alarm'),
('POWER', 'ZTE', '', 'power AC power OFF'),

-- ============================================================
-- SITE_DOWN alarms (technology-specific)
-- ============================================================

-- SITE_DOWN | 2G
('SITE_DOWN', 'Huawei', '2G', 'OML Fault'),
('SITE_DOWN', 'Huawei', '2G', 'CSL fault'),
('SITE_DOWN', 'Nokia',  '2G', 'BTS O&M link failure'),
('SITE_DOWN', 'ZTE',    '2G', 'Link between OMM and NE broken'),

-- SITE_DOWN | 3G
('SITE_DOWN', 'Huawei', '3G', 'NodeB Unavailable'),
('SITE_DOWN', 'Nokia',  '3G', 'WCDMA Base station out of use'),
('SITE_DOWN', 'ZTE',    '3G', 'NodeB is out of service'),

-- SITE_DOWN | 4G
('SITE_DOWN', 'Huawei', '4G', 'Enodeb Out of service'),
('SITE_DOWN', 'Huawei', '4G', 'Ne is disconnected'),
('SITE_DOWN', 'Nokia',  '4G', 'NE3SWS agent not responding to requests'),
('SITE_DOWN', 'ZTE',    '4G', 'eNodeB is out of service'),

-- SITE_DOWN | 5G
('SITE_DOWN', 'Huawei', '5G', 'gNodeB Out of Service'),
('SITE_DOWN', 'Huawei', '5G', 'Ne is disconnected'),
('SITE_DOWN', 'Nokia',  '5G', 'NE3SWS agent not responding to requests'),
('SITE_DOWN', 'ZTE',    '5G', 'gNodeB DU out-of-service'),

-- ============================================================
-- CELL_DOWN alarms (technology-specific)
-- ============================================================

-- CELL_DOWN | 2G
('CELL_DOWN', 'Huawei', '2G', 'GSM cell out of service'),
('CELL_DOWN', 'Nokia',  '2G', 'BCCH missing'),
('CELL_DOWN', 'ZTE',    '2G', 'Cell interruption alarm'),

-- CELL_DOWN | 3G
('CELL_DOWN', 'Huawei', '3G', 'UMTS Cell Unavailable'),
('CELL_DOWN', 'Nokia',  '3G', 'WCDMA cell out of use'),
('CELL_DOWN', 'ZTE',    '3G', 'Cell is out of service'),

-- CELL_DOWN | 4G
('CELL_DOWN', 'Huawei', '4G', 'Cell unavailable'),
('CELL_DOWN', 'Nokia',  '4G', 'Base station Service problem'),
('CELL_DOWN', 'Nokia',  '4G', 'Cell Service Problem'),
('CELL_DOWN', 'ZTE',    '4G', 'LTE cell outage'),

-- CELL_DOWN | 5G
('CELL_DOWN', 'Huawei', '5G', 'NR DU Cell TRP Unavailable'),
('CELL_DOWN', 'Huawei', '5G', 'NR DU Cell Unavailable'),
('CELL_DOWN', 'Huawei', '5G', 'NR Cell Unavailable'),
('CELL_DOWN', 'Nokia',  '5G', 'Base station Service problem'),
('CELL_DOWN', 'Nokia',  '5G', 'Cell Service Problem'),
('CELL_DOWN', 'ZTE',    '5G', 'DU cell out-of-service');

-- ============================================================
-- Verify
-- ============================================================
SELECT category, vendor, technology, COUNT(*) as count
FROM ai_alarm_mappings
GROUP BY category, vendor, technology
ORDER BY category, vendor, technology;
