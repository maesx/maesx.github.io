## ADDED Requirements

### Requirement: Segmentation record stores fused image
The system SHALL store the fused image (original + mask overlay) in the segmentation_records table.

#### Scenario: Fused image is saved after segmentation
- **WHEN** a segmentation operation completes successfully
- **THEN** the fused_image field SHALL contain the Base64 encoded fused image

### Requirement: Segmentation record stores class-wise IoU scores
The system SHALL store per-class IoU scores in the segmentation_records table as JSON.

#### Scenario: Class IoU is saved after segmentation
- **WHEN** a segmentation operation completes successfully
- **THEN** the class_iou field SHALL contain a JSON array of IoU scores for each class

### Requirement: Segmentation record stores pixel distribution
The system SHALL store pixel distribution percentages in the segmentation_records table as JSON.

#### Scenario: Pixel distribution is saved after segmentation
- **WHEN** a segmentation operation completes successfully
- **THEN** the pixel_distribution field SHALL contain a JSON array of percentage values for each class

### Requirement: Segmentation record stores instance information
The system SHALL store instance segmentation information in the segmentation_records table as JSON.

#### Scenario: Instance info is saved for instance segmentation
- **WHEN** an instance segmentation operation completes successfully
- **THEN** the instance_info field SHALL contain JSON with instance count, bounding boxes, and class assignments

#### Scenario: Instance info is null for semantic segmentation
- **WHEN** a semantic segmentation operation completes
- **THEN** the instance_info field MAY be null or empty JSON