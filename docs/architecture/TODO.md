# To Do

## Observius
- [ ] **02-22-2025**: 
- [ ] **02-22-2025**: Automate Creation of Devices..
    - [ ] Figure out how to tackle the device-type problem
    - [ ] Figure out how to tackle the hostname / device creation problem (start w/ unknown interfaces and unknown hosts?)
- [ ] **02-22-2025**: Implement auto import of standard libraries for Device-Types and Module-Types
- [ ] **02-22-2025**: Disable ETC yaml loading for collectors that are not enabled.
- [ ] **02-22-2025**: Implement a config manager.

## InventoryCleaner
- [ ] **02-22-2025**: Implement a data completeness validation method. Verify that all rows in source tables is at least partially represented in the master_inventory table.
- [ ] **02-22-2025**: Get to the bottom of why some of the rows are not completely represented. 
    - For example: notice how the MAC Address for 127.0.0.1 is not in the master_inventory.

## Database
- [ ] **02-22-2025**: Add a feature that makes it so that you only generate the tables whose collector feature is enabled.
- [ ] **02-22-2025**: Add another table for temporarily storing/evaluating/comparing before transferring to the master_inventory DB.
- [ ] **02-22-2025**: Store the ONI source information, and temporary inventory in the other database.