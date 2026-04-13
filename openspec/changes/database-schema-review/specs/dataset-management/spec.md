## ADDED Requirements

### Requirement: Dataset can be created with metadata
The system SHALL allow creating datasets with name, description, and type.

#### Scenario: Dataset is created successfully
- **WHEN** creating a dataset with name "training_set_v1"
- **THEN** a record SHALL be created in datasets table
- **AND** image_count and annotation_count SHALL be initialized to 0

### Requirement: Dataset tracks image count
The system SHALL maintain accurate image_count in the datasets table.

#### Scenario: Image count increments on upload
- **WHEN** an image is added to a dataset
- **THEN** the dataset's image_count SHALL increment by 1

#### Scenario: Image count decrements on deletion
- **WHEN** an image is removed from a dataset
- **THEN** the dataset's image_count SHALL decrement by 1

### Requirement: Dataset image stores annotation data
The system SHALL store annotation data as JSON in dataset_images table.

#### Scenario: Annotation is saved with image
- **WHEN** an image with annotations is uploaded
- **THEN** annotation_data field SHALL contain the annotation JSON
- **AND** annotation_status SHALL be "annotated"

### Requirement: Dataset image tracks annotation status
The system SHALL track whether each image is annotated.

#### Scenario: Unannotated image status
- **WHEN** an image is uploaded without annotations
- **THEN** annotation_status SHALL be "pending"

#### Scenario: Annotated image status
- **WHEN** annotations are added to a pending image
- **THEN** annotation_status SHALL change to "annotated"

### Requirement: Dataset tracks total size
The system SHALL maintain total_size in the datasets table.

#### Scenario: Total size updates on image upload
- **WHEN** an image is added to a dataset
- **THEN** total_size SHALL increase by the image's file_size