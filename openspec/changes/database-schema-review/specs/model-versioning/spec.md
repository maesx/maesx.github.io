## ADDED Requirements

### Requirement: Model can have multiple versions
The system SHALL support multiple versions of the same model coexisting in the database.

#### Scenario: Multiple versions of same model exist
- **WHEN** a model "unet_plusplus" has versions "1.0.0" and "1.1.0"
- **THEN** both versions SHALL exist in the models table with different version values

### Requirement: Model version has parent reference
The system SHALL track version inheritance via parent_model_id field.

#### Scenario: New version references parent
- **WHEN** creating version "1.1.0" from version "1.0.0"
- **THEN** parent_model_id SHALL reference the ID of version "1.0.0"

### Requirement: Model version has changelog
The system SHALL store version change descriptions in the changelog field.

#### Scenario: Changelog is saved with new version
- **WHEN** a new model version is created
- **THEN** the changelog field SHALL contain a description of changes from previous version

### Requirement: Latest version is marked
The system SHALL mark the latest version of each model with is_latest flag.

#### Scenario: Only one latest version per model
- **WHEN** a new version becomes the latest
- **THEN** is_latest SHALL be 1 for the new version
- **AND** is_latest SHALL be 0 for all previous versions of the same model

#### Scenario: Query returns latest version by default
- **WHEN** querying models without specifying version
- **THEN** the system SHALL return models where is_latest = 1