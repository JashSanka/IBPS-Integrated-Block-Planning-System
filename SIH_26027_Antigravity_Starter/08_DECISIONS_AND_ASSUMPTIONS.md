# DECISIONS AND ASSUMPTIONS

This file is a living record.

## Confirmed from the SIH problem statement

- Departments: Engineering, S&T, Traction Distribution.
- Maintenance information is associated with TMS, SMMS and TDMS.
- COA provides block/corridor operational context.
- Train timetable and goods-train forecast matter.
- Required output includes optimized block schedules.
- Weekly and monthly horizons are expected.
- Evaluation can include RMSE, inlier count etc. for the ISRO problem, but those metrics are NOT relevant to PS 26027.

## Prototype assumptions

These are NOT claims about official Railway schemas.

- exact task fields;
- exact severity values;
- exact resource types;
- exact compatibility rules;
- exact train delay penalties;
- exact asset availability formula;
- synthetic traffic-density score;
- synthetic block capacities.

Every such assumption should be labeled as a prototype modeling choice.

## Do not assume

- live access to Railway internal systems;
- exact BDMS API;
- exact TMS/SMMS/TDMS database schema;
- official priority weights;
- official safety rules beyond what is explicitly supplied.

## Architecture principle

Make assumptions replaceable.
