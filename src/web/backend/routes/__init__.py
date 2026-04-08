"""Routes package"""
from src.web.backend.routes.models import ModelsResource, ModelDetailResource, ModelUploadResource
from src.web.backend.routes.segment import SegmentResource, BatchSegmentResource, SegmentHistoryResource
from src.web.backend.routes.visualization import VisualizationResource, GPUMonitorResource
from src.web.backend.routes.auth import LoginResource
from src.web.backend.routes.augmentation import AugmentationPreviewResource

__all__ = [
    'ModelsResource', 'ModelDetailResource', 'ModelUploadResource',
    'SegmentResource', 'BatchSegmentResource', 'SegmentHistoryResource',
    'VisualizationResource', 'GPUMonitorResource',
    'LoginResource',
    'AugmentationPreviewResource'
]
