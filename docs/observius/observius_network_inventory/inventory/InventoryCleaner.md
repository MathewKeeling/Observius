#

## Overview

### Clean Inventory Methodology

```

Go through the database line by line. Row by row. 

If you find two columns where the column value (or column values) match. 
Consider the two rows.

Build a THIRD row

For each row and subsequent row considered:

    if one of the two rows has a '' or BLANK value:
        ignore that data.Where possible, 
    if one row has a value:
        please place that value in thew NEW (THIRD) row. 
    if one row has a value and the other row has a value too:
        take the value from the row that has the highest 'last_seen' value and place that in the NEW (THIRD) row.
    Delete the first and second (original) rows.

Repeat until you are out of rows.
```